"""Root-chain gate: every wait on the principal, and every question to the principal, carries its chain from a root value.

INVARIANT: a wait passes only with a chain of verbatim quotes that equals its tree path, whose root link is the principal's own words and states the value; a debt is paid only by the principal's own words (closed_by), never by a status change alone.
FAILS WHEN: a status changes and the debt list does not; a question is cited as an assertion; a missing or unreadable tree, bank file or debt file passes instead of failing.

A "wait" is a node whose status starts with "wait". Its `chain` lists EVERY node on its tree path, root first, the node itself
last (no skipped links, no cherry-picking). Each link is
    {"node": id, "quote": verbatim text, "source": where, "fit": "states"|"supports"|"related", "why": one sentence}
source forms: a bank id: the key of a record in the bank that `record bank` writes, or, where a project also cuts its bank
              into clauses, the id of a record of principal-clauses, principal-dialog-answers, principal-questions or
              principal-comments in the clause bank directory (a "#aN" suffix is allowed),
              "OW:<line>" (line N of the files that the config key `words` matches, read in sorted order),
              or "path:<file under the project root>".

What the gate checks (it checks that the work is done, recorded and verifiable; whether a quote FITS its claim stays the
reader's judgement, which is why `render` prints the chain for the principal to read):
  1. the chain's nodes equal the node's tree path, in order
  2. every quote is verbatim in its source (a dialog quote must start an ANSWER segment, not the assistant's question)
  3. the root link is the principal's own words, and states the value (fit "states")
  4. every non-root link says why it follows from the one above it
  5. a quoted document line is not followed within 8 lines by "Superseded"
  6. the node has a REPRODUCED evidence entry, and `artifacts` (files the claim is about) are not newer than
     `reproduced_at`; or `reproduction_na` says why no artifact exists (the exemption is counted and shown)

usage, from a project (the configuration names the tree, the debt list, the bank and the words files):
  python3 -I bin/loop gate check        one JSON line; writes the state file chain-gate.json; exit 0 when no wait fails outside the debt
  python3 -I bin/loop gate render ID    the chain as text, for a status line or a question to the principal
  python3 -I bin/loop gate baseline     record the CURRENT failing waits as dated debt (explicit; listed; paid down, never hidden)
  python3 -I bin/loop gate selftest     synthetic cases in a temporary project; each must come out as expected
"""
import argparse
import datetime
import glob
import json
import os
import pathlib
import re
import sys
import tempfile

from loop import config

BANK_FILES = ("principal-clauses", "principal-dialog-answers", "principal-questions", "principal-comments")
KIND_OF_FILE = {"principal-clauses": "principal-clause", "principal-comments": "principal-comment", "bank": "principal-words"}
PRINCIPAL_KINDS = ("principal-clause", "principal-answer", "principal-words", "principal-comment")
SPEECH = ("assert", "deny", "ask", "instruct", "approve")
SUPERSEDED_WINDOW = 8   # lines after a quoted line in which "Superseded" is looked for
KEY_CHARS = 60          # the first characters of a quote: how a quote is located in a document
MIN_REASON = 12         # the least length of a 'why' or a 'reading'
MTIME_SLACK_S = 60      # an artifact may be this many seconds newer than reproduced_at
MALFORMED = (AttributeError, KeyError, OSError, TypeError, ValueError)


def N(s):
    """Whitespace collapsed and curly apostrophes made straight: the form in which quotes are compared."""
    return " ".join(str(s).replace(chr(0x2019), "'").split())


def _rel(p, root):
    """A path as the configuration writes it: relative to the project root when it lies under it."""
    try:
        return str(pathlib.Path(p).relative_to(root))
    except ValueError:
        return str(p)


def _write_bank(bank_dir, records, names=BANK_FILES):
    """One JSON line per record in each named bank file; a file without records is written empty."""
    bank_dir.mkdir(parents=True, exist_ok=True)
    for f in names:
        text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records.get(f, []))
        (bank_dir / (f + ".jsonl")).write_text(text, encoding="utf-8")


def ctx_load(bank_dir, words, root, bank_file=None):
    """The principal's bank and the lines of the words files, with what is wrong with them: `bad` counts bank lines that are
    not a JSON object (skipped and counted); `missing` names the bank files that are absent or unreadable. check fails on either."""
    bank, bad, missing = {}, 0, []
    bank_dir = pathlib.Path(bank_dir)
    # Two stores. The bank that `record bank` writes (bank_file): required when it is the only store. The four clause files:
    # required as soon as their directory exists (a project that cuts its bank into clauses keeps all four), or when no
    # bank file is given. With neither, the bank file is named as missing.
    stores = [(f, bank_dir / (f + ".jsonl")) for f in BANK_FILES] if bank_file is None or bank_dir.is_dir() else []
    if bank_file is not None and (pathlib.Path(bank_file).exists() or not stores):
        stores.append(("bank", pathlib.Path(bank_file)))
    for f, p in stores:
        try:
            lines = p.read_text(encoding="utf-8").split("\n")
        except (OSError, ValueError):
            missing.append(p.name)
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
                kind = "principal-dialog-answers" if f == "bank" and r.get("kind") == "dialog" else f
                bank[r.get("id") or r.get("key")] = (kind, r.get("time") or r.get("timestamp") or "", N(r.get("text", "")))
            except (AttributeError, TypeError, ValueError):
                bad += 1
    pats = [words] if isinstance(words, str) else list(words)
    found = {m for pat in pats for m in glob.glob(os.path.join(str(root), pat), recursive=True) if os.path.isfile(m)}
    ow = []
    for m in sorted(found):
        try:
            ow.extend(pathlib.Path(m).read_text(encoding="utf-8", errors="replace").split("\n"))
        except OSError:
            continue
    return {"bank": bank, "ow": ow, "bad": bad, "missing": missing, "root": pathlib.Path(root)}


def _ow_index(src):
    """The 1-based line of an OW:<line> source, or None. Line 0 and below are refused: a negative index would read from the end."""
    try:
        n = int(src[3:])
    except ValueError:
        return None
    return n if n >= 1 else None


def _ow_line(src, ctx):
    """The normalized text of the words line that an OW:<line> source names, or None."""
    n = _ow_index(src)
    return N(ctx["ow"][n - 1]) if n is not None and n <= len(ctx["ow"]) else None


def find_file(rel, root):
    """A path link: an absolute path as it is, a relative one under the project root. None when there is no such file."""
    p = pathlib.Path(rel)
    p = p if p.is_absolute() else pathlib.Path(root) / p
    return p if p.is_file() else None


def verify(src, quote, ctx):
    """-> dict(ok, reason, kind, when, near) for one link's quote."""
    q = N(quote)
    bad = lambda why, kind="", when="": {"ok": False, "reason": why, "kind": kind, "when": when, "near": None}
    if not q:
        return bad("empty quote")
    if src.startswith("OW:"):
        n, line = _ow_index(src), _ow_line(src, ctx)
        if line is None:
            return bad(f"bad words id {src}")
        if q not in line:
            return bad(f"quote not in words line {n}", "principal-words", f"line {n}")
        return {"ok": True, "reason": "", "kind": "principal-words", "when": f"words line {n}", "near": None}
    base = src.split("#")[0]
    if base in ctx["bank"]:
        f, tm, text = ctx["bank"][base]
        if f == "principal-dialog-answers":
            if ('="' + q) not in text:
                return bad(f"quote does not start an answer segment of dialog {base}", "principal-answer", tm)
            return {"ok": True, "reason": "", "kind": "principal-answer", "when": tm, "near": None}
        if q not in text:
            return bad(f"quote not in bank record {base}", "principal-clause", tm)
        return {"ok": True, "reason": "", "kind": KIND_OF_FILE.get(f, "principal-question"), "when": tm, "near": None}
    if src.startswith("path:"):
        p = find_file(src[5:], ctx["root"])
        if p is None:
            return bad(f"file not found: {src[5:]}")
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        if q not in N(" ".join(lines)):
            return bad(f"quote not in {src[5:]}", "doc", src[5:])
        near = None
        key = q[:KEY_CHARS]
        for i, l in enumerate(lines):
            if key in N(l):
                if re.search(r"(?i)superseded", " ".join(lines[i:i + 1 + SUPERSEDED_WINDOW])):
                    near = i + 1
                break
        return {"ok": True, "reason": "", "kind": "doc", "when": src[5:], "near": near}
    return bad(f"unknown source form: {src!r}")


def followed_text(src, quote, ctx):
    """The 3 characters after the quote in its source record (a quote cut from a question has no question mark of its own)."""
    q = N(quote)
    if src.startswith("OW:"):
        text = _ow_line(src, ctx) or ""
    else:
        base = src.split("#")[0]
        text = ctx["bank"][base][2] if base in ctx["bank"] else ""
    i = text.find(q)
    return text[i + len(q): i + len(q) + 3] if i >= 0 else ""


def speech_problem(quote, act, followed):
    """The label must fit the quote's form. A question (the quote ends in a question mark, or one follows it in its source)
    is never an assertion or an approval; it is a deny, an ask or an instruct, and the reading says which."""
    if act not in SPEECH:
        return f"speech_act must be one of {SPEECH}, not {act!r}"
    is_q = bool(re.search("[?" + chr(0xFF1F) + r"]\W*$", N(quote))) or "?" in followed or chr(0xFF1F) in followed
    if is_q and act in ("assert", "approve"):
        return "the quote is a question: it is a deny, an ask or an instruct (the reading says which), not an assert or an approve"
    return ""


def tree_paths(tree):
    nodes, path = {}, {}

    def walk(n, p):
        nodes[n["id"]] = n
        path[n["id"]] = p + [n["id"]]
        for c in n.get("children") or []:
            walk(c, p + [n["id"]])

    for r in tree["roots"]:
        walk(r, [])
    return nodes, path


def parse_iso(s):
    return datetime.datetime.fromisoformat(s).timestamp()


def check_node(n, path, ctx):
    """-> list of failure strings (empty = the chain passes)."""
    fails = []
    ch = n.get("chain")
    if not ch:
        return ["no chain"]
    ids = [l.get("node") for l in ch]
    if ids != path:
        fails.append(f"chain nodes {ids} are not the tree path {path}")
    for i, l in enumerate(ch):
        v = verify(l.get("source", ""), l.get("quote", ""), ctx)
        tag = l.get("node")
        if not v["ok"]:
            fails.append(f"{tag}: {v['reason']}")
        elif v["near"] and not N(l.get("superseded_ok", "")):
            fails.append(f"{tag}: the quoted line ({l.get('source')} line {v['near']}) is followed within {SUPERSEDED_WINDOW} lines by "
                         f"'Superseded'; cite the later text, or set superseded_ok with the reason")
        if v["ok"] and v["kind"] in PRINCIPAL_KINDS:
            sp = speech_problem(l.get("quote", ""), l.get("speech_act", ""), followed_text(l.get("source", ""), l.get("quote", ""), ctx))
            if sp:
                fails.append(f"{tag}: {sp}")
        if i == 0:
            if l.get("fit") != "states":
                fails.append(f"root {tag}: no verified principal clause states the value (fit={l.get('fit')})")
            if v["ok"] and v["kind"] not in PRINCIPAL_KINDS:
                fails.append(f"root {tag}: the root link must be the principal's own words, not a {v['kind']}")
        elif len(N(l.get("why", ""))) < MIN_REASON:
            fails.append(f"{tag}: no 'why' (how this follows from the link above)")
    ev = n.get("evidence")
    repro = isinstance(ev, list) and any(isinstance(e, list) and e and e[0] == "REPRODUCED" for e in ev)
    if not N(n.get("reproduction_na", "")):
        if not repro:
            fails.append("no REPRODUCED evidence entry (reported evidence alone is not a re-derivation)")
        arts, ra = n.get("artifacts") or [], n.get("reproduced_at")
        if not arts or not ra:
            fails.append("no artifacts/reproduced_at: cannot show the reproduction is current")
        else:
            try:
                t0 = parse_iso(ra)
            except (TypeError, ValueError):
                fails.append(f"reproduced_at is not an ISO time: {ra!r}")
                arts = []
            for a in arts:
                p = pathlib.Path(a)
                p = p if p.is_absolute() else pathlib.Path(ctx["root"]) / p
                if not p.exists():
                    fails.append(f"artifact missing: {a}")
                elif p.stat().st_mtime > t0 + MTIME_SLACK_S:
                    fails.append(f"artifact changed after the reproduction: {a}")
    return fails


def _node_fails(n, path, ctx):
    """check_node, with a node that cannot be checked reported as a failure rather than raised."""
    try:
        return check_node(n, path, ctx)
    except MALFORMED as e:
        return [f"not checkable: {type(e).__name__}: {e}"]


def check_closure(cb, ctx):
    """'' when a node's closed_by holds: the principal's verbatim words, a speech act that fits their form, and a labelled reading."""
    if not cb:
        return "left the wait state without closed_by (the principal's words)"
    v = verify(cb.get("source", ""), cb.get("quote", ""), ctx)
    if not v["ok"]:
        return f"closed_by: {v['reason']}"
    if v["kind"] not in PRINCIPAL_KINDS:
        return "closed_by must be the principal's own words, not a document"
    sp = speech_problem(cb.get("quote", ""), cb.get("speech_act", ""), followed_text(cb.get("source", ""), cb.get("quote", ""), ctx))
    if sp:
        return f"closed_by: {sp}"
    if len(N(cb.get("reading", ""))) < MIN_REASON:
        return "closed_by: no 'reading' (what the quote is taken to mean, labelled as the assistant's reading)"
    return ""


def _closure_fails(cb, ctx):
    try:
        return check_closure(cb, ctx)
    except MALFORMED as e:
        return f"closed_by is not checkable: {type(e).__name__}: {e}"


def waits_of(nodes):
    return {i: n for i, n in nodes.items() if str(n.get("status", "")).startswith("wait")}


def load_tree(cfg):
    """-> (nodes, paths, None); or (None, None, detail) when the tree is missing or unreadable."""
    t = cfg.path("tree")
    if not t.is_file():
        return None, None, f"no tree at {_rel(t, cfg.root)}"
    try:
        nodes, paths = tree_paths(json.loads(t.read_text(encoding="utf-8")))
    except MALFORMED:
        return None, None, f"tree at {_rel(t, cfg.root)} is not readable"
    return nodes, paths, None


def load_debt(cfg):
    """-> (ids of the debt, None); or (empty, detail) when the debt file exists and cannot be read, which is a failure."""
    d = cfg.path("chain_debt")
    if not d.exists():
        return set(), None
    try:
        return set(json.loads(d.read_text(encoding="utf-8"))["waits"]), None
    except MALFORMED:
        return set(), f"debt file {_rel(d, cfg.root)} is not readable"


def run_check(cfg, nodes, paths):
    """-> (summary, results per wait); writes the state file chain-gate.json. A missing or unreadable input is named in the
    summary and fails it. A debt is paid only by the principal's own words (closed_by) or by passing its chain."""
    ctx = ctx_load(cfg.path("clause_bank_dir"), cfg["words"], cfg.root, cfg.path("bank"))
    debt, debt_err = load_debt(cfg)
    res = {}
    for i, n in waits_of(nodes).items():
        res[i] = {"status": n.get("status"), "title": str(n.get("title", ""))[:100], "fails": _node_fails(n, paths[i], ctx),
                  "exempt": bool(N(n.get("reproduction_na", "")))}
    failing = {i for i, r in res.items() if r["fails"]}
    new_fail = sorted(failing - debt, key=str)
    # A debt node that stopped waiting is paid ONLY if it carries the principal's own verbatim words as `closed_by`;
    # changing a status alone does not pay debt.
    closed, closure_fail = [], {}
    for i in sorted(debt - set(res), key=str):
        n = nodes.get(i)
        cb = (n or {}).get("closed_by") or {}
        if n is None:
            closure_fail[i] = ["node no longer in the tree"]
        elif not cb:
            closure_fail[i] = ["left the wait state without closed_by (the principal's words)"]
        else:
            msg = _closure_fails(cb, ctx)
            if msg:
                closure_fail[i] = [msg]
            else:
                closed.append(i)
    paid = sorted(set(closed) | {i for i in debt & set(res) if not res[i]["fails"]}, key=str)
    out = {"ok": not new_fail and not closure_fail and not ctx["bad"] and not ctx["missing"] and debt_err is None,
           "bank_bad_lines": ctx["bad"], "bank_missing": ctx["missing"], "debt_unreadable": debt_err,
           "waits": len(res), "pass": len(res) - len(failing),
           "fail": len(failing), "debt_open": sorted(failing & debt, key=str), "debt_paid": paid,
           "closed_by_principal_words": closed, "closure_fail": closure_fail,
           "new_fail": new_fail, "exempt": sorted((i for i, r in res.items() if r["exempt"]), key=str)}
    cfg.state("chain-gate.json").write_text(json.dumps({"summary": out, "waits": res}, ensure_ascii=False, indent=1), encoding="utf-8")
    return out, res


def check(cfg):
    nodes, paths, err = load_tree(cfg)
    if err:
        print(json.dumps({"ok": False, "detail": err}, ensure_ascii=False))
        return 1
    out, _ = run_check(cfg, nodes, paths)
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out["ok"] else 1


def render(cfg, i):
    nodes, paths, err = load_tree(cfg)
    if err:
        print(json.dumps({"ok": False, "detail": err}, ensure_ascii=False))
        return 1
    if i not in nodes:
        print(f"no node {i}")
        return 2
    n, ctx = nodes[i], ctx_load(cfg.path("clause_bank_dir"), cfg["words"], cfg.root, cfg.path("bank"))
    f = _node_fails(n, paths[i], ctx)
    print(f"{i} [{n.get('status')}, {n.get('who')}] {n.get('title')}")
    print("gate: " + ("PASS" if not f else "FAIL: " + "; ".join(f)))
    try:
        for l in n.get("chain") or []:
            v = verify(l.get("source", ""), l.get("quote", ""), ctx)
            print(f"  {l.get('node')} ({l.get('fit')}; {l.get('speech_act') or 'NO SPEECH ACT'}; {v['kind'] or '?'} {v['when']}; {'verbatim' if v['ok'] else 'NOT VERIFIED'})")
            print(f"      \"{l.get('quote')}\"")
            if l.get("why"):
                print(f"      why: {l['why']}")
        cb = n.get("closed_by")
        if cb:
            print(f"closed by the principal's words ({cb.get('speech_act') or 'NO SPEECH ACT'}): \"{cb.get('quote')}\"\n      reading (the assistant's): {cb.get('reading') or 'NONE'}")
        if n.get("reproduced_at"):
            print(f"reproduced at {n['reproduced_at']} against: {', '.join(n.get('artifacts') or [])}")
        if n.get("reproduction_na"):
            print(f"reproduction exempt: {n['reproduction_na']}")
        if n.get("default"):
            print(f"default: {n['default']}")
    except MALFORMED as e:
        print(f"not printable: {type(e).__name__}: {e}")
    return 0


def baseline(cfg):
    nodes, paths, err = load_tree(cfg)
    if err:
        print(json.dumps({"ok": False, "detail": err}, ensure_ascii=False))
        return 1
    out, res = run_check(cfg, nodes, paths)
    if out["bank_missing"] or out["bank_bad_lines"]:
        print(json.dumps({"ok": False, "detail": "baseline refused: a bank input is missing or malformed, so its failures would be recorded as debt",
                          "bank_missing": out["bank_missing"], "bank_bad_lines": out["bank_bad_lines"]}, ensure_ascii=False))
        return 1
    failing = sorted((i for i, r in res.items() if r["fails"]), key=str)
    debt = cfg.path("chain_debt")
    debt.parent.mkdir(parents=True, exist_ok=True)
    if debt.is_file():
        # an overwrite leaves a dated copy of what it replaces: the stores are append-only, never rewritten
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")
        try:
            cfg.state(f"chain-debt-{stamp}.json").write_bytes(debt.read_bytes())
        except OSError as e:
            print(json.dumps({"ok": False, "detail": f"baseline refused: the old debt file cannot be copied ({e})"}, ensure_ascii=False))
            return 1
    debt.write_text(json.dumps({
        "set_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M+00:00"),
        "note": "Waits that had no verified root chain when the gate was introduced. Each is owed a chain; the list only "
                "shrinks. A wait that is not on this list and fails the gate fails the loop's chain check.",
        "waits": failing}, indent=1), encoding="utf-8")
    print(json.dumps({"debt_recorded": failing}, ensure_ascii=False))
    return 0


def _cases(d):
    """The synthetic cases, built in the temporary project d: one line per case; returns how many came out wrong."""
    now = datetime.datetime.now(datetime.timezone.utc)
    clause = "Ship the small version first and widen it once it works"
    bank = d / "bank"
    _write_bank(bank, {
        "principal-clauses": [{"id": "clause-1", "time": "2026-01-01T00:01:00Z", "text": clause}],
        "principal-dialog-answers": [
            {"id": "dialog-1", "time": "2026-01-01T00:02:00Z", "text": 'Which path? ="Publish the small version first, then tune it later"'},
            {"id": "dialog-2", "time": "2026-01-01T00:03:00Z", "text": 'Who asked? ="Who asked for this??!!"'}]})
    doc, art, sup = d / "doc.md", d / "art.txt", d / "sup.md"
    doc.write_text("The principal's plan line.\n", encoding="utf-8")
    art.write_text("x", encoding="utf-8")
    sup.write_text("A cited plan line.\nmore\nSuperseded: see below\n", encoding="utf-8")
    ctx = ctx_load(bank, [], d)
    base = {
        "evidence": [["REPRODUCED", "ran it", "here"]], "artifacts": ["art.txt"],
        "reproduced_at": now.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "chain": [
            {"node": "R", "quote": clause, "source": "clause-1", "fit": "states", "speech_act": "assert", "why": ""},
            {"node": "W", "quote": "The principal's plan line.", "source": "path:doc.md", "fit": "supports",
             "why": "the plan line is what this wait is about"}]}

    def variant(**kw):
        n = json.loads(json.dumps(base))
        for k, v in kw.items():
            if k == "link0":
                n["chain"][0].update(v)
            elif k == "link1":
                n["chain"][1].update(v)
            else:
                n[k] = v
        return n

    cases = [
        ("good chain passes", variant(), ["R", "W"], False),
        ("altered root quote fails", variant(link0={"quote": clause + " and then some"}), ["R", "W"], True),
        ("skipped tree node fails", variant(), ["R", "X", "W"], True),
        ("empty why fails", variant(link1={"why": ""}), ["R", "W"], True),
        ("no REPRODUCED fails", variant(evidence=[["REPORTED", "said so", "board"]]), ["R", "W"], True),
        ("root not stating the value fails", variant(link0={"fit": "supports"}), ["R", "W"], True),
        ("dialog quote from mid-answer fails",
         variant(link0={"quote": "then tune it later", "source": "dialog-1#a0"}), ["R", "W"], True),
        ("dialog quote at the answer start passes",
         variant(link0={"quote": "Publish the small version first", "source": "dialog-1#a0"}), ["R", "W"], False),
        ("quote followed by 'Superseded' fails",
         variant(link1={"quote": "A cited plan line.", "source": "path:sup.md"}), ["R", "W"], True),
        ("exemption with a stated reason passes",
         variant(evidence=[], artifacts=[], reproduction_na="principal preference, no artifact"), ["R", "W"], False),
        ("a question quote labelled assert fails",
         variant(link0={"quote": "Who asked for this??!!", "source": "dialog-2#a0", "speech_act": "assert"}), ["R", "W"], True),
        ("the same quote labelled deny passes",
         variant(link0={"quote": "Who asked for this??!!", "source": "dialog-2#a0", "speech_act": "deny"}), ["R", "W"], False),
        ("a principal link without a speech act fails", variant(link0={"speech_act": ""}), ["R", "W"], True),
        ("artifact newer than the reproduction fails", None, ["R", "W"], True),
    ]
    bad = 0
    for name, node, path, want_fail in cases:
        if node is None:
            node = variant()
            later = now.timestamp() + 3600
            os.utime(art, (later, later))
        got = bool(_node_fails(node, path, ctx))
        ok = got == want_fail
        bad += not ok
        print(("ok   " if ok else "WRONG") + f" {name} (expected {'fail' if want_fail else 'pass'}, got {'fail' if got else 'pass'})")
    q14 = {"source": "dialog-2", "quote": "Who asked for this??!!", "speech_act": "deny",
           "reading": "The principal rejects the premise that the request is theirs; it names no one else."}
    for name, cb, want_fail in [
            ("closure: rhetorical question labelled deny, with a reading, passes", q14, False),
            ("closure: the same labelled assert fails", {**q14, "speech_act": "assert"}, True),
            ("closure: no reading fails", {**q14, "reading": ""}, True),
            ("closure: a document is not the principal's words",
             {"source": "path:doc.md", "quote": "The principal's plan line.", "speech_act": "deny", "reading": q14["reading"]}, True)]:
        got = bool(_closure_fails(cb, ctx))
        ok = got == want_fail
        bad += not ok
        print(("ok   " if ok else "WRONG") + f" {name} (expected {'fail' if want_fail else 'pass'}, got {'fail' if got else 'pass'})")
    d2 = d / "bank-malformed"
    _write_bank(d2, {f: [{"id": "x:" + f, "text": "ok"}] for f in BANK_FILES})
    with (d2 / "principal-clauses.jsonl").open("a", encoding="utf-8") as fh:
        fh.write("not json\n[1]\n\n")
    c2 = ctx_load(d2, [], d)
    ok = c2["bad"] == 2 and len(c2["bank"]) == 4 and not c2["missing"]
    bad += not ok
    print(("ok   " if ok else "WRONG") + f" bank: 2 malformed lines are skipped and counted, 4 good records kept (expected 2/4, got {c2['bad']}/{len(c2['bank'])})")
    d3 = d / "bank-missing"
    _write_bank(d3, {}, names=BANK_FILES[:3])
    c3 = ctx_load(d3, [], d)
    ok = c3["missing"] == ["principal-comments.jsonl"]
    bad += not ok
    print(("ok   " if ok else "WRONG") + f" bank: an absent bank file is named as missing (expected ['principal-comments.jsonl'], got {c3['missing']})")
    return 1 if bad else 0


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        return _cases(pathlib.Path(tmp))


def main(argv=None):
    """The verbs check, render ID, baseline and selftest. Returns the exit code."""
    parser = argparse.ArgumentParser(prog="loop gate", description="a wait must carry a verified chain of verbatim quotes down to a root, or a closure in the principal's words")
    sub = parser.add_subparsers(dest="cmd", metavar="VERB", required=True)
    sub.add_parser("check", help="verify every wait, write the state file; exit 1 on a new failure")
    sub.add_parser("baseline", help="record the current failing waits as dated debt")
    sub.add_parser("selftest", help="synthetic cases; each must come out as expected")
    r = sub.add_parser("render", help="print the chain of one node")
    r.add_argument("id", help="the node id")
    try:
        a = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    except SystemExit as e:
        return int(e.code or 0)
    if a.cmd == "selftest":
        return selftest()
    cfg = config.load()
    if a.cmd == "check":
        return check(cfg)
    if a.cmd == "render":
        return render(cfg, a.id)
    return baseline(cfg)


if __name__ == "__main__":
    sys.exit(main())
