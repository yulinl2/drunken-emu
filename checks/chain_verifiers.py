#!/usr/bin/env python3
"""checks/chain_verifiers.py -- the ten verifiers of docs/OPERATION-MODEL.md section 5, over a recorded chain.

Content-blind by construction.  `run_chain` hands every verifier `chain.blind(chain)`: enums, numbers, booleans and
three kinds of opaque label (`intent`/`view` keys, `held` labels, RELOAD `source`) that are compared or counted and
never interpreted.  Free text (`target`, `note`, ...) is not in what a verifier receives.  checks/test_chain.py proves
it twice: a tripwire where the text lives, and a mutation (replace every free-text field: the findings stay equal).

Every verifier has the same shape:   verifier(chain, cfg) -> [{"verifier", "step", "message"}, ...]
  * at most ONE finding per step per verifier (reasons are joined), so "the steps it flags" is a clean list;
  * `step` is the 1-based step number in the chain file;
  * a verifier looks only at steps that DECLARE the property it checks.  Silence therefore means "nothing declared
    wrong", never "nothing wrong": each docstring says what it cannot see.

   name                   OPERATION-MODEL   issue
   anchoring              5.1               #38
   memory_budget          5.2               #33
   candidate_set          5.3               #38
   interruption           5.4               #34
   colocation             5.5               #35
   progress               5.6               #36
   causal                 5.7               #37
   single_path            5.8               #39
   commit_correctness     5.9               #39
   separators             5.10              #31 (no sub-issue of its own)
"""
from __future__ import annotations

from dataclasses import dataclass

from chain import DEFAULT_BUDGET, LOSSES, READING_ONLY, blind, resolve_budget
from chain_load import chain_load

LOOKALIKE = 0.5          # similarity at or above which confusables count as look-alikes (anchoring)


@dataclass(frozen=True)
class Config:
    budget: int = DEFAULT_BUDGET
    lookalike: float = LOOKALIKE


def _f(name: str, step: dict, message: str) -> dict:
    return {"verifier": name, "step": step["n"], "message": message}


def anchoring(chain: dict, cfg: Config) -> list[dict]:
    """5.1 (#38): choosing among look-alikes needs an anchor other than reading.

    Flags a step whose `confusables` are look-alikes (count >= 1 and similarity >= cfg.lookalike, default 0.5)
    when its `anchor` is text-keyword or none.  An edge, a fixed position or a unique visual is a way to find
    the target without reading it; a keyword among near-identical names is not.
    Cannot see: whether the declared anchor is true; look-alikes the narrator did not count; whether 0.5 is the
    right line (it is a default; `bin/emu chain check --lookalike X` moves it); a choice the narrator gave no
    `confusables`.
    """
    out = []
    for s in chain["steps"]:
        c = s["confusables"]
        if c["count"] >= 1 and c["similarity"] >= cfg.lookalike and s["anchor"] in READING_ONLY:
            out.append(_f("anchoring", s, f"{s['op']} chooses among {c['count']} look-alike(s) (similarity "
                          f"{c['similarity']:.2f}) by reading only (anchor: {s['anchor']}); give the target an "
                          f"edge, fixed-position or unique-visual anchor, or remove the look-alikes"))
    return out


def memory_budget(chain: dict, cfg: Config) -> list[dict]:
    """5.2 (#33): held slots never exceed B, and no chain needs a RELOAD to finish.

    A step's working set is `need` (what it juggles itself) + the items in `held`.  Flags demand > cfg.budget
    (default 3), and every RELOAD step (the goal fell out of memory and was fetched from outside).
    Cannot see: what the person really held (`held` is the narrator's list: a forgotten item under-reports);
    B is a parameter, not a measurement of anyone; it does not know a RELOAD is avoidable.
    """
    out = []
    for s in chain["steps"]:
        held = len(s["held"])
        demand = s["need"] + held
        why = []
        if demand > cfg.budget:
            why.append(f"working set is {demand} slots (the step needs {s['need']}, {held} held across it), "
                       f"more than B={cfg.budget}: something falls out")
        if s["op"] == "RELOAD":
            why.append(f"RELOAD from {s['source']!r}: the goal had fallen out of memory, so the chain needs a "
                       f"detour to finish")
        if why:
            out.append(_f("memory_budget", s, "; ".join(why)))
    return out


def candidate_set(chain: dict, cfg: Config) -> list[dict]:
    """5.3 (#38): the person can see the option set is complete without ENUMERATE across screens.

    Flags every ENUMERATE step whose `set_visibly_complete` is not true (default false: an ENUMERATE exists
    because the screen did not say "all N shown").  `pages` only sharpens the message.
    Cannot see: a set the person never tried to enumerate (no ENUMERATE step, so no flag), a "complete" claim
    the page makes falsely, or sets that are complete but badly ordered.
    """
    out = []
    for s in chain["steps"]:
        if s["op"] == "ENUMERATE" and not s["set_visibly_complete"]:
            out.append(_f("candidate_set", s, f"the option set is not visibly complete: the person pages through "
                          f"{s['pages']} screen(s) and checks the seams (show a count or 'all shown')"))
    return out


def interruption(chain: dict, cfg: Config) -> list[dict]:
    """5.4 (#34): after a refresh, or leaving and returning, position, goal and partial work are restored.

    Flags (a) a step that declares `restores` (REFRESH always does; RE-ORIENT and NAVIGATE may) and does not list
    all of position, goal, partial; (b) any step whose `interruption` is non-empty: leaving at that step loses it.
    List all three in `restores` even when nothing of one kind existed: nothing lost counts as restored.
    Cannot see: a refresh or an app switch nobody recorded; whether a restored view is the SAME view (a
    restored position that lands one screen off); interruptions longer than the narrator's one step.
    """
    out = []
    for s in chain["steps"]:
        why = []
        if "restores" in s:
            lost = [x for x in LOSSES if x not in s["restores"]]
            if lost:
                why.append(f"after {s['op']} not restored: {', '.join(lost)}")
        if s["interruption"]:
            why.append(f"an interruption (refresh, app switch) at this step loses: {', '.join(s['interruption'])}")
        if why:
            out.append(_f("interruption", s, "; ".join(why)))
    return out


def colocation(chain: dict, cfg: Config) -> list[dict]:
    """5.5 (#35): at COMMIT, everything the decision depends on is on screen.

    Flags a COMMIT with `everything_on_screen` false (what each row will become, not only that it will change),
    or with `preview_before` false unless the commit is idempotent (nothing to regret).
    Cannot see which information a decision depends on: `everything_on_screen` is the narrator's yes or no.
    A chain that marks a commit idempotent silences the preview rule; the label is a claim, not a check.
    """
    out = []
    for s in chain["steps"]:
        if s["op"] != "COMMIT":
            continue
        why = []
        if not s["everything_on_screen"]:
            why.append("not everything the decision depends on is on screen (a review that cannot show what each "
                       "row becomes is a formality)")
        if not s["preview_before"] and s["reversibility"] != "idempotent":
            why.append(f"no preview before a {s['reversibility']} COMMIT")
        if why:
            out.append(_f("colocation", s, "; ".join(why)))
    return out


def progress(chain: dict, cfg: Config) -> list[dict]:
    """5.6 (#36): during WAIT the view stays put and progress is visible; a partial result says what is left.

    Flags a WAIT with `progress_visible` false, `view_stable` false, or `partial_result_says_left` false (absent
    means this wait yields no partial result), and any step whose `feedback` is none (an action the person cannot
    tell registered).
    Cannot see: whether a visible spinner is honest; the length of a wait; a wait the narrator wrote as no step.
    """
    out = []
    for s in chain["steps"]:
        why = []
        if s["op"] == "WAIT":
            if not s["progress_visible"]:
                why.append("no visible progress during the wait")
            if not s["view_stable"]:
                why.append("the view moves during the wait")
            if s.get("partial_result_says_left") is False:
                why.append("the partial result does not say what is left (or why the rest failed)")
        if s["feedback"] == "none":
            why.append("the action got no feedback: the person cannot tell it registered")
        if why:
            out.append(_f("progress", s, "; ".join(why)))
    return out


def causal(chain: dict, cfg: Config) -> list[dict]:
    """5.7 (#37): every list or prompt says where it came from and what it does not include (no wrong INFER).

    Looks at steps that declare BOTH `origin_stated` and `exclusions_stated` (a step that shows a list or a
    prompt) and flags a false one.  If an INFER follows within three steps the message names it: it is the
    person's guess at the cause the screen did not give.
    Cannot see: whether an inference is actually wrong (only that the screen gave no basis for it); a list the
    narrator did not mark as list-showing; what the list should have said.
    """
    out = []
    steps = chain["steps"]
    for i, s in enumerate(steps):
        if "origin_stated" not in s:
            continue
        why = []
        if not s["origin_stated"]:
            why.append("does not say where it came from")
        if not s["exclusions_stated"]:
            why.append("does not say what is left out or not yet included")
        if why:
            nxt = next((t for t in steps[i + 1:i + 4] if t["op"] == "INFER"), None)
            msg = "the list or prompt shown here " + " and ".join(why)
            if nxt:
                msg += f"; the person then has to INFER its cause (step {nxt['n']})"
            out.append(_f("causal", s, msg))
    return out


def single_path(chain: dict, cfg: Config) -> list[dict]:
    """5.8 (#39): one action per intent; two views that do the same job are one finding.

    Groups steps by `intent` and flags an intent served from two or more distinct `view`s: ONE finding per intent,
    placed at the step where the second view first appears.  Put `intent` only on steps that PERFORM the job,
    not on steps that travel to it.
    Cannot see: two views doing the same job under different intent keys; whether the narrator's `view` keys
    name views a person would call different; intents the narrator left off.  Compares keys, never meanings.
    """
    seen: dict[str, list[tuple[str, dict]]] = {}
    for s in chain["steps"]:
        if s["intent"]:
            views = seen.setdefault(s["intent"], [])
            if s["view"] not in [v for v, _ in views]:
                views.append((s["view"], s))
    out = []
    for intent, views in seen.items():
        if len(views) >= 2:
            where = ", ".join(f"{v!r} (step {st['n']})" for v, st in views)
            out.append(_f("single_path", views[1][1], f"intent {intent!r} is served by {len(views)} views: {where}; "
                          f"keep one path"))
    return sorted(out, key=lambda f: f["step"])


def commit_correctness(chain: dict, cfg: Config) -> list[dict]:
    """5.9 (#39): after a commit the system re-reads the target and reports correctness against intent.

    For every COMMIT: `verify_after` must be correctness (an idempotent commit may stop at consistency), and a
    later VERIFY step of an allowed `kind` must exist in the chain, so the chain shows the person seeing the check.
    Consistency says "A matches B"; correctness says "A matches what was meant".
    Cannot see: whether a reported "correct" is correct; a re-read the system does but never shows; whether the
    later VERIFY step is about this commit (it only has to come after it).
    """
    out = []
    steps = chain["steps"]
    for i, s in enumerate(steps):
        if s["op"] != "COMMIT":
            continue
        ok = ("consistency", "correctness") if s["reversibility"] == "idempotent" else ("correctness",)
        why = []
        if s["verify_after"] not in ok:
            why.append(f"after COMMIT the system offers {s['verify_after']!r} only (verify_after); it should "
                       f"re-read the target and report {' or '.join(ok)} against intent")
        if not any(t["op"] == "VERIFY" and t["kind"] in ok for t in steps[i + 1:]):
            why.append(f"no later VERIFY step of kind {' or '.join(ok)}: the person is never shown the result checked")
        if why:
            out.append(_f("commit_correctness", s, "; ".join(why)))
    return out


def separators(chain: dict, cfg: Config) -> list[dict]:
    """5.10 (no sub-issue; under #31): block boundaries are visible without reading the content.

    Flags a step whose `boundary_visible` is false: where one block ends and the next begins (a key, then the
    grader's note) is recoverable only by reading, which is why the person narrowed paragraph, then sentence.
    Cannot see: text the narrator did not mark as block-structured; what the right separator would be.
    """
    out = []
    for s in chain["steps"]:
        if s.get("boundary_visible") is False:
            out.append(_f("separators", s, "the boundary between blocks is only visible by reading the content "
                          "(e.g. where a key ends and a note begins)"))
    return out


# name -> (function, OPERATION-MODEL section 5 item, issue); the order IS the section 5 numbering
VERIFIERS = {
    "anchoring": (anchoring, "5.1", "#38"),
    "memory_budget": (memory_budget, "5.2", "#33"),
    "candidate_set": (candidate_set, "5.3", "#38"),
    "interruption": (interruption, "5.4", "#34"),
    "colocation": (colocation, "5.5", "#35"),
    "progress": (progress, "5.6", "#36"),
    "causal": (causal, "5.7", "#37"),
    "single_path": (single_path, "5.8", "#39"),
    "commit_correctness": (commit_correctness, "5.9", "#39"),
    "separators": (separators, "5.10", "#31"),
}
ORDER = list(VERIFIERS)


def run_chain(chain: dict, budget: int | None = None, lookalike: float = LOOKALIKE) -> dict:
    """Load numbers and findings for one chain.  The verifiers see only the blind view."""
    b = resolve_budget(chain, budget)
    cfg = Config(budget=b, lookalike=lookalike)
    view = blind(chain)
    findings: list[dict] = []
    for fn, _, _ in VERIFIERS.values():
        findings.extend(fn(view, cfg))
    findings.sort(key=lambda f: (f["step"], ORDER.index(f["verifier"])))
    return {"id": chain["id"], "budget": b, "load": chain_load(view, b), "findings": findings}


def check_doc(doc: dict, budget: int | None = None, ids: list[str] | None = None) -> list[dict]:
    """run_chain over every chain of a normalised document (optionally only the chains named in `ids`)."""
    return [run_chain(c, budget) for c in doc["chains"] if not ids or c["id"] in ids]


def steps_by_verifier(findings: list[dict]) -> dict[str, list[int]]:
    """{verifier: [step, ...]} for the verifiers that fired; handy for tests and for reading a report."""
    out: dict[str, list[int]] = {}
    for f in findings:
        out.setdefault(f["verifier"], []).append(f["step"])
    return out
