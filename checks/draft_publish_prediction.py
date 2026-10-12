#!/usr/bin/env python3
"""
draft_publish_prediction.py -- the prediction registered BEFORE the owner's first run of the draft publisher
(speeds-kit userscripts/draft-publish.user.js, docs/DRAFT-PUBLISH.md), in the form checks/prediction_score.py scores.

Point: the publisher was built and sent to the owner without going through this kit. This is the late registration, for the build that
was the head when it was pushed (speeds-kit commit and sha256 below). Nothing is scored; nobody has used the flow on a phone. A change of the
script after the push is a NEW dated registration: do not edit this one (the pin test fails if the fixture changes).

    python3 checks/draft_publish_prediction.py BUILD.txt          # BUILD.txt: four lines: speeds-kit commit, script sha256, delivered-file sha256, script lines

Writes docs/predictions/draft-publish-first-run.prediction.json (schema emu-prediction/1) and .md. Reads checks/fixtures/chains/draft_publish_hw2.json,
runs `bin/emu chain check --json` on it (and at B = 2 and 4), and reads docs/predictions/draft-publish-first-run.measured.json (content-blind boxes
of the sheet on a mock Canvas, 390 x 844 touch). Stdlib only.
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

# id, short, name, comparable by duration?, why not
SEGMENTS = [
    ("dp-install-check", "S1", "install and first read", False, "starts when a person (the coordinating session) says the file is ready, and runs through the chat app, Files and Safari"),
    ("dp-trial-write", "S2", "one-student trial write", True, ""),
    ("dp-look-at-one", "S3", "look at the written student", True, ""),
    ("dp-write-rest", "S4", "write the rest", True, ""),
    ("dp-failure-retry", "S5", "a run with failures, and the retry", False, "happens only if a run ends with failures"),
    ("dp-interrupted-run", "S6", "coming back after an interrupted write", False, "happens only if the page dies in the middle of the long write"),
    ("dp-manual-set", "S7", "Manual route: set the policy", False, "optional: only if the owner takes the Manual route; Canvas's own screens"),
    ("dp-manual-post", "S8", "Manual route: post the grades", False, "optional: only if the owner takes the Manual route; Canvas's own screens"),
]

# id, chain, step, kind, event, observable, p, basis, rests_on
E = [
    ("I1", "dp-install-check", 6, "friction", "the file does not reach the Userscripts folder on the first try (wrong folder, unsure which, or saved again)", "the narration says the file went to another folder, had to be moved or saved again, or that the folder was a worry", 0.25, "guess", "HW1 A4 says the remembered folder costs nothing, for another destination; nothing on the save sheet says which folder is right"),
    ("I2", "dp-install-check", 10, "friction", "after the reload the owner is unsure whether the script is installed, and looks for or waits for the button", "the narration says they did not know whether it had worked, looked for the button or reloaded again", 0.30, "declared", "progress finding at step 10: nothing on the page says the script is there until the 初稿 button appears"),
    ("I3", "dp-install-check", 11, "friction", "the owner cannot find the 初稿 button on the SpeedGrader page (another control covers it, or it is mistaken for one)", "the narration or a screenshot shows a search for the button, or it hidden", 0.15, "guess", "its place (top right, 72 px down) was measured on the mock page, not on the real SpeedGrader"),
    ("I4", "dp-install-check", 13, "friction", "the first read ends in a red line instead of the counts (a refusal, a lost login, an answer of Canvas the script did not expect)", "a screenshot or the narration shows a red line in the sheet at the first check", 0.20, "guess", "the real Canvas has not been tried; the guards (points total, grading type, group, anonymous, moderated) and the field names are assumptions"),
    ("I5", "dp-install-check", 14, "friction", "the sheet says that more than half of the students' files do not match (the file ids mean something else than the script assumes)", "the sheet shows the line about the file check and its button", 0.20, "guess", "the middle number of Canvas's file names is assumed to be the attachment id (about 80% sure)"),
    ("I6", "dp-install-check", 15, "friction", "the counts differ from the numbers in the chat and the owner stops to work out why", "the narration says the numbers were not what the chat said, or they compared and puzzled", 0.35, "guess", "skipped, absent and unchecked counts depend on the real course (graded students, a missing-submission zero, the two emailed students)"),
    ("I7", "dp-install-check", 14, "smooth", "the counts and the main button are on one screen, with no scrolling", "a screenshot of the sheet shows the counts and the main button together", 0.90, "measured", "docs/predictions/draft-publish-first-run.measured.json: the main button is in view in every state, the footer does not scroll"),
    ("T1", "dp-trial-write", 1, "friction", "the owner does not see why only one student is written the first time", "the narration says they did not understand the one-student step, or tapped expecting all", 0.20, "declared", "the posting line and the button label ('先试写 1 位') say it; the owner has no habit for it yet"),
    ("T2", "dp-trial-write", 3, "friction", "the owner does not read the first student's preview to the end (it needs a scroll) or skips it", "the narration says they did not read it, or a screenshot shows it unscrolled at the tap", 0.40, "declared", "measured: the scrolling part of the sheet is 1.2 screens with the clipped preview (3.9 before the clip); a reader taps when the button is in view"),
    ("T3", "dp-trial-write", 6, "friction", "the owner hesitates at the confirmation (reads it twice, or cancels and starts again)", "the narration says they hesitated or cancelled", 0.30, "guess", "an irreversible write that the student sees at once; the dialog is native text"),
    ("T4", "dp-trial-write", 7, "friction", "the trial write ends with a red line instead of 试写完成", "a screenshot or the narration shows a failure after the trial", 0.30, "guess", "the first real write on the real Canvas: permissions, the rubric assessment form, the rate limit"),
    ("T5", "dp-trial-write", 11, "friction", "after the reload the owner cannot find the written student in SpeedGrader", "the narration says they searched for the student", 0.30, "guess", "the sheet lists in the order of the names; SpeedGrader's own order is assumed to be the same"),
    ("T6", "dp-trial-write", 9, "smooth", "the owner takes the result line as the check and does not look for a proof elsewhere", "the narration does not mention verifying the write by other means than looking at the student", 0.70, "declared", "the line says the write was read back and matched; the verifiers find no gap there"),
    ("L1", "dp-look-at-one", 2, "friction", "SpeedGrader does not show the written comments at first (the rubric is collapsed or the comments need a tap)", "the narration says the comments were not visible at first", 0.35, "guess", "how SpeedGrader shows free-form criterion comments on a phone is not known"),
    ("L2", "dp-look-at-one", 4, "friction", "the owner finds a deduction or a comment they think is wrong in the first student", "the narration says something looked wrong", 0.40, "guess", "an unreviewed machine draft; HW1's first pass had errors"),
    ("L3", "dp-look-at-one", 3, "friction", "the comment layout (tags such as [Q5b-gen], long keys) looks odd or too long to the owner", "the narration says the comments looked strange or too long", 0.25, "guess", "the layout is TapGrade's, which the owner knows; keys are long"),
    ("L4", "dp-look-at-one", 4, "friction", "the owner stops after the look and does not write the rest in the same sitting", "the narration or the chat says they stopped", 0.20, "guess", "depends on what they see in L2"),
    ("W1", "dp-write-rest", 1, "friction", "the owner does not find the way back to the pending write (the button reads 初稿·已试写)", "the narration says they did not know what to do next", 0.15, "declared", "the label and the line 'you wrote only <name> last time' are meant to bring the goal back"),
    ("W2", "dp-write-rest", 4, "friction", "the counts after the trial surprise the owner (the written student counts as already the draft)", "the narration says the numbers were not what they expected", 0.15, "guess", "the count of 'already the draft' is 1 at this point"),
    ("W3", "dp-write-rest", 8, "friction", "the owner hesitates at the second confirmation", "the narration says they hesitated", 0.15, "guess", "after looking at one student the decision is made; the dialog is the same kind"),
    ("W4", "dp-write-rest", 9, "friction", "the long write ends with one or more failed students", "the footer line shows a failure count above 0", 0.45, "guess", "the first run at scale on the real Canvas: rate limits, permission quirks, a student with no enrolment"),
    ("W5", "dp-write-rest", 9, "friction", "the page is interrupted during the long write (the phone locks, another app, a reload)", "the narration says the write was interrupted or the button read 初稿·未完", 0.25, "guess", "1 to 3 minutes on a phone; Safari may suspend a tab that is not in view"),
    ("W6", "dp-write-rest", 12, "friction", "the owner compares the final numbers with the chat and finds a mismatch they have to explain", "the narration says the totals did not match what the chat said", 0.30, "guess", "59 was the plan; skipped, unchecked and held counts depend on the real course"),
    ("W7", "dp-write-rest", 10, "smooth", "the final line is understood at the first reading", "the narration does not say they re-read it", 0.80, "declared", "one line with three numbers and the read-back statement"),
    ("F1", "dp-failure-retry", 2, "friction", "the owner does not understand Canvas's own error text for a failed student", "the narration says the message was unclear (only if a run had failures)", 0.50, "declared", "the message is Canvas's, in English or a status code; it says why, not what to do"),
    ("F2", "dp-failure-retry", 9, "smooth", "one retry clears all the failures", "the second run ends with 0 failed (only if a run had failures)", 0.60, "guess", "failures of a first run are often a rate limit or a timeout"),
    ("R1", "dp-interrupted-run", 3, "smooth", "after an interrupted write the owner understands the red line and writes the rest without asking", "the narration says they understood and continued (only if a write was interrupted)", 0.75, "declared", "the sheet opens by itself and says the last run did not finish"),
    ("M1", "dp-manual-set", 4, "friction", "the owner needs more than one try to find Grade Posting Policy in the Gradebook", "the narration says the setting was hard to find (only if the route is taken)", 0.50, "guess", "Canvas's screens; not narrated by this owner"),
    ("M2", "dp-manual-post", 4, "friction", "the owner needs more than one try to find Post grades in the Gradebook", "the narration says it was hard to find (only if the route is taken)", 0.50, "guess", "Canvas's screens; not narrated by this owner"),
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
    onsets = {b: {cid: sorted(f["step"] for f in c["findings"] if f["verifier"] == "memory_budget") for cid, c in {c["id"]: c for c in chain_check(b)["files"][0]["chains"]}.items()} for b in (2, 3, 4)}
    segs = []
    for cid, short, name, comparable, why in SEGMENTS:
        c = by_id[cid]
        segs.append({"id": cid, "short": short, "name": name, "comparable_by_duration": comparable, "not_comparable_because": why, "steps": c["steps"], "load": c["load"],
                     "peak_slots": c["peak_slots"], "predicted_loss_onsets_at_B": {str(b): onsets[b][cid] for b in (2, 3, 4)}})
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
        "title": "The first run of the draft publisher on the owner's phone: HW2's machine drafts into Canvas (speeds-kit userscripts/draft-publish.user.js 0.2.2)",
        "registered_by": "the commit that adds this version of this file: its commit time is the registration time; it was pushed before the owner was told the flow was registered",
        "drafted": info["drafted"], "spec": "theory/RECORD-THEORY.md section 8; issue #32, test point E5 (a second pass); the owner's remark of 2026-10-12 that the newest issues and PRs were left hanging",
        "artifact": {"repository": "speeds-kit", "commit": info["commit"], "script": "userscripts/draft-publish.user.js", "script_sha256": info["script_sha256"], "script_lines": int(info["lines"]),
                     "version": "0.2.2", "delivered_file_sha256": info["file_sha256"], "delivered_file": "rutgers-fa26-463-regression/hw2/drafts/hw2-drafts.user.js (private: it holds student grades; not in the repository)",
                     "mock_canvas": "tests/tapgrade/mock_canvas.py of the same commit", "docs_read": "docs/DRAFT-PUBLISH.md and the script itself"},
        "fixture": {"path": str(FIXTURE.relative_to(ROOT)), "sha256": sha(FIXTURE)},
        "measured": {"path": str(MEASURED.relative_to(ROOT)), "sha256": sha(MEASURED), "tool": "measure_publisher.py in the contributing session's scratch (content-blind: boxes and sizes only), 390x844 touch, headless Chromium, mock Canvas, the real HW2 draft data rebound to the mock", "states": [s["state"] for s in measured["states"]]},
        "scorer": {"path": "checks/prediction_score.py", "sha256": sha(ROOT / "checks/prediction_score.py")},
        "generator": {"path": "checks/draft_publish_prediction.py", "sha256": sha(Path(__file__).resolve())},
        "drunken_emu": {"note": "the parent of the registration commit, on branch claude/relaxed-ramanujan-bgj6za (PR #43)"},
        "parameters": {"budget": 3, "budget_sensitivity": [2, 4], "lookalike": 0.5, "p_basis": BASES,
                       "rank_ties": {"method": "not computed: fewer than 4 segments are comparable by duration, so Kendall's tau is not scored on this pass", "unstable_pairs": []}},
        "chain_check_command": f"bin/emu chain check {FIXTURE.relative_to(ROOT)} --json", "chain_check_json": check,
        "predictors": measured["states"], "segments": segs,
        "ranking": {"by": "load of one instance of the segment (ordinal only: not minutes, not a threshold)", "groups_longest_first": [g for _, g in sorted(groups.items())], "rank": rank,
                    "excluded_from_tau": [s["id"] for s in segs if not s["comparable_by_duration"]],
                    "baseline_by_step_count": {"steps": count, "rank": avg_ranks({k: float(v) for k, v in count.items()})}},
        "events": events,
        "scoring": {"script": "checks/prediction_score.py", "outcomes_schema": "emu-outcomes/1",
                    "coding": "the transcriber codes each event from the narration and the screenshots using the event and observable columns only, writes the outcomes file, and only then runs the script; the p column is not read while coding",
                    "outcome": {"1": "the observable condition is met by the narration or the screenshots", "0": "the event's segment is narrated or shown and the condition is not met", "null": "the segment is neither narrated nor shown: the event is not scored (conditional chains: S5 to S8)"},
                    "brier": "mean over scored events of (p - o)^2, against the constant forecast at the mean p and against 0.5; also per basis and per segment",
                    "kendall": "not scored unless 4 comparable segments have a measured duration; with S2 to S4 only, it is not",
                    "onsets": "narrated losses within two steps of a predicted onset at B = 3 (none are predicted at B = 3: every chain peaks at 3 slots), B = 2 and B = 4 as registered",
                    "p02be": "the observed rate of events whose steps carry a verifier finding against events whose steps carry none; unregistered frictions; false findings",
                    "owner_leaves": "if you can: a few lines written right after, in your own words, of what slowed you, what you re-read and what surprised you; and screenshots with the clock. Nothing else. If you cannot, say so: the screenshots alone score the events they show."},
        "falsifiers": {"P-02be": {"claim": "a chain can pass by omission: the silence of the verifiers does not mean a step is smooth", "shown_on_this_pass_if": ["an unregistered friction sits at a step where no verifier fired", "a finding sits at a step the narration calls smooth"]},
                       "load model": {"claim": "the chains, written from the code, find where the owner is slowed", "falsified_if": ["the events at steps with a finding occur no more often than the events at steps without one, over at least 15 scored events"]},
                       "the publisher's own assumptions": {"claim": "the first real run reveals what the mock could not", "shown_if": ["I4, I5, T4 or W4 occur: the real Canvas answered something the script did not expect"]}},
        "limits": ["written by the author of the publisher, of the fixture and of this generator, with no second reader, and after the first build had already been sent to the owner",
                   f"the weights are ordinal and uncalibrated (P-67a1); amounts are guesses; {sum(1 for e in E if e[7] == 'guess')} of the {len(E)} probabilities are guesses and {sum(1 for e in E if e[3] == 'smooth')} predict that nothing goes wrong",
                   "the sheet was measured on a mock Canvas in headless Chromium at 390x844 touch with this container's fonts, not on an iPhone, not on the real SpeedGrader, whose own controls may cover the 初稿 button",
                   "the owner is ill, and this is a pass under that condition, which the model does not know about",
                   "if the owner ran any version before this registration was pushed, this registration is void for that run: the outcomes may be coded but are post hoc",
                   "S5 to S8 are conditional chains: their events are scored only if the segment happens"],
    }


def md(pred: dict) -> str:
    a, ev = pred["artifact"], pred["events"]
    by = {s["id"]: s for s in pred["segments"]}
    chk = {c["id"]: c for c in pred["chain_check_json"]["files"][0]["chains"]}
    top = sorted((e for e in ev if e["kind"] == "friction"), key=lambda e: -e["p"])[:5]
    n_basis = {b: sum(1 for e in ev if e["basis"] == b) for b in BASES}
    out = [f"# Registered before the first run: where the draft publisher will be hard (speeds-kit {a['commit'][:7]}, publisher {a['version']})", "",
           "<!-- draft-publish-prediction: generated by checks/draft_publish_prediction.py, do not edit by hand -->", "",
           f"**Registered: the commit time of the commit that adds this file.** Drafted {pred['drafted']}. Nothing is scored. Nobody has used this flow on a phone.", "",
           "## Why this exists, and why it is late",
           "- The publisher writes the machine's first draft of a whole class into Canvas. The owner is ill and will run it on a phone. It is exactly the kind of flow this kit exists for, and it was built and sent without going through the kit. The owner pointed that out on 2026-10-12.",
           "- Since then: the phone audit (`blind_audit.py`) ran, a content-blind measurement of the sheet found three faults it does not count (list bars 18 px high, text down to 12 px, the main button leaving the screen), the designed chains went through `bin/emu chain check` (18 findings on the first build, 13 now), and the script changed because of them (0.2.0 to 0.2.2). Those changes and why are in speeds-kit `CHANGELOG.md` and `docs/DRAFT-PUBLISH.md`.",
           "- The owner was asked not to tap the write button before this registration was pushed. **If a run happened before the push, this registration is void for that run.**", "",
           "## What is registered",
           f"- The chains: `{pred['fixture']['path']}`: 8 chains, 74 steps, B = 3, provenance `designed`. Evidence in the steps' notes: `[declared]` is a judgment about what the screen says, `[guess]` is nothing the owner said, `[measured]` is a number of the measurement file.",
           f"- {len(ev)} events with probabilities: {n_basis['measured']} measured, {n_basis['declared']} declared, {n_basis['carried-from-HW1']} carried from HW1, {n_basis['guess']} guessed; {sum(1 for e in ev if e['kind'] == 'smooth')} predict that nothing goes wrong.",
           "- Most likely frictions (top five): " + "; ".join(f"{e['event'].split(' (')[0]} ({e['id']}, {e['p']:.2f})" for e in top) + ".",
           "- Against: speeds-kit `" + a["commit"] + "`, `userscripts/draft-publish.user.js` sha256 `" + a["script_sha256"] + "` (" + str(a["script_lines"]) + " lines); the file the owner has is that script with the class's data in it, sha256 `" + a["delivered_file_sha256"] + "`.", "",
           "| Chain | Steps | Load | Peak slots | Findings | Rank by load |", "|---|---|---|---|---|---|"]
    for s in pred["segments"]:
        out.append(f"| `{s['id']}` ({s['name']}) | {s['steps']} | {s['load']:.2f} | {s['peak_slots']} | {len(chk[s['id']]['findings'])} | {pred['ranking']['rank'][s['id']]:g} |")
    out += ["", "What the findings are: 13 in all; 8 are in Canvas's own Gradebook screens (the Manual route), 1 is the chat app's menu, and 4 are a reload that closes the sheet or the silence of a loading page. Memory is not predicted to fail anywhere at B = 3 (every chain peaks at 3 slots); at B = 2 it fails at the steps listed in the JSON. The friction predicted is not memory: it is first contact with the real Canvas (I4, I5, T4, W4), SpeedGrader's own screens (L1, T5, I3) and the owner's hesitation before an irreversible write (T3, W3).", "",
            "## Measured on the artifact (mock Canvas, headless Chromium, 390 x 844 touch)",
            "- The sheet's counts and the main button are on one screen; the main button is in view in every state, also with every list opened (the footer does not scroll).",
            "- No tap target under 44 px (the list bars were 18 px in the first build); no text under 13 px (12 px before).",
            "- The scrolling part of the sheet is 1.2 screens in the one-student trial with the clipped preview (3.9 before the clip), 1.8 with every list opened.", "",
            "## What the owner leaves after the pass",
            "If you can: a few lines written right after, in your own words, of what slowed you, what you re-read and what surprised you, and screenshots with the clock. If you cannot, say so; the screenshots alone score the events they show. Nothing else. Do not read the events table first: it would prime the lines.", "",
            "## Events", "", "| Id | Segment | Step | p | Basis | Event | Observable |", "|---|---|---|---|---|---|---|"]
    for e in ev:
        st = e["steps"][0]
        out.append(f"| {e['id']} | `{e['segment']}` | {st['step']} {st['op']} | {e['p']:.2f} | {e['basis']} | {e['event']} | {e['observable']} |")
    out += ["", "## Scoring", "`python3 checks/prediction_score.py docs/predictions/draft-publish-first-run.prediction.json OUTCOMES.json`: Brier over the scored events (against the constant forecast and against 0.5), per basis and per segment; onsets at B = 2, 3, 4; P-02be. Kendall's tau is not scored unless four comparable segments have a measured duration, which this flow does not give (S2 to S4 only).", "",
            "## What would show the model wrong",
            "- Events at steps with a finding occur no more often than events at steps without one (over at least 15 scored events).",
            "- An unregistered friction at a step where no verifier fired, or a finding at a step narrated as smooth (P-02be).",
            "- I4, I5, T4 or W4 occur: the real Canvas answered something the script did not expect. That is not a flaw of the model; it is what the mock could not say, and it is the reason for the one-student trial.", "",
            "## Limits"] + [f"- {x}." for x in pred["limits"]] + [""]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    lines = Path(argv[0]).read_text().split()
    import time
    info = {"commit": lines[0], "script_sha256": lines[1], "file_sha256": lines[2], "lines": lines[3], "drafted": time.strftime("%Y-%m-%d %H:%M %Z")}
    pred = build(info)
    OUT_JSON.write_text(json.dumps(pred, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(md(pred), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}: {len(pred['events'])} events, {len(pred['segments'])} segments, {pred['chain_check_json']['findings']} findings")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
