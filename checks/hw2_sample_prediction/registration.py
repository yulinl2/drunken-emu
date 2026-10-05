"""The registration as data: docs/predictions/hw2-sample-pass.prediction.json, computed from the fixture, the two measured files, the inputs and
the first-draft baseline.  `build` is a pure function of those and of the parent commit (the commit the chain numbers were computed at)."""
from __future__ import annotations

import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

from . import changes, events as E
from .cites import EXAMPLE_ITEMS, Cites
from .inputs import REPO, INPUTS_PATH

sys.path.insert(0, str(REPO / "checks"))
import chain as C            # noqa: E402
import chain_load as L       # noqa: E402
import chain_verifiers as V  # noqa: E402

FIXTURE = "checks/fixtures/chains/tapgrade_0_6_7_sample_pass.json"
PRED = "docs/predictions/hw2-sample-pass.prediction.json"
MD = "docs/predictions/hw2-sample-pass.md"
MEASURED = "docs/predictions/hw2-sample-pass.measured.json"
MEASURED_EXAMPLE = "docs/predictions/hw2-sample-pass.measured-example-bank.json"
SCORER = "checks/prediction_score.py"
MEASURE_TOOL = "checks/measure_sample_predictors.py"
PACKAGE = "checks/hw2_sample_prediction"
SEED, DRAWS, SCALE, FLIP = 20261005, 2000, (0.5, 1.5), 0.05


def sha(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def generator_shas(repo: Path = REPO) -> dict:
    return {p.name: sha(p) for p in sorted((Path(repo) / PACKAGE).glob("*.py"))}


def cli(repo: Path, *args: str) -> str:
    p = subprocess.run(["bash", "bin/emu", "chain", "check", FIXTURE, *args], cwd=str(repo), capture_output=True, text=True, timeout=120)
    if p.returncode not in (0, 1):
        raise RuntimeError(f"bin/emu chain check failed ({p.returncode}): {p.stderr.strip()}")
    return p.stdout


def used_at_problems(predictors: list[dict], steps_of: dict) -> list[str]:
    """`used_at` of the predictor table names steps (S3:9; S4:6, 7; S6:2-7): every one must exist in the fixture"""
    short = {f"S{i + 1}": s[1] for i, s in enumerate(E.SEG)}
    out = []
    for r in predictors:
        text = re.sub(r"\([^)]*\)", "", r["used_at"])
        if text.strip() == "all chains":
            continue
        for part in re.finditer(r"(S\d):\s*([\d,\s-]+)", text):
            cid = E.PREFIX + short[part.group(1)]
            for tok in re.split(r"\s*,\s*", part.group(2).strip().rstrip(";").strip()):
                a, _, b = tok.partition("-")
                if not a.strip().isdigit():
                    continue
                lo, hi = int(a), int(b or a)
                if not (1 <= lo <= hi <= steps_of[cid]):
                    out.append(f"{r['family']} / {r['what'][:40]}: {part.group(1)}:{tok} is not a step of {cid} ({steps_of[cid]} steps)")
    return out


def build(repo: Path, MJ: dict, AJ: dict, inputs: dict, parent: str, drafted: str | None = None) -> dict:
    repo = Path(repo)
    doc = C.load(repo / FIXTURE)
    chains = {c["id"]: c for c in doc["chains"]}
    report = cli(repo).rstrip("\n").split("\n")
    check_json = json.loads(cli(repo, "--json"))
    by_id = {c["id"]: c for c in check_json["files"][0]["chains"]}
    over = {b: {cid: json.loads(cli(repo, "--json", "--budget", str(b)))["files"][0]["chains"][i]["over_budget_steps"] for i, cid in enumerate(chains)} for b in (2, 3, 4)}

    # ---- the ranking, with ties from the weights' uncertainty -----------------------------------------------------------------------------
    ids = [E.PREFIX + s[1] for s in E.SEG]
    rnd = random.Random(SEED)
    wins = {(a, b): 0 for a in ids for b in ids if a != b}
    for _ in range(DRAWS):
        w = {k: v * rnd.uniform(*SCALE) for k, v in L.WEIGHTS.items()}
        ld = {i: L.chain_load(C.blind(chains[i]), weights=w)["load"] for i in ids}
        for a in ids:
            for b in ids:
                if a != b and ld[a] > ld[b]:
                    wins[(a, b)] += 1
    stable = {(a, b): wins[(a, b)] / DRAWS >= 1 - FLIP for a in ids for b in ids if a != b}      # a beats b in at least 95% of the draws
    base_load = {i: by_id[i]["load"] for i in ids}
    order = sorted(ids, key=lambda i: -base_load[i])
    groups = []                                              # consecutive segments that are not stably ordered share a rank
    for i in order:
        if groups and not stable[(groups[-1][-1], i)] and not stable[(i, groups[-1][-1])]:
            groups[-1].append(i)
        else:
            groups.append([i])
    rank, pos = {}, 1
    for g in groups:
        for i in g:
            rank[i] = pos + (len(g) - 1) / 2
        pos += len(g)
    unstable = sorted((a, b, wins[(a, b)] / DRAWS) for a in ids for b in ids if a < b and not stable[(a, b)] and not stable[(b, a)])

    def avg_ranks(values):                                   # longest/biggest first; equal values share the average rank
        order_ = sorted(values, key=lambda k: -values[k])
        out, i = {}, 0
        while i < len(order_):
            j = i
            while j + 1 < len(order_) and values[order_[j + 1]] == values[order_[i]]:
                j += 1
            for k in order_[i:j + 1]:
                out[k] = (i + 1 + j + 1) / 2
            i = j + 1
        return out

    step_rank = avg_ranks({i: len(chains[i]["steps"]) for i in ids})

    # ---- events: every step reference is checked against the fixture ----------------------------------------------------------------------
    evs, covered = [], set()
    for e in E.events(MJ, AJ, inputs):
        refs = []
        for suffix, step in e["steps"]:
            cid = E.PREFIX + suffix
            assert cid in chains, (e["id"], cid)
            stp = chains[cid]["steps"][step - 1]
            refs.append({"chain": cid, "step": step, "op": stp["op"]})
            covered.add((cid, step))
        assert e["basis"] in E.ALLOWED_BASES and 0 <= e["p"] <= 1, e["id"]
        kind = "path" if e["id"] == "Q2" else "fine" if e["p"] <= 0.10 else "friction"       # fine: the registered belief is that this goes right (p is the chance it does not)
        evs.append({"id": e["id"], "segment": E.PREFIX + e["steps"][0][0], "kind": kind, "steps": refs, "event": e["event"], "observable": e["observable"], "p": e["p"], "basis": e["basis"], "rests_on": e["rests_on"]})
    ids_ = [e["id"] for e in evs]
    assert len(ids_) == len(set(ids_)), "an event id is used twice"
    findings = [[c["id"], f["step"], f["verifier"]] for c in check_json["files"][0]["chains"] for f in c["findings"]]
    missing = [f for f in findings if (f[0], f[1]) not in covered]
    assert not missing, f"findings with no event: {missing}"
    predictors = E.predictors(MJ, AJ, inputs)
    bad = used_at_problems(predictors, {cid: len(c["steps"]) for cid, c in chains.items()})
    assert not bad, "the predictor table names steps that are not there:\n  " + "\n  ".join(bad)

    # ---- segments ---------------------------------------------------------------------------------------------------------------------------
    from .chains import build as build_chains                # the dataflow table is the one the fixture was derived from
    _, flows = build_chains(MJ, AJ, inputs)
    segments, seg_numbers = [], []
    for short, suffix, name, comparable, why in E.SEG:
        cid = E.PREFIX + suffix
        ch = chains[cid]
        segments.append({"id": cid, "short": short, "name": name, "comparable_by_duration": comparable, "not_comparable_because": why if not comparable else "",
                         "noted_limit": why if comparable and why else "", "steps": len(ch["steps"]), "load": base_load[cid], "rank": rank[cid],
                         "predicted_loss_onsets_at_B": {str(b): over[b][cid] for b in (2, 3, 4)}, "dataflow": flows[cid]})
        seg_numbers.append({"id": cid, "steps": len(ch["steps"]), "load": base_load[cid], "peak_slots": by_id[cid]["peak_slots"], "findings": len(by_id[cid]["findings"]), "rank": rank[cid],
                            "over_budget": {str(b): over[b][cid] for b in (2, 3, 4)}})

    n_pairs = lambda r: len(r) * (len(r) - 1) // 2
    comp = [E.PREFIX + x[1] for x in E.SEG if x[3]]
    differ = sum(1 for a in comp for b in comp if a < b and (((rank[a] > rank[b]) - (rank[a] < rank[b])) != ((step_rank[a] > step_rank[b]) - (step_rank[a] < step_rank[b]))))
    sk, script = inputs["speeds_kit"], inputs["speeds_kit"]["script"]
    cite = Cites(inputs["citations"])
    M = MJ["sample"]
    raw_doc = json.loads((repo / FIXTURE).read_text(encoding="utf-8"))       # the file as written: the loader fills defaults in, which the first draft's record does not have
    ch_changes = changes.compute(repo, inputs, MJ, AJ, raw_doc, seg_numbers, findings, [[a, b, r] for a, b, r in unstable], groups, evs)
    reg = {
        "schema": "emu-prediction/1", "id": "hw2-sample-pass",
        "title": "The HW2 blind sample pass on the owner's phone (TapGrade 0.6.7 sample mode): where it will be hard, how much, in which order",
        "registered_by": "the commit that adds this file: its commit time is the registration (theory/RECORD-THEORY.md section 8, step 2)",
        "drafted": drafted or inputs["drafted"],
        "spec": "theory/RECORD-THEORY.md section 8; issue #32, test point E5",
        "artifact": {"repository": "speeds-kit", "commit": sk["commit"], "checkout_head": sk["checkout_head"], "script": script["path"], "script_sha256": script["sha256"], "script_lines": script["lines"],
                     "version": script["version"], "build": script["build"],
                     "mock_canvas": {"path": sk["mock_canvas"]["path"], "sha256": sk["mock_canvas"]["sha256"]},
                     "docs_read": "docs/TAPGRADE.md (Blind sample mode, and the lines cited from its Install, Data from the kit and correction sections) and docs/HW2-HW3-RUNBOOK.md (steps 7 and 8, and the line cited from its sample-size section) at that commit"},
        "inputs": {"path": INPUTS_PATH, "sha256": sha(repo / INPUTS_PATH), "what": "the commit, the sha256 of every file read from the speeds-kit checkout, and the place of every code line a note cites"},
        "fixture": {"path": FIXTURE, "sha256": sha(repo / FIXTURE)},
        "measured": {"path": MEASURED, "sha256": sha(repo / MEASURED), "bank": MJ["sample"]["bank"], "tool": MEASURE_TOOL, "tool_sha256": sha(repo / MEASURE_TOOL),
                     "tool_command": "python3 checks/measure_sample_predictors.py userscripts/tapgrade.user.js MOCK_URL --bank large"},
        "measured_example_bank": {"path": MEASURED_EXAMPLE, "sha256": sha(repo / MEASURED_EXAMPLE), "bank": AJ["sample"]["bank"],
                                  "why": f"the same measurement with a bank of the size the runbook's example output gives ({EXAMPLE_ITEMS} bank items, {cite('rbStderr')}: {EXAMPLE_ITEMS} chips in all); the real size of HW2's bank is unknown",
                                  "tool_command": "python3 checks/measure_sample_predictors.py userscripts/tapgrade.user.js MOCK_URL --bank example"},
        "scorer": {"path": SCORER, "sha256": sha(repo / SCORER)},
        "generator": {"path": PACKAGE + "/", "sha256": generator_shas(repo),
                      "what": "the code that wrote the fixture, this file and the .md from the inputs, the measured files and the first-draft baseline: `python3 -m checks.hw2_sample_prediction build --check` rebuilds them in memory and compares"},
        "drunken_emu": {"commit": parent, "note": "the parent of the registration commit, on branch wt/e5; an integration that rewrites commits changes this hash, the fixture's sha256 does not move"},
        "parameters": {
            "budget": 3, "budget_sensitivity": [2, 4], "lookalike": V.LOOKALIKE, "weights": L.WEIGHTS, "verifiers": list(V.VERIFIERS),
            "weights_source": "checks/chain_load.py WEIGHTS at the drunken-emu commit named above (unchanged since the branch point 6116f64)",
            "rank_ties": {"method": "each load weight scaled by a uniform draw in [0.5, 1.5]; two segments are tied when neither is above the other in at least 95% of the draws", "draws": DRAWS, "seed": SEED,
                          "scale": list(SCALE), "flip_above": FLIP, "unstable_pairs": [{"a": a, "b": b, "a_above_b_share": r} for a, b, r in unstable]},
            "p_basis": list(E.ALLOWED_BASES)},
        "chain_check_command": f"bin/emu chain check {FIXTURE} --json",
        "chain_check_report": report, "chain_check_json": check_json,
        "over_budget_steps": {str(b): over[b] for b in (2, 3, 4)},
        "predictors": predictors,
        "segments": segments,
        "ranking": {"by": "load of one instance of the segment (ordinal only: not minutes, not a threshold)", "groups_longest_first": groups,
                    "rank": rank, "excluded_from_tau": [E.PREFIX + s[1] for s in E.SEG if not s[3]],
                    "baseline_by_step_count": {"note": f"the simplest competitor, fixed now: rank the segments by the number of steps the chain lists (no weights). P-67a1 asks whether the weights add anything over counting steps. It orders {differ} of the {n_pairs(comp)} comparable pairs differently from the load, so this pass tells the two apart only there",
                                               "steps": {i: len(chains[i]["steps"]) for i in ids}, "rank": step_rank}},
        "events": evs,
        "changes_since_first_draft": ch_changes["first_draft"],
        "changes_since_replaced_registration": ch_changes.get("replaced"),
        "scoring": {
            "script": SCORER, "outcomes_schema": "emu-outcomes/1",
            "coding": "the transcriber codes each event from the narration and the screenshots using the event and observable columns only, writes the outcomes file, and only then runs the script; the p column is not read while coding",
            "outcome": {"1": "the observable condition is met by the narration or the screenshots", "0": "the event's segment is narrated or shown and the condition is not met", "null": "the segment is neither narrated nor shown: the event is not scored"},
            "brier": {"formula": "mean over scored events of (p - o)^2", "references": ["the constant forecast at the mean p of the scored events", "the constant forecast 0.5 (score 0.25)"], "also_reported": ["per basis, with how often p was on the right side of 0.5", "per segment"]},
            "kendall": {"variant": "tau-b", "predicted": "ranking.rank (average ranks; a lower rank is a longer segment)", "measured": "per segment, the median over its dated instances of the minutes from its first event to its last, read from clocks (resolution one minute)",
                        "ties": "measured minutes are rounded to whole minutes; equal means tied", "min_segments": 4, "excluded": [E.PREFIX + s[1] for s in E.SEG if not s[3]],
                        "p": "exact one-sided permutation p over the orders of the measured values", "baseline": "ranking.baseline_by_step_count, scored the same way",
                        "reversal": "a pair the weights order stably (not in parameters.rank_ties.unstable_pairs) that is measured the other way by at least 1 minute and 25% of the longer one"},
            "durations": {"sources": ["the status-bar clock of a screenshot", "the foot's 'Recorded HH:MM' of a recorded pair", "the History screen's save times", "chat message times"],
                          "instances": {"pair": "between two consecutive saves with no reload, lock or break between them", "pair-reload": "a pair interval that contains a narrated reload", "pair-lock": "from the unlock to the next save",
                                        "queue": "from the first page after the load toast to the first pair header after Next pair", "export": "from the tap on Check to the toast 'Copied N picks as JSON'", "handback": "from the toast to the message in the chat",
                                        "break": "a gap over 10 minutes between two consecutive saves is a break and is not an instance; the lock interval is removed"}},
            "onsets": {"window_steps": 2, "B": "scored at B=3 as the primary and, as they were registered, at B=2 and B=4; none is chosen after the pass",
                       "hit": "a loss (forgot, lost the goal, went back to re-read) is narrated at a moment the transcriber maps, from the chains' step targets and before reading p, to a step within 2 steps of a predicted onset of the same chain",
                       "chance": "for each narrated loss, the share of that chain's steps that lie within 2 steps of a predicted onset (5 of 9 in the pair chain at B=3)",
                       "false_alarm": "a loss narrated in a chain with no predicted onset at that B"},
            "p02be": "the observed rate of events whose steps carry a verifier finding against events whose steps carry none; unregistered frictions (a friction no event describes) and whether their step is silent; false findings (a finding whose step is narrated as smooth)",
            "owner_leaves": "a narration written right after, in their own words (as on 2026-10-03), and screenshots with clock times; nothing else"},
        "falsifiers": {
            "P-67a1": {"claim": "the chain load, with ordinal weights, orders segments of one task by their duration",
                       "falsified_on_this_pass_if": ["tau-b of the load ranking is 0 or below over the comparable segments that have a measured duration (4 are needed to score)",
                                                    "any pair the weights order stably is measured the other way by at least 1 minute and 25% (kendall.reversals)",
                                                    "tau-b of the step-count baseline is at least that of the load: the weights add nothing over counting steps"],
                       "limit": f"the two rankings differ on {differ} of {n_pairs(comp)} comparable pairs, so the third test can only fail or pass on those"},
            "P-02be": {"claim": "a chain can pass by omission: the silence of the verifiers does not mean a step is smooth",
                       "shown_on_this_pass_if": ["an unregistered friction sits at a step where no verifier fired (p02be.unregistered_at_a_silent_step above 0)", "a finding sits at a step the narration calls smooth (p02be.false_findings above 0)",
                                                 "events at steps with no finding occur at least as often as events at steps with one (p02be: the rate without a finding is not below the rate with one)"],
                       "falsified_on_this_pass_if": ["none of the three holds over at least 15 scored events"]},
            "memory model (theory section 10)": {"claim": "pressure above B marks where goals are lost",
                                                 "falsified_on_this_pass_if": ["at B=3 the narrated losses in the chains with a predicted onset hit within two steps no more often than chance gives (onsets.3: hits_within_two_steps at or below hits_expected_by_chance)"],
                                                 "also_reported": "the same at B=2 and B=4; B is not chosen from them"},
            "measured predictors (theory section 10)": {"claim": "what is measured on the artifact says what people perceive",
                                                        "falsified_on_this_pass_if": ["for events with basis 'measured', p was on the wrong side of 0.5 more often than on the right side (brier.by_basis.measured: agree below half of n)"]}},
        "limits": ["written by the same author as the builder of the chain layer, the fixture and the measurement script: not independent",
                   "the load weights are ordinal and uncalibrated (P-67a1); amounts, parts per pair and taps per pair are guesses",
                   "the pass has not happened: every p is a belief, none is fitted", "the artifact was measured on a mock Canvas in headless Chromium at 390x844 touch with this container's fonts, not on an iPhone, not on a real Canvas, with an invented sample",
                   f"the snapshot is speeds-kit {sk['commit'][:7]}, the sample fixer's follow-up included; a further review round may change the sample mode again, and what it changes is not predicted here: if this registration is already pushed when it does, the new code is a new dated registration",
                   "HW1's outcomes are base rates only (basis carried-from-HW1): one pass by one person",
                   f"the real bank's size is unknown: the measured layout is for an invented bank of {M['chips']} chips ({M['chips'] / M['questions']:.0f} per question), and a bank of the runbook's example size ({EXAMPLE_ITEMS} bank items, {cite('rbStderr')}: {EXAMPLE_ITEMS} chips in all) was measured too; events P1, P2, P8 and P12 state a p between the two",
                   "+-2 steps covers 5 of the 9 steps of the pair chain: a loss placed at random hits more often than not", "silence in a narration is ambiguous: an event coded 0 may be a difficulty that was not mentioned",
                   "the transcriber is the coordinating session, which has read this file: coding blind to p is a rule, not a guarantee",
                   "one pass by one person: the protocol accumulates across tasks, and each new account is held out until scored (theory section 8)"],
    }
    return reg


def dump(reg: dict) -> str:
    return json.dumps(reg, indent=1, ensure_ascii=False) + "\n"
