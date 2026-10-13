#!/usr/bin/env python3
"""
draft_publish_prediction.py -- the prediction registered BEFORE the owner's first run of the draft publisher
(speeds-kit userscripts/draft-publish.user.js, docs/DRAFT-PUBLISH.md), in the form checks/prediction_score.py scores.

Second registration. The first (commit 3e87f6f, publisher 0.2.2) was for a build without the audit layer (A1-A4), at B = 3, and asked the owner for
narration and screenshots, which the owner's rule 2 forbids. This one is for the build the owner holds: publisher 0.3.1 (speeds-kit commit below).
Nothing is scored; nobody has used the flow on a phone. A change of the fixture after the push is a NEW dated registration: do not edit this one
(the pin test fails if the fixture or the measurement changes).

    python3 checks/draft_publish_prediction.py BUILD.txt   # BUILD.txt: five lines: speeds-kit commit, template sha256, delivered-file sha256, template lines, publisher version

Writes docs/predictions/draft-publish-first-run.prediction.json (schema emu-prediction/1) and .md. Reads checks/fixtures/chains/draft_publish_hw2.json,
runs `bin/emu chain check --json` on it (and at B = 3 and 4), and reads docs/predictions/draft-publish-first-run.measured.json (the facts of
`python3 -m speedkit.rehearse --json`: boxes and sizes of the sheet on a mock Canvas, 390 x 844 touch; no name, grade or comment). Stdlib only.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "checks/fixtures/chains/draft_publish_hw2.json"
MEASURED = ROOT / "docs/predictions/draft-publish-first-run.measured.json"
OUT_JSON = ROOT / "docs/predictions/draft-publish-first-run.prediction.json"
OUT_MD = ROOT / "docs/predictions/draft-publish-first-run.md"
PID = "draft-publish-first-run"
BASES = ["measured", "declared", "carried-from-HW1", "guess"]
BUDGET, SENSITIVITY = 2, [3, 4]

NOCLOCK = "nobody keeps a clock: the owner is asked for nothing, and the run's record times only the write itself"
# id, short, name, comparable by duration?, why not
SEGMENTS = [
    ("dp-install-check", "S1", "install and first read", False, "starts when a person (the coordinating session) says the file is ready, and runs through the chat app, Files and Safari; " + NOCLOCK),
    ("dp-audit-look", "S2", "look at the rubric and at one student (the audit)", False, "optional, as far as the owner takes it; " + NOCLOCK),
    ("dp-trial-write", "S3", "one-student trial write", False, "happens only if the assignment posts grades at once; " + NOCLOCK),
    ("dp-look-at-one", "S4", "look at the written student", False, "follows S3; " + NOCLOCK),
    ("dp-write-rest", "S5", "write the rest", False, "follows S3 and S4; " + NOCLOCK),
    ("dp-write-all", "S6", "one-tap write (the Manual policy)", False, "happens only if the policy is Manual; " + NOCLOCK),
    ("dp-rubric-step", "S7", "create the rubric (only if Canvas has none)", False, "happens only if HW2 has no rubric on Canvas; " + NOCLOCK),
    ("dp-failure-retry", "S8", "a run with failures, and the retry", False, "happens only if a run ends with failures"),
    ("dp-interrupted-run", "S9", "coming back after an interrupted write", False, "happens only if the page dies in the middle of the long write"),
    ("dp-move-button", "S10", "move the blue button", False, "happens only if the button is in the way"),
    ("dp-manual-set", "S11", "Manual route: set the policy", False, "optional: only if the owner takes the Manual route; Canvas's own screens"),
    ("dp-manual-post", "S12", "Manual route: post the grades", False, "optional: only if the owner takes the Manual route; Canvas's own screens"),
]

# id, chain, step, kind, event, observable, p, basis, rests_on
# Observables are what the owner says in the chat unasked, a screenshot sent unasked, or the run's own record (A3: 复制最近一次记录) if it is ever pasted. Nothing is requested.
E = [
    ("I1", "dp-install-check", 6, "friction", "the file does not reach the Userscripts folder on the first try (wrong folder, unsure which, or saved again)", "the owner says the file went to another folder or was saved again, or the blue button never appears after the reload", 0.25, "guess", "HW1 A4 says the remembered folder costs nothing, for another destination; nothing on the save sheet says which folder is right"),
    ("I2", "dp-install-check", 10, "friction", "after the reload the owner is unsure whether the script is installed, and looks for or waits for the button", "the owner asks whether it installed, or says the button did not show", 0.30, "declared", "progress finding at step 10: nothing on the page says the script is there until the 初稿 button appears"),
    ("I2b", "dp-install-check", 14, "friction", "an older copy of an hw2 file is mounted instead of this one (the owner was sent several today); the sheet's title carries an older version or has no dock", "the owner describes a sheet unlike the one described, or the run's record names an older publisher (draft-publish 0.3.0 or earlier)", 0.25, "guess", "Userscripts keeps files by name; the message says to delete the old copies; the first host on the page wins (the second sees the host and does nothing)"),
    ("I3", "dp-install-check", 11, "friction", "the owner cannot find the 初稿 button on the SpeedGrader page, or it covers something and is not moved", "the owner says so", 0.10, "guess", "its place (top right, 72 px down) was measured on the mock page, not on the real SpeedGrader; since 0.3.1 it can be dragged"),
    ("I4", "dp-install-check", 13, "friction", "the first read ends in a red line instead of the counts (a refusal, a lost login, an answer of Canvas the script did not expect)", "the owner says there is a red line, or sends it", 0.20, "guess", "the real Canvas has not been tried; the guards (points total, grading type, group, anonymous, moderated) and the field names are assumptions"),
    ("I5", "dp-install-check", 14, "friction", "the sheet says that more than half of the students' files do not match (the file ids mean something else than the script assumes)", "the owner mentions the line about the file check or its button", 0.20, "guess", "the middle number of Canvas's file names is assumed to be the attachment id (about 80% sure)"),
    ("I6", "dp-install-check", 15, "friction", "the numbers on the sheet differ from the message (57 to write, 2 held by the file check, 10 held) and the owner stops to work out why", "the owner says the numbers were not what the message said", 0.20, "guess", "skipped, absent and unchecked counts depend on the real course (graded students, a missing-submission zero)"),
    ("I7", "dp-install-check", 14, "smooth", "the counts, the foot and the main button are in view together on the first screen, with no scrolling", "nothing in the owner's messages says the button or the counts were out of reach", 0.90, "measured", "docs/predictions/draft-publish-first-run.measured.json: in every state of the rehearsal the dock (status, foot, buttons) is in view, 289 to 329 px of the 692 px sheet, with every list opened"),
    ("A1", "dp-audit-look", 1, "friction", "the rubric line is red: Canvas's rubric differs from the file and the sheet writes nothing", "the owner mentions a red rubric line or sends it", 0.15, "guess", "the rubric on Canvas was made by TapGrade's setup or by hand; the sheet compares rows, maxima and numbering"),
    ("A2", "dp-audit-look", 6, "friction", "the owner does not go through the 57 bars: the list has no order by total or by flag, only names, so they open a few or none", "the owner says they only looked at some, or did not look", 0.45, "declared", "A2 lists every student with the total and the deductions in one line, in Canvas's order; nothing orders it or marks the odd ones"),
    ("A3", "dp-audit-look", 8, "friction", "the owner does not read an opened student's rows to the end", "the owner says they did not read it all", 0.55, "declared", "measured: one open student is 2173 px, 5.6 screens of the scrolling part, because the [Key] lines are long"),
    ("T1", "dp-trial-write", 1, "friction", "the owner does not see why only one student is written the first time", "the owner says they did not understand the one-student step, or taps expecting all", 0.20, "declared", "the foot's first line and the button label ('先试写 1 位') say it; the owner has no habit for it yet"),
    ("T2", "dp-trial-write", 3, "friction", "the owner does not read the first student's open bar to the end, or skips it", "the owner says they did not read it", 0.55, "declared", "measured: the bar starts 439 px down a scrolling part that shows 364 px, and is 2173 px tall (5.6 screens); a reader taps when the button is in view"),
    ("T3", "dp-trial-write", 5, "friction", "the owner hesitates at the confirmation (reads it twice, or cancels and starts again)", "the owner says they hesitated or cancelled", 0.30, "guess", "an irreversible write that the student sees at once; the dialog is native text of five foot lines and a sentence"),
    ("T4", "dp-trial-write", 7, "friction", "the trial write ends with a red line instead of 试写完成", "the owner says the trial failed, or sends the red line", 0.30, "guess", "the first real write on the real Canvas: permissions, the rubric assessment form, the rate limit"),
    ("T5", "dp-trial-write", 11, "friction", "after the reload the owner cannot find the written student in SpeedGrader", "the owner says they searched for the student", 0.30, "guess", "the sheet lists in the order of the names; SpeedGrader's own order is assumed to be the same"),
    ("T6", "dp-trial-write", 9, "smooth", "the owner takes the result line as the check and does not look for a proof elsewhere", "the owner does not say they verified the write by other means than looking at the student", 0.70, "declared", "the line says the write was read back and matched; the run's record holds every row before and after"),
    ("T7", "dp-trial-write", 8, "friction", "the owner does not know what to do after the trial (the result line is six lines long on a 390 px sheet)", "the owner asks what now", 0.25, "declared", "measured: 0.3.1's line is long and the dock is 422 px of 692 px right after the trial, so the lists keep 39 % of the sheet; 0.3.2 shortens it"),
    ("K1", "dp-trial-write", 2, "friction", "the dock leaves too little of the sheet to scroll the lists comfortably (39 % of the sheet right after the trial, 55 % at the first read)", "the owner says the sheet is cramped or the list hard to scroll", 0.15, "guess", "measured by speedkit.rehearse: the lists keep 55 % of the sheet at the first read and 39 % after the trial in 0.3.1"),
    ("L1", "dp-look-at-one", 2, "friction", "SpeedGrader does not show the written comments at first (the rubric is collapsed or the comments need a tap)", "the owner says the comments were not visible at first", 0.35, "guess", "how SpeedGrader shows free-form criterion comments on a phone is not known"),
    ("L2", "dp-look-at-one", 4, "friction", "the owner finds a deduction or a comment they think is wrong in the first student", "the owner says something looked wrong", 0.40, "guess", "an unreviewed machine draft; HW1's first pass had errors; the draftcheck report lists 11 students whose notes praise a joint F-test argument and still deduct (the key accepts only 'Yes')"),
    ("L3", "dp-look-at-one", 3, "friction", "the comment layout (tags such as [Q5b-gen], long keys, 'part not attempted' on partial answers) looks odd or too long to the owner", "the owner says the comments looked strange or too long", 0.25, "guess", "the layout is TapGrade's, which the owner knows; keys are long; the coordinating session found the label 'part not attempted' on 216 lines, some for answers the student attempted"),
    ("L4", "dp-look-at-one", 4, "friction", "the owner stops after the look and does not write the rest in the same sitting", "the owner or the chat says they stopped", 0.20, "guess", "depends on what they see in L2"),
    ("W1", "dp-write-rest", 1, "friction", "the owner does not find the way back to the pending write (the button reads 初稿·已试写)", "the owner says they did not know what to do next", 0.15, "declared", "the label and the line 'you wrote only <name> last time' are meant to bring the goal back"),
    ("W2", "dp-write-rest", 4, "friction", "the counts after the trial surprise the owner (the written student counts as already the draft)", "the owner says the numbers were not what they expected", 0.15, "guess", "the count of 'already the draft' is 1 at this point"),
    ("W3", "dp-write-rest", 7, "friction", "the owner hesitates at the second confirmation", "the owner says they hesitated", 0.15, "guess", "after looking at one student the decision is made; the dialog is the same kind"),
    ("W4", "dp-write-rest", 9, "friction", "the long write ends with one or more failed students", "the run's record shows a failure count above 0, or the owner says so", 0.45, "guess", "the first run at scale on the real Canvas: rate limits, permission quirks, a student with no enrolment"),
    ("W5", "dp-write-rest", 9, "friction", "the page is interrupted during the long write (the phone locks, another app, a reload)", "the button read 初稿·未完, the record says 没有写完, or the owner says so", 0.25, "guess", "1 to 3 minutes on a phone; Safari may suspend a tab that is not in view"),
    ("W6", "dp-write-rest", 12, "friction", "the owner adds the numbers up (1 + 56 = 57) and they do not match what the sheet said at the first read", "the owner says the totals did not match", 0.20, "guess", "skipped, unchecked and held counts depend on the real course; the sheet does not add them up for the owner"),
    ("W7", "dp-write-rest", 10, "smooth", "the final line is understood at the first reading", "the owner does not say they re-read it", 0.80, "declared", "one line with three numbers and the read-back statement"),
    ("O1", "dp-write-all", 4, "friction", "the owner hesitates at the confirmation of the 57-student write", "the owner says they hesitated or cancelled", 0.30, "guess", "no student has been looked at in SpeedGrader first; the policy (hidden until posted) is the safety"),
    ("O2", "dp-write-all", 6, "friction", "the long write ends with one or more failed students", "the run's record shows a failure count above 0, or the owner says so", 0.45, "guess", "as W4"),
    ("O3", "dp-write-all", 7, "smooth", "the final line is understood at the first reading", "the owner does not say they re-read it", 0.80, "declared", "as W7"),
    ("B1", "dp-rubric-step", 6, "friction", "creating the rubric is refused or ends in a red line", "the owner says the rubric step failed, or sends the red line", 0.30, "guess", "the rubric form (criteria, ratings, association) was never tried on the real Canvas; only if HW2 has no rubric"),
    ("B2", "dp-rubric-step", 8, "smooth", "the read-back matches the file row by row and the write button appears", "the owner does not report a mismatch", 0.65, "declared", "the sheet shows the rows before the tap and reads them back after it (A1)"),
    ("F1", "dp-failure-retry", 2, "friction", "the owner does not understand Canvas's own error text for a failed student", "the owner says the message was unclear (only if a run had failures)", 0.50, "declared", "the message is Canvas's, in English or a status code; it says why, not what to do"),
    ("F2", "dp-failure-retry", 9, "smooth", "one retry clears all the failures", "the second run's record ends with 0 failed (only if a run had failures)", 0.60, "guess", "failures of a first run are often a rate limit or a timeout"),
    ("R1", "dp-interrupted-run", 3, "smooth", "after an interrupted write the owner understands the red line and writes the rest without asking", "the owner continues without a question (only if a write was interrupted)", 0.75, "declared", "the sheet opens by itself and says the last run did not finish"),
    ("D1", "dp-move-button", 2, "friction", "dragging the blue button does not work on the phone (it opens the sheet, scrolls the page, or does not move)", "the owner says so (only if they try)", 0.25, "guess", "tested with real touch events and a mouse in Chromium, not in an iPhone's WebKit inside the Userscripts extension"),
    ("M1", "dp-manual-set", 4, "friction", "the owner needs more than one try to find Grade Posting Policy in the Gradebook", "the owner says the setting was hard to find (only if the route is taken)", 0.50, "guess", "Canvas's screens; not narrated by this owner"),
    ("M2", "dp-manual-post", 4, "friction", "the owner needs more than one try to find Post grades in the Gradebook", "the owner says it was hard to find (only if the route is taken)", 0.50, "guess", "Canvas's screens; not narrated by this owner"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chain_check(budget: int | None = None) -> dict:
    cmd = [str(ROOT / "bin/emu"), "chain", "check", str(FIXTURE.relative_to(ROOT)), "--json"] + (["--budget", str(budget)] if budget else [])
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode not in (0, 1):
        raise SystemExit(f"chain check failed ({r.returncode}): {r.stderr[-400:]}")
    return json.loads(r.stdout)


def avg_ranks(values: dict[str, float], descending: bool = True) -> dict[str, float]:
    order = sorted(values, key=lambda k: -values[k] if descending else values[k])
    ranks, i = {}, 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in order[i:j + 1]:
            ranks[k] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def build(info: dict) -> dict:
    fix = json.loads(FIXTURE.read_text(encoding="utf-8"))
    steps_of = {c["id"]: c["steps"] for c in fix["chains"]}
    check = chain_check()
    by_id = {c["id"]: c for c in check["files"][0]["chains"]}
    onsets = {b: {cid: sorted(f["step"] for f in c["findings"] if f["verifier"] == "memory_budget") for cid, c in {c["id"]: c for c in chain_check(b)["files"][0]["chains"]}.items()} for b in [BUDGET] + SENSITIVITY}
    segs = []
    for cid, short, name, comparable, why in SEGMENTS:
        c = by_id[cid]
        segs.append({"id": cid, "short": short, "name": name, "comparable_by_duration": comparable, "not_comparable_because": why, "steps": c["steps"], "load": c["load"],
                     "peak_slots": c["peak_slots"], "predicted_loss_onsets_at_B": {str(b): onsets[b][cid] for b in [BUDGET] + SENSITIVITY}})
    load = {s["id"]: s["load"] for s in segs}
    count = {s["id"]: s["steps"] for s in segs}
    rank = avg_ranks(load)
    groups = {}
    for k, v in sorted(rank.items(), key=lambda kv: kv[1]):
        groups.setdefault(v, []).append(k)
    events = []
    for eid, cid, step, kind, ev, obs, p, basis, why in E:
        assert basis in BASES and 0 < p < 1, eid
        assert 1 <= step <= len(steps_of[cid]), (eid, cid, step)
        events.append({"id": eid, "segment": cid, "kind": kind, "steps": [{"chain": cid, "step": step, "op": steps_of[cid][step - 1]["op"]}], "event": ev, "observable": obs, "p": p, "basis": basis, "rests_on": why})
    measured = json.loads(MEASURED.read_text(encoding="utf-8"))
    return {
        "schema": "emu-prediction/1", "id": PID,
        "title": f"The first run of the draft publisher on the owner's phone: HW2's machine drafts into Canvas (speeds-kit userscripts/draft-publish.user.js {info['version']}), second registration",
        "registered_by": "the commit that adds this version of this file: its commit time is the registration time; it was pushed before the owner was told the flow was registered",
        "supersedes": {"commit": "3e87f6f5085a5c8533f5fe73e4396f2e8e98d80b", "why": "that registration was for speeds-kit 70f8ef6 (publisher 0.2.2): no audit layer (A1-A4), B = 3, held lists that kept the goal and the chat's numbers in memory through the whole sheet, and it asked the owner for narration and screenshots (rule 2 of the owner's rules forbids it). It is void; git keeps it."},
        "drafted": info["drafted"], "spec": "theory/RECORD-THEORY.md sections 5 and 8; issue #32, test point E5 (a second pass); the owner's remarks of 2026-10-12 that the newest issues and PRs of this repository were left hanging and that memory load was not computed",
        "artifact": {"repository": "speeds-kit", "commit": info["commit"], "script": "userscripts/draft-publish.user.js", "script_sha256": info["script_sha256"], "script_lines": int(info["lines"]),
                     "version": info["version"], "delivered_file_sha256": info["file_sha256"], "delivered_file": "rutgers-fa26-463-regression/hw2/drafts/hw2-drafts.user.js (private: it holds student grades; not in the repository; reproducible from the template of that commit and the data)",
                     "mock_canvas": "tests/tapgrade/mock_canvas.py of the same commit", "docs_read": "docs/DRAFT-PUBLISH.md and the script itself"},
        "fixture": {"path": str(FIXTURE.relative_to(ROOT)), "sha256": sha(FIXTURE)},
        "measured": {"path": str(MEASURED.relative_to(ROOT)), "sha256": sha(MEASURED), "tool": "python3 -m speedkit.rehearse (speeds-kit 0a73c79), content-blind: boxes and sizes only, 390x844 touch, headless Chromium, mock Canvas, the real HW2 draft data rebound to the mock", "states": [s["state"] for s in measured["states"]]},
        "scorer": {"path": "checks/prediction_score.py", "sha256": sha(ROOT / "checks/prediction_score.py")},
        "generator": {"path": "checks/draft_publish_prediction.py", "sha256": sha(Path(__file__).resolve())},
        "drunken_emu": {"note": "the parent of the registration commit, on branch claude/relaxed-ramanujan-bgj6za (PR #43)"},
        "parameters": {"budget": BUDGET, "budget_sensitivity": SENSITIVITY, "lookalike": 0.5, "p_basis": BASES,
                       "rank_ties": {"method": "not computed: no segment is comparable by duration (nobody keeps a clock), so Kendall's tau is not scored on this pass", "unstable_pairs": []}},
        "chain_check_command": f"bin/emu chain check {FIXTURE.relative_to(ROOT)} --json", "chain_check_json": check,
        "predictors": measured["states"], "segments": segs,
        "ranking": {"by": "load of one instance of the segment (ordinal only: not minutes, not a threshold)", "groups_longest_first": [g for _, g in sorted(groups.items())], "rank": rank,
                    "excluded_from_tau": [s["id"] for s in segs if not s["comparable_by_duration"]],
                    "baseline_by_step_count": {"steps": count, "rank": avg_ranks({k: float(v) for k, v in count.items()})}},
        "events": events,
        "hypothesis": {"id": "H-externalized", "claim": "inside the sheet nothing is held that the sheet shows: the goal is the main button in the dock, the numbers the chat gave are the file line and the foot, the written student's name is the line the sheet shows on the next open; so the held lists of the chains inside the sheet are empty or have one item, and B = 2 holds",
                       "falsified_if": ["the owner loses the goal, a number or the written student's name although the sheet displayed it", "a step inside the sheet is narrated as needing something kept in mind that the chain does not list"]},
        "scoring": {"script": "checks/prediction_score.py", "outcomes_schema": "emu-outcomes/1",
                    "coding": "from what the owner says in the chat unasked, a screenshot sent unasked, and the run's record if it is ever pasted: the transcriber codes each event using the event and observable columns only, writes the outcomes file, and only then runs the script; the p column is not read while coding. Nothing is requested from the owner.",
                    "outcome": {"1": "the observable condition is met by what the owner sent", "0": "the event's segment is shown (a record, a message about it) and the condition is not met", "null": "the segment is not shown: the event is not scored (most events, on this pass)"},
                    "brier": "mean over scored events of (p - o)^2, against the constant forecast at the mean p and against 0.5; also per basis and per segment",
                    "kendall": "not scored: no segment has a measured duration",
                    "onsets": "narrated losses within two steps of a predicted onset at B = 2 (none are predicted: every chain peaks at 2 slots), B = 3 and B = 4 as registered",
                    "p02be": "the observed rate of events whose steps carry a verifier finding against events whose steps carry none; unregistered frictions; false findings",
                    "owner_leaves": "nothing. The tool's own record (复制最近一次记录 in the sheet, kept on the phone) scores the events it shows if the owner or the coordinating session ever pastes it; the coordinating session reads such records by counts only"},
        "falsifiers": {"P-02be": {"claim": "a chain can pass by omission: the silence of the verifiers does not mean a step is smooth", "shown_on_this_pass_if": ["an unregistered friction sits at a step where no verifier fired", "a finding sits at a step the owner calls smooth"]},
                       "load model": {"claim": "the chains, written from the code, find where the owner is slowed", "falsified_if": ["the events at steps with a finding occur no more often than the events at steps without one, over at least 15 scored events"]},
                       "the publisher's own assumptions": {"claim": "the first real run reveals what the mock could not", "shown_if": ["I4, I5, T4, B1 or W4 occur: the real Canvas answered something the script did not expect"]},
                       "H-externalized": {"claim": "the sheet carries what the owner would otherwise hold (B = 2)", "falsified_if": ["the owner loses the goal, a number or the written student's name although the sheet displayed it"]}},
        "limits": ["written by the author of the publisher, of the fixture and of this generator, with no second reader, and after the first build had already been sent to the owner",
                   f"the weights are ordinal and uncalibrated (P-67a1); amounts are guesses; {sum(1 for e in E if e[7] == 'guess')} of the {len(E)} probabilities are guesses and {sum(1 for e in E if e[3] == 'smooth')} predict that nothing goes wrong",
                   "the loads are not comparable with the registration for 0.2.2: the held lists changed by a hypothesis (H-externalized), not only by the build",
                   "the sheet was measured on a mock Canvas in headless Chromium at 390x844 touch with this container's fonts, not on an iPhone, not on the real SpeedGrader, whose own controls may cover the 初稿 button; the drag was tested with real touch events and a mouse in Chromium, not in WebKit",
                   "the owner is ill, and this is a pass under that condition, which the model does not know about",
                   "most events can be scored only if the owner says something unasked: with nothing requested, many will stay unscored, which is the price of asking for nothing",
                   "if the owner ran any version before this registration was pushed, this registration is void for that run: the outcomes may be coded but are post hoc",
                   "S2 to S12 are conditional or optional chains: their events are scored only if the segment happens"],
    }


def md(pred: dict) -> str:
    a, ev = pred["artifact"], pred["events"]
    chk = {c["id"]: c for c in pred["chain_check_json"]["files"][0]["chains"]}
    top = sorted((e for e in ev if e["kind"] == "friction"), key=lambda e: -e["p"])[:5]
    n_basis = {b: sum(1 for e in ev if e["basis"] == b) for b in BASES}
    fix = json.loads((ROOT / pred["fixture"]["path"]).read_text(encoding="utf-8"))
    n_steps = sum(len(c["steps"]) for c in fix["chains"])
    findings = [(cid, f) for cid, c in chk.items() for f in c["findings"]]
    by_verifier: dict[str, int] = {}
    for _, f in findings:
        by_verifier[f["verifier"]] = by_verifier.get(f["verifier"], 0) + 1
    manual = sum(len(chk[c]["findings"]) for c in ("dp-manual-set", "dp-manual-post"))
    sheet_findings = [(cid, f) for cid, f in findings if cid not in ("dp-manual-set", "dp-manual-post", "dp-install-check")]
    m = json.loads((ROOT / pred["measured"]["path"]).read_text(encoding="utf-8"))
    out = [f"# Registered before the first run: where the draft publisher will be hard (speeds-kit {a['commit'][:7]}, publisher {a['version']}), second registration", "",
           "<!-- draft-publish-prediction: generated by checks/draft_publish_prediction.py, do not edit by hand -->", "",
           f"**Registered: the commit time of the commit that adds this file.** Drafted {pred['drafted']}. Nothing is scored. Nobody has used this flow on a phone.", "",
           "## What this replaces, and why",
           f"- The first registration of this flow (commit `{pred['supersedes']['commit'][:7]}`, 2026-10-12 09:41 UTC) was for speeds-kit `70f8ef6` (publisher 0.2.2): a build without the audit layer (A1 the rubric as its own step, A2 every student listed, A3 a record of every row before and after, A4 the foot repeated in the confirmation), at B = 3, with held lists that kept the goal and the chat's numbers in memory through the whole sheet, and it asked the owner for narration and screenshots. The owner's rules forbid the last (rule 2: the owner's share is the sign-in and one tap) and require the audit layer (rule 4). **It is void**; git keeps it.",
           "- Since then the two publishers were merged (speeds-kit `ab19308`, publisher 0.3.1, the file the owner holds), the rehearsal and the geometry became a committed tool (`python3 -m speedkit.rehearse`, rule 8) instead of scratch scripts, and the budget became B = 2, as the owner asked (\"算好 memory load\"; `theory/RECORD-THEORY.md` section 5).",
           "- Read and applied by hand where they could be, because PR #58 (`contrib/calendar-reader`, still a side branch) is not wired into `bin/emu`, was never run on today's layer, and its `echo` splits phrases on spaces and so cannot see a repeated Chinese phrase: `echo` (below), `wall`, `fold`, `aim`; `travel` has nothing to measure (the sheet has no colour key).",
           "- The owner was asked not to tap the write button before this registration was pushed. **If a run happened before the push, this registration is void for that run.**", "",
           "## What is registered",
           f"- The chains: `{pred['fixture']['path']}`: {len(fix['chains'])} chains, {n_steps} steps, B = {pred['parameters']['budget']} (sensitivity B = {', '.join(str(b) for b in pred['parameters']['budget_sensitivity'])}), provenance `designed`. Evidence in the steps' notes: `[declared]` is a judgment about what the screen says, `[guess]` is nothing the owner said, `[measured]` is a number of the measurement file.",
           "- **A hypothesis (H-externalized) the held lists rest on:** inside the sheet nothing is held that the sheet shows. The goal is the main button in the dock (`发布 57 位初稿`, `写入剩下的 56 位`), the numbers the chat gave are the file line and the foot, the written student's name is the line the sheet shows on the next open and the button's label `初稿·已试写` cues the goal after a reload. So inside the sheet the chains hold nothing or one item, and B = 2 holds. If the owner loses the goal, a number or the name although the sheet displayed it, the hypothesis is falsified. The loads are therefore **not comparable** with the registration for 0.2.2.",
           f"- {len(ev)} events with probabilities: {n_basis['measured']} measured, {n_basis['declared']} declared, {n_basis['carried-from-HW1']} carried from HW1, {n_basis['guess']} guessed; {sum(1 for e in ev if e['kind'] == 'smooth')} predict that nothing goes wrong.",
           "- Most likely frictions (top five): " + "; ".join(f"{e['event'].split(' (')[0]} ({e['id']}, {e['p']:.2f})" for e in top) + ".",
           "- Against: speeds-kit `" + a["commit"] + "`, `userscripts/draft-publish.user.js` sha256 `" + a["script_sha256"] + "` (" + str(a["script_lines"]) + " lines); the file the owner has is that script with the class's data in it, sha256 `" + a["delivered_file_sha256"] + "` (reproducible from that commit's template and the data).", "",
           "| Chain | Steps | Load | Peak slots | Findings | Rank by load |", "|---|---|---|---|---|---|"]
    for s in pred["segments"]:
        out.append(f"| `{s['id']}` ({s['name']}) | {s['steps']} | {s['load']:.2f} | {s['peak_slots']} | {len(chk[s['id']]['findings'])} | {pred['ranking']['rank'][s['id']]:g} |")
    out += ["", f"What the findings are: {len(findings)} in all (" + ", ".join(f"{n} {v}" for v, n in sorted(by_verifier.items())) + f"); {manual} are in Canvas's own Gradebook screens (the Manual route), {sum(1 for c, f in findings if c == 'dp-install-check')} in the install chain (the chat app's menu among look-alike lines, and the silence of the page while it loads), and {len(sheet_findings)} are a reload that loses the position in SpeedGrader (after the trial write, after the long write, and when the written student is looked for). {by_verifier.get('memory_budget', 0)} are memory findings at B = {pred['parameters']['budget']}; the largest working set of any chain is {max(s['peak_slots'] for s in pred['segments'])} slots. The friction predicted is not memory: it is first contact with the real Canvas (I4, I5, T4, B1, W4), SpeedGrader's own screens (L1, T5, I3), the owner's hesitation before an irreversible write (T3, W3, O1) and, in the audit, the length of what is shown (A2, A3, T2).", "",
            "## Measured on the artifact (`python3 -m speedkit.rehearse`: mock Canvas, headless Chromium, 390 x 844 touch, the 0.3.1 file)",
            f"- {sum(1 for l in m['lines'] if l['pass'])} of {len(m['lines'])} lines pass; the one that fails is the tool's own floor: right after the one-student trial the lists keep 39 % of the sheet (the floor is 40 %). 0.3.2 shortens that result line and fixes it; it was not sent to the owner.",
           "- The status line, the foot and the buttons are in view in every state, with every list opened. No tap target under 44 px; no text under 13 px.", "",
           "| state | sheet | scrolling part (visible / content) | dock | foot | the open student bar (starts at / tall) |", "|---|---|---|---|---|---|"]
    for s in m["states"]:
        fo = s.get("first_open")
        out.append(f"| {s['state']} | {s['sheet_h']} px | {s['scroll_visible_h']} / {s['scroll_content_h']} px | {s['dock_h']} px | {s['foot_h'] or '-'} | " + (f"{fo['top']} / {fo['height']} px" if fo else "-") + " |")
    out += ["",
            "## Reader cost (PR #58's five questions, by hand)",
            "- **echo**: on the first screen (Manual policy, the real data on the mock) two phrases are said twice verbatim, the rubric line (25 characters, in the rubric bar and in the foot) and the posting policy (18 characters, in a hint and in the foot), and the three counts are said twice in other words (`57 位可以写入` and `将写入 57 位学生`; `10 位机器没把握，暂缓` and `暂缓 10 位`; `2 位的文件核对不过` and `文件核对不过 2 位`). The foot repeats the whole count block; when the foot is shown, the block above it is what could go. Not changed in this build.",
           "- **wall**: the longest unbroken run is one opened student: 2173 px, 5.6 screens of the scrolling part.",
           "- **fold**: the first thing to act on, the main button, is in view in every state.",
           "- **aim**: the smallest target is 44 px; none is under.", "",
            "## What the owner leaves after the pass",
            "Nothing. No narration, no screenshots, no clock. What scores the events is what the owner says unasked, and the run's own record on the phone (the sheet's `复制最近一次记录`, kept for the last 10 runs) if it is ever pasted. Most events will therefore stay unscored; that is the price of asking for nothing.", "",
            "## Events", "", "| Id | Segment | Step | p | Basis | Event | Observable |", "|---|---|---|---|---|---|---|"]
    for e in ev:
        st = e["steps"][0]
        out.append(f"| {e['id']} | `{e['segment']}` | {st['step']} {st['op']} | {e['p']:.2f} | {e['basis']} | {e['event']} | {e['observable']} |")
    out += ["", "## Scoring", "`python3 checks/prediction_score.py docs/predictions/draft-publish-first-run.prediction.json OUTCOMES.json`: Brier over the scored events (against the constant forecast and against 0.5), per basis and per segment; onsets at B = 2, 3, 4; P-02be. Kendall's tau is not scored: no segment has a measured duration.", "",
            "## What would show the model wrong",
            "- H-externalized: the owner loses the goal, a number or the written student's name although the sheet displayed it.",
            "- Events at steps with a finding occur no more often than events at steps without one (over at least 15 scored events).",
            "- An unregistered friction at a step where no verifier fired, or a finding at a step the owner calls smooth (P-02be).",
            "- I4, I5, T4, B1 or W4 occur: the real Canvas answered something the script did not expect. That is not a flaw of the model; it is what the mock could not say, and it is the reason for the one-student trial.", "",
            "## Limits"] + [f"- {x}." for x in pred["limits"]] + [""]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    lines = Path(argv[0]).read_text().split()
    import time
    info = {"commit": lines[0], "script_sha256": lines[1], "file_sha256": lines[2], "lines": lines[3], "version": lines[4], "drafted": time.strftime("%Y-%m-%d %H:%M %Z")}
    pred = build(info)
    OUT_JSON.write_text(json.dumps(pred, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(md(pred), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}: {len(pred['events'])} events, {len(pred['segments'])} segments, {pred['chain_check_json']['findings']} findings")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
