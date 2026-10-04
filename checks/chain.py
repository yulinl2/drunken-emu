#!/usr/bin/env python3
"""checks/chain.py -- the operation-chain format: load, validate, normalise.  Stdlib only, no browser.

A *chain* records a task as the steps a person actually took (docs/OPERATION-MODEL.md section 1), each step
with the properties that make its cost visible (section 2).  This module is the format.  It reads a JSON file
(YAML only if PyYAML happens to import; never required), checks it loudly, and fills every default, so the load
(checks/chain_load.py) and the verifiers (checks/chain_verifiers.py) always see one fixed shape.
Reference with tables and a worked example: docs/OPERATION-CHAINS.md.

The shortest valid file:

    {"provenance": {"source": "narrated", "date": "2026-10-03", "who": "me"},
     "steps": [{"op": "ANCHOR", "anchor": "edge", "target": "the menu button, top right"},
               "READ the first line"]}

Rules this file enforces (each one is a test in checks/test_chain.py):
  * a mistake is an error, never a silent default: unknown op, unknown key, bad enum value, a missing
    required key, a key on the wrong op.  Every problem names its step number, and ALL problems are reported
    in one pass (ChainError.problems), so a hand-written file is fixed in one round, not one error at a time;
  * FREE TEXT IS WALLED OFF.  `target`, `note` (and a chain's `task`, `setup`, `notes`, a provenance `who`,
    `note`) are for humans.  They live under a `text` key after normalisation and `blind()` removes them: the
    verifiers and the load only ever receive the blind chain, so no verifier CAN read them;
  * normalisation is idempotent: parse(dumps(parse(x))) == parse(x).

What this module cannot see: whether the chain is TRUE.  It checks shape and consistency of what the narrator
declared (an ANCHOR step with a reading-only anchor is a contradiction and is rejected), never whether the
person really found the button without reading.
"""
from __future__ import annotations

import copy
import datetime
import difflib
import json
import re
from pathlib import Path

FORMAT = "emu-chain/1"
DEFAULT_BUDGET = 3          # working-memory slots, OPERATION-MODEL section 3; "a few"

# --- vocabulary ------------------------------------------------------------------------------------------------
# The 15 primitives of OPERATION-MODEL section 1, plus TAP: section 4 writes it in both chains (the physical act
# on a target that an earlier step already chose).  TAP is not a primitive of the model: it carries no cost.
OPS = ("ANCHOR", "SCAN", "READ", "ENUMERATE", "DISCRIMINATE", "HOLD", "KEYIFY", "RELOAD", "NAVIGATE",
       "RE-ORIENT", "INFER", "WAIT", "REFRESH", "COMMIT", "VERIFY", "TAP")
OP_ALIASES = {"REORIENT": "RE-ORIENT", "RE_ORIENT": "RE-ORIENT"}
ANCHORS = ("edge", "fixed-position", "unique-visual", "text-keyword", "none")
POSITIONAL = ("edge", "fixed-position", "unique-visual")     # found without reading
READING_ONLY = ("text-keyword", "none")                       # found by reading, or not anchored at all
READINGS = ("none", "coarse", "fine")
FEEDBACKS = ("immediate", "delayed", "none")
REVERSIBILITIES = ("idempotent", "reversible", "irreversible")
LOSSES = ("position", "goal", "partial")                      # what an interruption can take away
VERIFY_AFTER = ("none", "consistency", "correctness")
VERIFY_KINDS = ("consistency", "correctness")
SOURCES = ("narrated", "designed", "captured")

# What a plain step costs when the narrator says nothing: (slots the step itself needs, reading).
# DISCRIMINATE's `need` is computed: the target plus its look-alikes.
OP_DEFAULTS = {
    "ANCHOR": (0, "none"), "SCAN": (1, "coarse"), "READ": (1, "fine"), "ENUMERATE": (1, "coarse"),
    "DISCRIMINATE": (None, "fine"), "HOLD": (1, "none"), "KEYIFY": (1, "none"), "RELOAD": (1, "none"),
    "NAVIGATE": (0, "none"), "RE-ORIENT": (1, "coarse"), "INFER": (1, "none"), "WAIT": (0, "none"),
    "REFRESH": (0, "none"), "COMMIT": (1, "none"), "VERIFY": (1, "coarse"), "TAP": (0, "none"),
}

COMMON_KEYS = {"n", "op", "target", "note", "text", "anchor", "confusables", "need", "held", "reading", "amount",
               "feedback", "reversibility", "interruption", "times", "intent", "view",
               "origin_stated", "exclusions_stated", "boundary_visible"}
OP_ONLY = {   # key -> the only ops it makes sense on
    "preview_before": {"COMMIT"}, "everything_on_screen": {"COMMIT"}, "verify_after": {"COMMIT"},
    "progress_visible": {"WAIT"}, "view_stable": {"WAIT"}, "partial_result_says_left": {"WAIT"},
    "restores": {"REFRESH", "RE-ORIENT", "NAVIGATE"},
    "set_visibly_complete": {"ENUMERATE"}, "pages": {"ENUMERATE"},
    "kind": {"VERIFY"}, "source": {"RELOAD"},
}
REQUIRED = {   # op -> keys with no default: the narrator must say
    "ANCHOR": ("anchor",), "DISCRIMINATE": ("confusables",), "RELOAD": ("source",), "REFRESH": ("restores",),
    "VERIFY": ("kind",), "WAIT": ("progress_visible", "view_stable"),
    "COMMIT": ("preview_before", "everything_on_screen", "verify_after", "reversibility"),
}
FREE_TEXT_STEP = ("target", "note")
FILE_KEYS = {"format", "provenance", "budget", "chains"}
CHAIN_KEYS = {"id", "task", "setup", "notes", "text", "provenance", "budget", "steps"}
PROV_KEYS = {"source", "date", "who", "note"}


class ChainError(ValueError):
    """The chain file is wrong.  `problems` lists every problem found, each naming its step number."""

    def __init__(self, problems: list[str], where: str = ""):
        self.problems = list(problems)
        self.where = where
        head = f"{where}: " if where else ""
        super().__init__(head + f"{len(self.problems)} problem(s)\n" + "\n".join(f"  - {p}" for p in self.problems))


# --- small type helpers (bool is an int in Python: reject it where a number is meant) ------------------------------
def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and v not in (float("inf"), float("-inf"))


def _hint(word, choices) -> str:
    m = difflib.get_close_matches(str(word), list(choices), n=1)
    return f" (did you mean {m[0]!r}?)" if m else ""


def _norm_op(op) -> str | None:
    if not isinstance(op, str):
        return None
    o = op.strip().upper()
    o = OP_ALIASES.get(o, o)
    return o if o in OPS else None


# --- one step ----------------------------------------------------------------------------------------------------
def _enum(s, key, allowed, default, P):
    v = s.get(key, default)
    if v not in allowed or not isinstance(v, str):
        P(f"`{key}` is {v!r}; allowed: {', '.join(allowed)}{_hint(v, allowed)}")
        return default
    return v


def _bool(s, key, P):
    if key not in s:
        return None
    v = s[key]
    if not isinstance(v, bool):
        P(f"`{key}` must be true or false, got {v!r}")
        return None
    return v


def _loss_list(s, key, P):
    v = s.get(key, [])
    if not isinstance(v, list) or any(x not in LOSSES for x in v) or len(set(map(str, v))) != len(v):
        P(f"`{key}` must be a list drawn from {list(LOSSES)} without repeats, got {v!r}")
        return []
    return list(v)


def _confusables(s, P):
    """[count, similarity] or {"count":..,"similarity":..}; count 0 = no look-alikes (similarity then ignored)."""
    if "confusables" not in s:
        return {"count": 0, "similarity": 0.0}
    v = s["confusables"]
    if isinstance(v, list) and len(v) == 2:
        c, sim = v
    elif isinstance(v, dict) and set(v) <= {"count", "similarity"} and "count" in v:
        c, sim = v["count"], v.get("similarity")
    else:
        P(f"`confusables` must be [count, similarity] or {{\"count\":..,\"similarity\":..}}, got {v!r}")
        return {"count": 0, "similarity": 0.0}
    if not _is_int(c) or c < 0:
        P(f"`confusables` count must be a whole number >= 0, got {c!r}")
        return {"count": 0, "similarity": 0.0}
    if c == 0:
        return {"count": 0, "similarity": 0.0}
    if not _is_num(sim) or not 0 <= sim <= 1:
        P(f"`confusables` with count {c} needs a similarity between 0 and 1 (how alike), got {sim!r}")
        return {"count": c, "similarity": 0.0}
    return {"count": c, "similarity": float(sim)}


def _step(raw, n: int, prev_held: list[str], problems: list[str]):
    """-> normalised step dict, or None when the step is hopeless (unknown op).  Problems go to `problems`."""
    pre = f"step {n}"

    def P(msg):
        problems.append(f"{pre}: {msg}")

    if isinstance(raw, str):                       # shorthand: "OP free text"
        parts = raw.strip().split(None, 1)
        raw = {"op": parts[0] if parts else "", "target": parts[1] if len(parts) > 1 else ""}
    if not isinstance(raw, dict):
        P(f"must be an object or an 'OP free text' string, got {type(raw).__name__}")
        return None
    op = _norm_op(raw.get("op"))
    if op is None:
        P(f"unknown op {raw.get('op')!r}{_hint(str(raw.get('op')).upper(), OPS)}; known ops: {', '.join(OPS)}")
        return None
    pre = f"step {n} ({op})"
    s = dict(raw)

    allowed = COMMON_KEYS | {k for k, ops in OP_ONLY.items() if op in ops}
    for k in s:
        if k in allowed:
            continue
        if k in OP_ONLY:
            P(f"key `{k}` only applies to {'/'.join(sorted(OP_ONLY[k]))}, not to {op}")
        else:
            P(f"unknown key `{k}`{_hint(k, sorted(COMMON_KEYS | set(OP_ONLY)))}")
    for k in REQUIRED.get(op, ()):
        if k not in s:
            P(f"missing required key `{k}` (no default: say what you saw)")
    if "n" in s and s["n"] != n:
        P(f"`n` is {s['n']!r} but this is step {n}")

    out: dict = {"n": n, "op": op}
    # anchor: how the target was found
    out["anchor"] = _enum(s, "anchor", ANCHORS, "none", P)
    if op == "ANCHOR" and "anchor" in s and out["anchor"] in READING_ONLY:
        P(f"an ANCHOR step is found without reading: `anchor` must be one of {', '.join(POSITIONAL)} "
          f"(got {out['anchor']!r}); if it was found by reading, make it a SCAN")
    out["confusables"] = _confusables(s, P)
    if op == "DISCRIMINATE" and "confusables" in s and out["confusables"]["count"] < 1:
        P("DISCRIMINATE needs at least one look-alike: `confusables` [count >= 1, similarity]")

    # memory: slots the step needs now, items held across it (inherited until changed)
    need_default, reading_default = OP_DEFAULTS[op]
    if need_default is None:
        need_default = out["confusables"]["count"] + 1
    need = s.get("need", need_default)
    if not _is_int(need) or need < 0:
        P(f"`need` must be a whole number >= 0, got {need!r}")
        need = need_default
    out["need"] = need
    if "held" in s:
        held = s["held"]
        if (not isinstance(held, list) or any(not isinstance(x, str) or not x.strip() for x in held)
                or len(set(held)) != len(held)):
            P(f"`held` must be a list of distinct non-empty labels (one per slot), got {held!r}")
            held = list(prev_held)
    else:
        held = list(prev_held)
    if op in ("HOLD", "KEYIFY", "RELOAD") and held == prev_held:
        P(f"{op} must change what is held: give `held` as the list after this step (it is {prev_held!r} before)")
    out["held"] = held

    # reading
    out["reading"] = _enum(s, "reading", READINGS, reading_default, P)
    amount = s.get("amount", 0 if out["reading"] == "none" else 1)
    if not _is_num(amount) or amount < 0:
        P(f"`amount` must be a number >= 0 (items read), got {amount!r}")
        amount = 1
    if out["reading"] == "none" and amount > 0:
        P(f"`amount` is {amount!r} but `reading` is none: say `coarse` or `fine`")
    out["amount"] = float(amount)
    out["feedback"] = _enum(s, "feedback", FEEDBACKS, "immediate", P)
    out["reversibility"] = _enum(s, "reversibility", REVERSIBILITIES, "idempotent", P)
    out["interruption"] = _loss_list(s, "interruption", P)
    times = s.get("times", 1)
    if not _is_int(times) or times < 1:
        P(f"`times` must be a whole number >= 1, got {times!r}")
        times = 1
    out["times"] = times

    # intent / view: opaque keys, compared for equality only
    for k in ("intent", "view"):
        v = s.get(k)
        if v is not None and (not isinstance(v, str) or not v.strip()):
            P(f"`{k}` must be a short non-empty key, got {v!r}")
            v = None
        out[k] = v
    if out["intent"] and not out["view"]:
        P("`intent` needs `view` too: two views serving one intent is what the single-path check compares")

    # op-specific
    if op == "COMMIT":
        out["preview_before"] = bool(_bool(s, "preview_before", P))
        out["everything_on_screen"] = bool(_bool(s, "everything_on_screen", P))
        out["verify_after"] = _enum(s, "verify_after", VERIFY_AFTER, "none", P)
    if op == "WAIT":
        out["progress_visible"] = bool(_bool(s, "progress_visible", P))
        out["view_stable"] = bool(_bool(s, "view_stable", P))
        v = _bool(s, "partial_result_says_left", P)
        if v is not None:                          # absent = this wait yields no partial result
            out["partial_result_says_left"] = v
    if "restores" in s and op in OP_ONLY["restores"]:
        out["restores"] = _loss_list(s, "restores", P)
    if op == "ENUMERATE":
        out["set_visibly_complete"] = bool(_bool(s, "set_visibly_complete", P))
        pages = s.get("pages", 1)
        if not _is_int(pages) or pages < 1:
            P(f"`pages` must be a whole number >= 1, got {pages!r}")
            pages = 1
        out["pages"] = pages
    if op == "VERIFY":
        out["kind"] = _enum(s, "kind", VERIFY_KINDS, "consistency", P)
    if op == "RELOAD":
        src = s.get("source")
        if not isinstance(src, str) or not src.strip():
            P("`source` must name where the lost goal is fetched from (e.g. \"chat\", \"notes\", \"task text\")")
            src = "?"
        out["source"] = src
    # list-showing (both or neither) and block-structured text
    o, e = _bool(s, "origin_stated", P), _bool(s, "exclusions_stated", P)
    if (("origin_stated" in s) != ("exclusions_stated" in s)):
        P("a step that shows a list or prompt needs BOTH `origin_stated` and `exclusions_stated`")
    elif o is not None and e is not None:
        out["origin_stated"], out["exclusions_stated"] = o, e
    b = _bool(s, "boundary_visible", P)
    if b is not None:
        out["boundary_visible"] = b

    text = dict(s["text"]) if isinstance(s.get("text"), dict) else {}
    for k in FREE_TEXT_STEP:
        if k in s:
            text[k] = s[k] if isinstance(s[k], str) else str(s[k])
    out["text"] = {"target": text.get("target", ""), "note": text.get("note", "")}
    return out


# --- provenance, chains, files -------------------------------------------------------------------------------------
def _provenance(file_prov, chain_prov, where, problems):
    merged: dict = {}
    for p in (file_prov, chain_prov):
        if p is None:
            continue
        if not isinstance(p, dict):
            problems.append(f"{where}: `provenance` must be an object with source, date, who")
            continue
        p = dict(p)
        t = p.pop("text", None)                        # the normalised form keeps who/note under `text`
        if isinstance(t, dict):
            for k in ("who", "note"):
                if k in t:
                    p.setdefault(k, t[k])
        for k in p:
            if k not in PROV_KEYS:
                problems.append(f"{where}: unknown provenance key `{k}`{_hint(k, PROV_KEYS)}")
        merged.update({k: v for k, v in p.items() if k in PROV_KEYS})
    if merged.get("source") not in SOURCES:
        problems.append(f"{where}: provenance `source` must be one of {', '.join(SOURCES)}, got {merged.get('source')!r}")
    d = merged.get("date")
    ok = isinstance(d, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) is not None
    if ok:
        try:
            datetime.date(int(d[:4]), int(d[5:7]), int(d[8:]))
        except ValueError:
            ok = False
    if not ok:
        problems.append(f"{where}: provenance `date` must be a real date YYYY-MM-DD, got {d!r}")
    if not isinstance(merged.get("who"), str) or not merged["who"].strip():
        problems.append(f"{where}: provenance `who` must say who recorded it (a role is enough; no personal data)")
    return merged


def _budget(v, where, problems):
    if v is None:
        return None
    if not _is_int(v) or v < 1:
        problems.append(f"{where}: `budget` must be a whole number >= 1 (working-memory slots), got {v!r}")
        return None
    return v


def _chain(raw, idx: int, file_prov, file_budget, multi: bool, problems):
    where = f"chain #{idx + 1}"
    if not isinstance(raw, dict):
        problems.append(f"{where}: must be an object")
        return None
    cid = raw.get("id")
    if cid is None:
        if multi:
            problems.append(f"{where}: several chains in one file need an `id` each")
        cid = f"chain-{idx + 1}"
    elif not isinstance(cid, str) or not cid.strip():
        problems.append(f"{where}: `id` must be a non-empty string")
        cid = f"chain-{idx + 1}"
    where = f"chain {cid!r}"
    for k in raw:
        if k not in CHAIN_KEYS:
            problems.append(f"{where}: unknown key `{k}`{_hint(k, CHAIN_KEYS)}")
    steps_raw = raw.get("steps")
    if not isinstance(steps_raw, list) or not steps_raw:
        problems.append(f"{where}: `steps` must be a non-empty list")
        steps_raw = []
    prov = _provenance(file_prov, raw.get("provenance"), where, problems)
    budget = _budget(raw.get("budget"), where, problems)
    steps, held = [], []
    sub: list[str] = []
    for i, r in enumerate(steps_raw):
        st = _step(r, i + 1, held, sub)
        if st is None:
            held_next = held
        else:
            steps.append(st)
            held_next = st["held"]
        held = held_next
    problems.extend(f"{where}, {p}" for p in sub)
    text_src = raw["text"] if isinstance(raw.get("text"), dict) else {}
    text = {k: str(raw.get(k, text_src.get(k, ""))) for k in ("task", "setup", "notes")}
    prov_text = {"who": prov.pop("who", ""), "note": prov.pop("note", "")}
    prov["text"] = prov_text
    return {"id": cid, "provenance": prov, "budget": budget if budget is not None else file_budget,
            "steps": steps, "text": text}


def parse(obj, where: str = "<chain>") -> dict:
    """Validate and normalise a decoded document.  -> {"format", "chains": [chain, ...]}.  Raises ChainError."""
    problems: list[str] = []
    if not isinstance(obj, dict):
        raise ChainError(["the file must be a JSON object with `steps` (one chain) or `chains` (several)"], where)
    fmt = obj.get("format", FORMAT)
    if fmt != FORMAT:
        problems.append(f"unknown `format` {fmt!r}; this reader knows {FORMAT!r}")
    if "chains" in obj:
        if "steps" in obj:
            problems.append("give either `chains` (several) or `steps` (one chain), not both")
        for k in obj:
            if k not in FILE_KEYS:
                problems.append(f"unknown key `{k}` next to `chains`{_hint(k, FILE_KEYS)}")
        raw_chains = obj["chains"] if isinstance(obj["chains"], list) and obj["chains"] else None
        if raw_chains is None:
            problems.append("`chains` must be a non-empty list")
            raw_chains = []
        file_prov, file_budget = obj.get("provenance"), _budget(obj.get("budget"), "file", problems)
    else:
        raw_chains, file_prov, file_budget = [{k: v for k, v in obj.items() if k != "format"}], None, None
    chains = []
    for i, rc in enumerate(raw_chains):
        c = _chain(rc, i, file_prov, file_budget, len(raw_chains) > 1, problems)
        if c is not None:
            chains.append(c)
    ids = [c["id"] for c in chains]
    for cid in sorted({x for x in ids if ids.count(x) > 1}):
        problems.append(f"chain id {cid!r} is used more than once")
    if problems:
        raise ChainError(problems, where)
    return {"format": FORMAT, "chains": chains}


def _no_duplicate_keys(pairs):
    seen: dict = {}
    for k, v in pairs:
        if k in seen:
            raise ValueError(f"duplicate key {k!r} in one object (JSON would silently keep the last); "
                             f"sibling keys: {sorted(seen)}")
        seen[k] = v
    return seen


def _no_constants(name):
    raise ValueError(f"{name} is not valid JSON")


def load_text(text: str, fmt: str = "json", where: str = "<text>") -> dict:
    if fmt == "json":
        try:
            obj = json.loads(text, object_pairs_hook=_no_duplicate_keys, parse_constant=_no_constants)
        except json.JSONDecodeError as e:
            raise ChainError([f"not valid JSON: {e.msg} at line {e.lineno} column {e.colno}"], where) from None
        except ValueError as e:
            raise ChainError([str(e)], where) from None
    else:
        try:
            import yaml                                    # optional: never a dependency of this layer
        except ImportError:
            raise ChainError(["YAML needs PyYAML, which is not installed; JSON is the canonical format"], where) from None
        try:
            obj = yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise ChainError([f"not valid YAML: {e}"], where) from None
    return parse(obj, where)


def load(path) -> dict:
    """Read, validate and normalise a chain file (.json; .yaml/.yml only when PyYAML imports)."""
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as e:
        raise ChainError([f"cannot read the file: {e.strerror or e}"], str(p)) from None
    return load_text(text, "yaml" if p.suffix.lower() in (".yaml", ".yml") else "json", str(p))


def dumps(doc: dict) -> str:
    """Canonical JSON of a normalised document; parse() accepts it again unchanged."""
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


# --- the blind view -----------------------------------------------------------------------------------------------
class _Trap(dict):
    """Stands where free text lives, in tests only: any read means a verifier looked at what it must not."""

    def _boom(self, *a, **k):
        raise AssertionError("a verifier read free text (target/note): verifiers must be content-blind")

    __getitem__ = get = __iter__ = __len__ = __contains__ = items = keys = values = __bool__ = _boom

    def __repr__(self):
        return "<free-text trap>"


def blind(chain: dict, trap: bool = False) -> dict:
    """A deep copy of one chain with every free-text field removed (or, with trap=True, replaced by a tripwire).

    Verifiers and the load receive only this.  What stays: enums, numbers, booleans, and three kinds of opaque
    label compared by equality or counted, never interpreted: `intent`/`view` keys, `held` labels, RELOAD `source`.
    """
    c = copy.deepcopy(chain)
    for holder in [c] + c["steps"] + [c["provenance"]]:
        if "text" in holder:
            del holder["text"]
            if trap:
                holder["text"] = _Trap()
    return c


def resolve_budget(chain: dict, override: int | None = None) -> int:
    """Precedence: an explicit override (the CLI's --budget), then the chain's own budget, then DEFAULT_BUDGET."""
    if override is not None:
        return override
    return chain.get("budget") or DEFAULT_BUDGET
