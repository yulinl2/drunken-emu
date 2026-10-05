"""checks/test_prediction.py -- the registered prediction for the HW2 blind sample pass is pinned to its fixture, and its scorer works.

docs/predictions/hw2-sample-pass.md (and .prediction.json) is a pre-registration (theory/RECORD-THEORY.md section 8): written before the
pass, committed, then scored. A registration that can be edited afterwards registers nothing, so this file fails when the fixture, the
measured file or the numbers move. No browser, no model, no network (CI job `chains`).

  1. the pin: the fixture, the measured files, the measurement script, the scorer, the inputs, the first-draft baseline and the generator
     have the registered sha256; the checker, run on the fixture, gives the registered load, peak, over-budget steps and findings per
     chain, and the registered report text; and the generator, run on the committed inputs and measurements, makes exactly the committed
     fixture, JSON and text (a hand edit of a registered file is found, and so is a change of the generator);
  2. the registered JSON is valid: p in [0, 1], every step id exists (and names the op the fixture has there), the ranking covers every
     segment, every finding has an event, the rank order is the load order up to the weights' ties (recomputed);
  3. the dataflow table derives the chains' `held` lists; every step note cites its evidence, and each line, entry id and measured key
     it cites exists; every line of the code or of the docs that a note or an event cites is a line the inputs file found by anchor, and a
     sentence about the runbook or docs/TAPGRADE.md cites the line it rests on;
  4. must-fire: a property changed in a copy of the fixture is detected, a tampered registration is detected; an anchor that matches
     twice or not at all stops the build; a difference since the first draft that no change explains stops it;
  5. the scorer (checks/prediction_score.py) on toy data, with the numbers worked out by hand, and its refusals;
  6. the one command (rebuild): what it refuses, that it never writes in the checkout it reads;
  7. the docs name the files, and the tables of the .md are the JSON's;
  8. the second registration (supersede): the rule that sets P1, P2 and P8, the judgments that name the value they replaced, the baselines that keep an earlier
     registration as data, and the stale statement that no note may make.
"""
import copy
import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import chain as C                      # noqa: E402
import chain_check as K                # noqa: E402
import chain_load as L                 # noqa: E402
import chain_verifiers as V            # noqa: E402
import prediction_score as P           # noqa: E402
from checks.hw2_sample_prediction import changes as CH, cites as CT, inputs as IN, rebuild as RB, registration as RG  # noqa: E402

KIT = HERE.parent
PRED = KIT / "docs" / "predictions" / "hw2-sample-pass.prediction.json"
MD = KIT / "docs" / "predictions" / "hw2-sample-pass.md"
INPUTS_FILE = KIT / IN.INPUTS_PATH
BASE = KIT / CH.BASELINE_DIR
REG = json.loads(PRED.read_text(encoding="utf-8"))
INPUTS = json.loads(INPUTS_FILE.read_text(encoding="utf-8"))
# the comparisons the registration makes: with the first draft, and with the registration it replaces (when there is one)
COMPARISONS = {k: REG[k] for k in ("changes_since_first_draft", "changes_since_replaced_registration") if REG.get(k)}
CHANGES_OF = {"changes_since_first_draft": CH.CHANGES, "changes_since_replaced_registration": CH.CHANGES_SINCE_REPLACED}
FIXTURE = KIT / REG["fixture"]["path"]
PFX = "tapgrade-0.6.7-sample-"
MSG = "the fixture changed after registration: write a NEW dated registration, do not edit this one"
DRIFT = ("the checker gives other numbers for the registered fixture (its weights, loader or a verifier moved): "
         "write a NEW dated registration, do not edit this one")


def sha(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_checker(path, budget=None):
    """what `bin/emu chain check --json` prints per chain, from the checker's own functions"""
    doc = C.load(path)
    return [K._json_chain(V.run_chain(c, budget, V.LOOKALIKE)) for c in doc["chains"]]


def registration_problems(fixture_path, reg) -> tuple[list[str], list[str]]:
    """(problems with the file itself, problems with what the checker says about it)"""
    file_problems, number_problems = [], []
    if sha(fixture_path) != reg["fixture"]["sha256"]:
        file_problems.append(f"sha256 of the fixture is {sha(fixture_path)[:12]}..., registered {reg['fixture']['sha256'][:12]}...")
    registered = {c["id"]: c for c in reg["chain_check_json"]["files"][0]["chains"]}
    try:
        now = {c["id"]: c for c in run_checker(fixture_path)}
    except C.ChainError as e:
        return file_problems + [f"the file no longer loads: {e}"], number_problems
    if set(now) != set(registered):
        number_problems.append(f"chains {sorted(set(now) ^ set(registered))} are not in both")
    for cid in sorted(set(now) & set(registered)):
        for key in ("budget", "steps", "peak_slots", "peak_held", "over_budget_steps", "counts", "terms", "load", "findings"):
            if now[cid][key] != registered[cid][key]:
                number_problems.append(f"{cid}: {key} is {now[cid][key]!r}, registered {registered[cid][key]!r}")
    for b in (2, 4):
        reg_over = reg["over_budget_steps"][str(b)]
        got = {c["id"]: c["over_budget_steps"] for c in run_checker(fixture_path, b)}
        for cid in sorted(set(got) & set(reg_over)):
            if got[cid] != reg_over[cid]:
                number_problems.append(f"{cid}: over-budget steps at B={b} are {got[cid]}, registered {reg_over[cid]}")
    return file_problems, number_problems


def params_problems(reg) -> list[str]:
    p, out = reg["parameters"], []
    if L.WEIGHTS != p["weights"]:
        out.append(f"weights are {L.WEIGHTS}, registered {p['weights']}")
    if V.LOOKALIKE != p["lookalike"]:
        out.append(f"look-alike line is {V.LOOKALIKE}, registered {p['lookalike']}")
    if list(V.VERIFIERS) != p["verifiers"]:
        out.append(f"verifiers are {list(V.VERIFIERS)}, registered {p['verifiers']}")
    return out


@pytest.fixture(scope="module")
def fx():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def chains():
    return {c["id"]: c for c in C.load(FIXTURE)["chains"]}


# --- 1. the pin -----------------------------------------------------------------------------------------------------------------------
def test_the_fixture_is_the_registered_one():
    file_problems, _ = registration_problems(FIXTURE, REG)
    assert not file_problems, MSG + "\n  " + "\n  ".join(file_problems)


def test_the_checker_gives_the_registered_numbers():
    file_problems, number_problems = registration_problems(FIXTURE, REG)
    assert not number_problems, (MSG if file_problems else DRIFT) + "\n  " + "\n  ".join(number_problems)


def test_the_checkers_parameters_are_the_registered_ones():
    problems = params_problems(REG)
    assert not problems, DRIFT + "\n  " + "\n  ".join(problems)


def test_the_cli_prints_what_the_registration_holds():
    """`bin/emu chain check` on the fixture: the JSON and the text report, exactly as registered (exit 1: the fixture has findings)"""
    rel = REG["fixture"]["path"]
    emu = lambda *a: subprocess.run(["bash", str(KIT / "bin" / "emu"), "chain", "check", rel, *a], capture_output=True, text=True, cwd=str(KIT), timeout=60)
    j = emu("--json")
    assert j.returncode == 1, j.stderr
    assert json.loads(j.stdout) == REG["chain_check_json"], MSG
    t = emu()
    assert t.returncode == 1
    assert t.stdout.rstrip("\n").split("\n") == REG["chain_check_report"], MSG


def test_the_measured_file_and_the_tools_are_the_registered_ones():
    m = REG["measured"]
    assert sha(KIT / m["path"]) == m["sha256"], "the measured file changed after registration: write a NEW dated registration, do not edit this one"
    assert sha(KIT / m["tool"]) == m["tool_sha256"], "the measurement script changed after registration: write a NEW dated registration"
    assert sha(KIT / REG["scorer"]["path"]) == REG["scorer"]["sha256"], "the scorer changed after registration: write a NEW dated registration"
    meas = json.loads((KIT / m["path"]).read_text(encoding="utf-8"))
    assert meas["schema"] == "emu-sample-predictors/1" and meas["errors"] == [] and meas["page_errors"] == []
    assert meas["script"]["sha256"] == REG["artifact"]["script_sha256"]
    assert meas["script"]["path"] == "userscripts/tapgrade.user.js", "the path recorded is the script's place in speeds-kit, not where a copy happened to be"
    assert meas["script"]["version"] == REG["artifact"]["version"] and REG["artifact"]["commit"] == INPUTS["speeds_kit"]["commit"]
    assert set(meas["predictors"]) == {"window", "primary_action", "chips", "feedback_ms", "view_stability", "loading", "first_contact", "interruption", "two_pages", "export"}
    assert meas["sample"]["bank"] == m["bank"] == "large"
    alt = REG["measured_example_bank"]
    assert sha(KIT / alt["path"]) == alt["sha256"], "the example-bank measurement changed after registration: write a NEW dated registration, do not edit this one"
    meas2 = json.loads((KIT / alt["path"]).read_text(encoding="utf-8"))
    assert meas2["schema"] == "emu-sample-predictors/1" and meas2["errors"] == [] and meas2["page_errors"] == [] and meas2["sample"]["bank"] == alt["bank"] == "example"
    assert meas2["script"]["sha256"] == meas["script"]["sha256"], "both measurements are of the same script"
    assert meas2["sample"]["chips"] == 31 and meas["sample"]["chips"] > 100


def test_the_inputs_and_the_first_draft_baseline_are_the_registered_ones():
    assert sha(INPUTS_FILE) == REG["inputs"]["sha256"], "the inputs file changed after registration: write a NEW dated registration, do not edit this one"
    sk = INPUTS["speeds_kit"]
    assert re.fullmatch(r"[0-9a-f]{40}", sk["commit"]) and sk["script"]["sha256"] == REG["artifact"]["script_sha256"] and sk["script"]["lines"] == REG["artifact"]["script_lines"]
    assert sk["mock_canvas"]["sha256"] == REG["artifact"]["mock_canvas"]["sha256"] and set(sk["read"]) == {"speedkit/tapgrade.py", "speedkit/picks.py", "docs/TAPGRADE.md", "docs/HW2-HW3-RUNBOOK.md"}
    assert INPUTS["drafted"] == REG["drafted"]
    for key, comparison in COMPARISONS.items():
        base = comparison["baseline"]
        assert set(base["sha256"]) == set(CH.BASELINE_FILES)
        for name, h in base["sha256"].items():
            assert sha(KIT / base["path"] / name) == h, f"{name} of {base['path']} changed after registration: write a NEW dated registration"


def test_the_generator_is_the_registered_one():
    assert RG.generator_shas(KIT) == REG["generator"]["sha256"], "the generator changed after registration: write a NEW dated registration, do not edit this one"


def test_the_committed_files_are_what_the_generator_makes():
    """the fixture, the registration JSON, its text and the OPERATION-CHAINS section, rebuilt in memory from the inputs, the measured files and the baseline"""
    problems = RB.check_all()
    assert not problems, MSG + "\n  " + "\n  ".join(problems)


def test_the_registration_names_the_commit_it_was_computed_at():
    c = REG["drunken_emu"]["commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", c)
    git = subprocess.run(["git", "cat-file", "-t", c], capture_output=True, text=True, cwd=str(KIT))
    if git.returncode == 0:                            # a shallow clone, or history rewritten by an integration, may not hold it: then only its shape is checked
        assert git.stdout.strip() == "commit"


# --- 2. the registered JSON is valid --------------------------------------------------------------------------------------------------------
def test_the_registration_has_its_parts():
    assert REG["schema"] == "emu-prediction/1" and REG["id"] == "hw2-sample-pass"
    for key in ("artifact", "inputs", "fixture", "measured", "measured_example_bank", "scorer", "generator", "drunken_emu", "parameters", "chain_check_report", "chain_check_json", "over_budget_steps",
                "predictors", "segments", "ranking", "events", "changes_since_first_draft", "changes_since_replaced_registration", "scoring", "falsifiers", "limits"):
        assert key in REG, key
    assert re.fullmatch(r"[0-9a-f]{64}", REG["fixture"]["sha256"]) and re.fullmatch(r"[0-9a-f]{64}", REG["artifact"]["script_sha256"])
    assert REG["parameters"]["budget"] == 3 and REG["parameters"]["budget_sensitivity"] == [2, 4]
    assert {p["label"] for p in REG["predictors"]} == {"measured", "declared", "carried-from-HW1", "guess"}
    assert set(REG["falsifiers"]) >= {"P-67a1", "P-02be"}
    assert len(REG["limits"]) >= 6


def test_probabilities_are_probabilities_and_step_ids_exist(chains):
    ids = [e["id"] for e in REG["events"]]
    assert len(ids) == len(set(ids)) and len(ids) >= 30
    for e in REG["events"]:
        assert isinstance(e["p"], (int, float)) and not isinstance(e["p"], bool) and 0 <= e["p"] <= 1, e["id"]
        assert e["basis"] in REG["parameters"]["p_basis"], e["id"]
        assert e["kind"] in ("friction", "path", "fine"), e["id"]
        assert e["kind"] != "fine" or e["p"] <= 0.10, e["id"]
        assert e["event"] and e["observable"] and e["rests_on"], e["id"]
        assert e["steps"], e["id"]
        assert e["segment"] == e["steps"][0]["chain"], e["id"]
        for r in e["steps"]:
            assert r["chain"] in chains, (e["id"], r)
            steps = chains[r["chain"]]["steps"]
            assert isinstance(r["step"], int) and 1 <= r["step"] <= len(steps), (e["id"], r)
            assert steps[r["step"] - 1]["op"] == r["op"], (e["id"], r)


def test_every_basis_and_kind_is_used_and_nothing_goes_wrong_is_predicted_somewhere():
    assert {e["basis"] for e in REG["events"]} == set(REG["parameters"]["p_basis"])
    assert {e["kind"] for e in REG["events"]} == {"friction", "path", "fine"}


def test_the_ranking_covers_every_segment(chains):
    seg_ids = [s["id"] for s in REG["segments"]]
    assert seg_ids == list(chains), "the registered segments are the fixture's chains, in its order"
    rk = REG["ranking"]
    assert set(rk["rank"]) == set(seg_ids) == set(rk["baseline_by_step_count"]["rank"])
    n = len(seg_ids)
    for table in (rk["rank"], rk["baseline_by_step_count"]["rank"]):
        assert sum(table.values()) == n * (n + 1) / 2 and all(1 <= v <= n for v in table.values())
    assert sorted(i for g in rk["groups_longest_first"] for i in g) == sorted(seg_ids)
    assert set(rk["excluded_from_tau"]) <= set(seg_ids) and len(seg_ids) - len(rk["excluded_from_tau"]) >= 5
    for s in REG["segments"]:
        assert s["rank"] == rk["rank"][s["id"]]
        assert s["comparable_by_duration"] == (s["id"] not in rk["excluded_from_tau"])
        assert s["comparable_by_duration"] or s["not_comparable_because"]


def test_the_rank_order_is_the_load_order_up_to_the_weights_ties(chains):
    """recomputed: each weight scaled by a uniform draw, the same seed; a pair is a tie when neither is above in 95% of the draws"""
    rt = REG["parameters"]["rank_ties"]
    ids = list(chains)
    rnd = random.Random(rt["seed"])
    wins = {(a, b): 0 for a in ids for b in ids if a != b}
    for _ in range(rt["draws"]):
        w = {k: v * rnd.uniform(*rt["scale"]) for k, v in L.WEIGHTS.items()}
        ld = {i: L.chain_load(C.blind(chains[i]), weights=w)["load"] for i in ids}
        for a in ids:
            for b in ids:
                if a != b and ld[a] > ld[b]:
                    wins[(a, b)] += 1
    unstable = sorted((a, b, wins[(a, b)] / rt["draws"]) for a in ids for b in ids
                      if a < b and wins[(a, b)] / rt["draws"] < 1 - rt["flip_above"] and wins[(b, a)] / rt["draws"] < 1 - rt["flip_above"])
    assert [(u["a"], u["b"], u["a_above_b_share"]) for u in rt["unstable_pairs"]] == unstable
    load = {s["id"]: s["load"] for s in REG["segments"]}
    tied = {frozenset((u["a"], u["b"])) for u in rt["unstable_pairs"]}
    rank = REG["ranking"]["rank"]
    for a in ids:
        for b in ids:
            if a < b:
                if frozenset((a, b)) in tied:
                    assert rank[a] == rank[b], (a, b)
                else:
                    assert (rank[a] < rank[b]) == (load[a] > load[b]) and rank[a] != rank[b], (a, b)


def test_every_finding_has_an_event_and_the_segment_numbers_are_the_checkers(chains):
    covered = {(r["chain"], r["step"]) for e in REG["events"] for r in e["steps"]}
    by_id = {c["id"]: c for c in REG["chain_check_json"]["files"][0]["chains"]}
    for cid, c in by_id.items():
        for f in c["findings"]:
            assert (cid, f["step"]) in covered, f"finding {cid} step {f['step']} {f['verifier']} has no event"
    for s in REG["segments"]:
        c = by_id[s["id"]]
        assert (s["steps"], s["load"]) == (len(chains[s["id"]]["steps"]), c["load"])
        assert s["predicted_loss_onsets_at_B"] == {str(b): REG["over_budget_steps"][str(b)][s["id"]] for b in (2, 3, 4)}
    assert REG["over_budget_steps"]["3"] == {c["id"]: c["over_budget_steps"] for c in by_id.values()}


def test_the_order_of_the_comparable_segments_does_not_depend_on_the_guessed_amounts(fx):
    """parts per pair, chip taps and chips per part are guesses: the order reload > lock > pair > export, hand-back > queue holds across them (install moves, and is not scored)"""
    def loads(parts, taps, chips):
        d = copy.deepcopy(fx)
        for c in d["chains"]:
            for i, st in enumerate(c["steps"], 1):
                if c["id"] == PFX + "pair-reload":
                    if i in (4, 5, 6, 7):
                        st["times"] = max(1, parts // 2)
                    if i in (13, 14, 15, 16):
                        st["times"] = parts
                    if i == 8:
                        st["times"] = max(1, taps - 1)
                    if i == 17:
                        st["times"] = taps
                elif c["id"] in (PFX + "pair", PFX + "pair-lock"):
                    if st["op"] in ("READ", "SCAN", "DISCRIMINATE") and st.get("times") == 4:
                        st["times"] = parts
                    if st["op"] == "TAP" and st.get("times") == 3:
                        st["times"] = taps
                if st["op"] == "DISCRIMINATE":
                    st["amount"] = chips
        return {c["id"][len(PFX):]: L.chain_load(C.blind(c))["load"] for c in C.parse(d)["chains"]}

    for parts, taps, chips in ((4, 3, 3.4), (3, 2, 2.5), (2, 2, 1.8), (2, 1, 1.8), (6, 4, 3.4)):
        ld = loads(parts, taps, chips)
        assert ld["pair-reload"] > ld["pair-lock"] > ld["pair"] > max(ld["export"], ld["handback"]) and min(ld["export"], ld["handback"]) > ld["queue"], (parts, taps, chips, ld)
    assert loads(4, 3, 3.4)["install"] < loads(4, 3, 3.4)["pair"] and loads(2, 2, 1.8)["install"] > loads(2, 2, 1.8)["pair"], "install is the one segment that moves"


# --- 3. dataflow, evidence ------------------------------------------------------------------------------------------------------------
def test_the_dataflow_table_derives_the_held_lists(fx):
    """held(step s) = the items produced before s and last needed at or after s (theory section 5): the chains' `held` are derived, not typed"""
    for s, ch in zip(REG["segments"], fx["chains"]):
        assert s["id"] == ch["id"]
        for d in s["dataflow"]:
            assert d["produced_at"] >= 0 and all(d["produced_at"] < n <= s["steps"] for n in d["needed_at"]), (s["id"], d["item"])
        for i, st in enumerate(ch["steps"], 1):
            want = [d["item"] for d in s["dataflow"] if d["produced_at"] < i <= max(d["needed_at"])]
            assert st.get("held", []) == want, (s["id"], i)


def test_the_peak_is_where_the_dataflow_says(fx):
    """the pressure point of the registration: the chip decision holds two items and needs two, in every pair chain; nothing else is over B"""
    raw = {c["id"]: c for c in fx["chains"]}
    over = REG["over_budget_steps"]["3"]
    for cid, steps in over.items():
        for n in steps:
            st = raw[cid]["steps"][n - 1]
            assert st["op"] == "DISCRIMINATE" and len(st["held"]) == 2, (cid, n)
    assert {cid for cid, steps in over.items() if steps} == {PFX + "pair", PFX + "pair-reload", PFX + "pair-lock"}


EVIDENCE = re.compile(r"userscripts/tapgrade\.user\.js:\d+|docs/[A-Za-z0-9_./-]+|HW1 [A-Z]\d?[a-z]?(?![A-Za-z0-9])|\[measured: |\[carried: unstated\]|\[guess\]|\[declared|speedkit/[a-z_]+\.py:\d+")


def test_every_step_note_cites_its_evidence(fx):
    for ch in fx["chains"]:
        for i, st in enumerate(ch["steps"], 1):
            assert st.get("note") and EVIDENCE.search(st["note"]), f"{ch['id']} step {i} ({st['op']}) cites nothing: a code line, a doc, an HW1 entry id, [measured: ...], [declared ...], [carried: unstated] or [guess]"


FILE_CITE = re.compile(r"((?:userscripts|speedkit|docs)/[A-Za-z0-9_.-]+\.(?:js|py|md)):(\d+)(?:-(\d+))?")
DOC_MENTION = re.compile(r"runbook|docs/(?:TAPGRADE|HW2-HW3-RUNBOOK)\.md", re.I)
DOC_LINE = re.compile(r"docs/(?:TAPGRADE|HW2-HW3-RUNBOOK)\.md:\d+")


def file_cites_problems(text, where):
    """every `file:A-B` in a text (the snapshot's script, its python, its docs) must be a place the inputs file found by anchor"""
    known = {(c["file"], tuple(c["lines"])) for c in INPUTS["citations"].values()}
    top = REG["artifact"]["script_lines"]
    out = []
    for m in FILE_CITE.finditer(text):
        a, b = int(m.group(2)), int(m.group(3) or m.group(2))
        if (m.group(1), (a, b)) not in known:
            out.append(f"{where}: {m.group(0)} is not a line the inputs file found by anchor (a typed number?)")
        if m.group(1) == "userscripts/tapgrade.user.js" and not 1 <= a <= b <= top:
            out.append(f"{where}: line {m.group(0)} is not in a {top}-line file")
    return out


def test_cited_lines_entries_and_keys_exist(fx):
    meas = json.loads((KIT / REG["measured"]["path"]).read_text(encoding="utf-8"))["predictors"]
    hw1 = {json.loads(l)["id"] for l in (KIT / "docs/evidence/hw1-correction-2026-10-03/transcription.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}

    def resolves(path):
        cur = meas
        for part in path.split("."):
            if not (isinstance(cur, dict) and part in cur):
                return False
            cur = cur[part]
        return True

    problems = []
    for ch in fx["chains"]:
        for i, st in enumerate(ch["steps"], 1):
            note, where = st["note"], f"{ch['id']} step {i}"
            problems += file_cites_problems(note, where)
            for m in re.finditer(r"HW1 ([A-Z]\d?[a-z]?)(?![A-Za-z0-9])", note):
                assert m.group(1) in hw1, f"{where}: HW1 entry {m.group(1)} does not exist"
            for m in re.finditer(r"\[measured: ([^\]]+)\]", note):
                for key in re.split(r"\s*(?:,|/)\s*", m.group(1)):
                    assert resolves(key.strip()), f"{where}: measured key {key!r} is not in the measured file"
    for e in REG["events"]:
        problems += file_cites_problems(e["rests_on"], f"event {e['id']}")
    assert not problems, "\n".join(problems)


def test_a_sentence_about_the_docs_cites_the_line_it_rests_on(fx):
    """a note or an event that speaks of the runbook or docs/TAPGRADE.md carries a line of them, found by anchor (cites.py): the anchor's pattern holds the words the sentence relies on,
    so a snapshot whose docs say something else stops the build instead of leaving a sentence that is no longer true"""
    texts = [(f"{ch['id']} step {i}", st["note"]) for ch in fx["chains"] for i, st in enumerate(ch["steps"], 1)] + [(f"event {e['id']}", e["rests_on"]) for e in REG["events"]]
    texts += [(f"{ch['id']} setup", ch["setup"]) for ch in fx["chains"]] + [(f"{ch['id']} notes", ch["notes"]) for ch in fx["chains"]]
    texts += [(f"limit {i}", x) for i, x in enumerate(REG["limits"], 1)] + [("measured_example_bank.why", REG["measured_example_bank"]["why"])]
    texts += [(f"{s['id']} dataflow {d['item']}", d["produced_on"] + " " + d["needed_on"]) for s in REG["segments"] for d in s["dataflow"]]
    md = MD.read_text(encoding="utf-8")
    point = md[md.index("## The point"): md.index("| Segment | Steps")]
    bank = md[md.index("### 3b."): md.index("## 4. Predicted loss onsets")]
    texts += [(f"the md, The point: {l[:50]}", l) for l in point.splitlines() if l.startswith("- ")] + [(f"the md, 3b: {l[:50]}", l) for l in bank.splitlines() if l and not l.startswith("|")]
    for where, text in texts:
        if DOC_MENTION.search(text):
            assert DOC_LINE.search(text), f"{where} speaks of the docs and cites no line of them (docs/HW2-HW3-RUNBOOK.md:N or docs/TAPGRADE.md:N, from an anchor of cites.py)"
    cited = {c["file"] for c in INPUTS["citations"].values()}
    assert {CT.RUNBOOK, CT.TAPGRADE_MD, CT.SCRIPT, CT.TAPGRADE_PY, CT.PICKS_PY} == cited


def test_a_quote_of_the_stale_runbook_line_names_the_commit_whose_runbook_said_it():
    """the runbooks at ca80695 and cac0dc8 said "Grade, then the Sample tab"; the one at cec1bba names the route.  A text that quotes the old line must say whose it was"""
    stale = "Grade, then the Sample tab"
    fx_text = FIXTURE.read_text(encoding="utf-8")
    texts = {"the md": MD.read_text(encoding="utf-8"), "the JSON": PRED.read_text(encoding="utf-8").replace('\\"', '"'), "the fixture": fx_text.replace('\\"', '"')}
    for name, text in texts.items():
        for m in re.finditer(re.escape(stale), text):
            assert re.search(r"ca80695|cac0dc8", text[max(0, m.start() - 240): m.start()]), f"{name} quotes {stale!r} with no commit before it: {text[max(0, m.start() - 160): m.end() + 40]!r}"
    assert 'runbook says "Grade, then the Sample tab"' not in texts["the md"].replace("The runbook says", "the runbook says"), "the sentence this test was written for"


def test_the_provenance_is_honest(fx):
    p = fx["provenance"]
    assert p["source"] == "designed" and p["date"] == INPUTS["drafted"][:10]
    assert "not from anyone using it" in p["note"] and "BEFORE" in p["note"]
    assert REG["artifact"]["script_sha256"] in p["who"] and INPUTS["speeds_kit"]["commit"] in p["who"]
    assert "[carried: unstated]" in p["note"] and "[guess]" in p["note"]


def test_no_student_names_or_real_ids_in_the_new_files():
    """the repository is public: the sample's students are invented, Canvas ids in the measured file are the mock's 90001..."""
    text = "\n".join((KIT / p).read_text(encoding="utf-8") for p in (REG["fixture"]["path"], REG["measured"]["path"], REG["measured_example_bank"]["path"], "docs/predictions/hw2-sample-pass.md", "docs/predictions/hw2-sample-pass.prediction.json",
                                                              IN.INPUTS_PATH, *(f"{CH.BASELINE_DIR}/{n}" for n in CH.BASELINE_FILES)))
    for m in re.finditer(r"\b(?:student_id|uid|user_id)\D{0,6}(\d{5,})", text):
        assert m.group(1).startswith("9000"), f"an id that is not the mock's: {m.group(1)}"
    assert not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[a-z]{2,}", text), "an e-mail address in a public file"


# --- 3b. citations by anchor ----------------------------------------------------------------------------------------------------------
TOY_SCRIPT = "line one\n  function a(x) {\n    return 1;\n  }\n  const B = 2;\n"


def toy_anchors(monkeypatch):
    monkeypatch.setattr(CT, "ANCHORS", {"a": (CT.SCRIPT, r"^  function a\(", CT.FUNC_END, 1), "b": (CT.SCRIPT, r"^  const B = ", None, 1)})


def test_an_anchor_finds_its_lines(monkeypatch):
    toy_anchors(monkeypatch)
    table = CT.resolve({CT.SCRIPT: TOY_SCRIPT})
    assert table["a"]["lines"] == [2, 4] and table["b"]["lines"] == [5, 5] and table["a"]["text"] == "function a(x) {"
    cite = CT.Cites(table)
    assert cite("a") == f"{CT.SCRIPT}:2-4" and cite("b") == f"{CT.SCRIPT}:5"
    assert CT.verify(table, {CT.SCRIPT: TOY_SCRIPT}) == []


def test_an_anchor_that_matches_twice_or_not_at_all_stops_the_build(monkeypatch):
    toy_anchors(monkeypatch)
    with pytest.raises(CT.AnchorError, match="matches 2 lines"):
        CT.resolve({CT.SCRIPT: TOY_SCRIPT + "  const B = 3;\n"})
    with pytest.raises(CT.AnchorError, match="matches 0 lines"):
        CT.resolve({CT.SCRIPT: "nothing here\n"})


def test_a_moved_or_rewritten_line_is_reported(monkeypatch):
    toy_anchors(monkeypatch)
    table = CT.resolve({CT.SCRIPT: TOY_SCRIPT})
    problems = CT.verify(table, {CT.SCRIPT: "a new first line\n" + TOY_SCRIPT})
    assert len(problems) == 2 and all("no longer reads" in x for x in problems)
    assert any("no recorded citation" in x for x in CT.verify({"a": table["a"]}, {CT.SCRIPT: TOY_SCRIPT}))


def test_the_inputs_hold_a_citation_for_every_anchor():
    assert set(INPUTS["citations"]) == set(CT.ANCHORS)
    top = INPUTS["speeds_kit"]["script"]["lines"]
    for key, c in INPUTS["citations"].items():
        a, b = c["lines"]
        assert 1 <= a <= b and (c["file"] != CT.SCRIPT or b <= top), key


def test_the_numbers_typed_from_the_docs_are_in_their_anchors():
    """a number the text takes from the docs (cites.py) is also in the pattern of the anchor that finds its line, so a snapshot whose docs say another number stops the build"""
    stderr, klass = CT.ANCHORS["rbStderr"][1], CT.ANCHORS["rbClass"][1]
    assert f"{CT.EXAMPLE_QUESTIONS} questions" in stderr and f"on {CT.SAMPLE_STUDENTS} students" in stderr and f"{CT.EXAMPLE_ITEMS} bank items" in stderr
    assert f"{CT.FIRST_DRAFT_CLASS} of {CT.CLASS_SIZE} students" in klass and f"{CT.FIRST_DRAFT_CLASS} students" in CT.ANCHORS["tgClass"][1]


def test_the_share_of_first_pages_is_the_examples_students_over_the_class():
    """38 sampled students over HW1's class of 68 or over the first draft's 66: 56 to 58% of first pages are a sampled student, 42 to 44% are not; Q1's two guessed terms give 0.16 at either end"""
    sh = CT.class_shares()
    assert (CT.pct_range(sh["in_lo"], sh["in_hi"]), CT.pct_range(sh["out_lo"], sh["out_hi"])) == ("56 to 58", "42 to 44")
    assert sh["in_lo"] + sh["out_hi"] == pytest.approx(1) and sh["in_hi"] + sh["out_lo"] == pytest.approx(1)
    assert CT.mix_range(0.10, 0.20) == "0.16" and CT.mix_range(0.10, 0.30) == "0.21 to 0.22"
    assert CT.pct_range(0.5, 0.504) == "50"
    q = {e["id"]: e for e in REG["events"]}
    assert q["Q2"]["p"] == round(sh["in_hi"], 2), "Q2 keeps the upper end of the share (its rests_on says so)"
    assert "42 to 44% of first pages are outside the sample" in q["Q1"]["rests_on"] and "0.16 at either end" in q["Q1"]["rests_on"] and "set at 0.15" in q["Q1"]["rests_on"] and q["Q1"]["p"] == 0.15


def toy_checkout(tmp_path, monkeypatch):
    """a speeds-kit checkout in miniature: a git repository holding the files a build reads, one anchor"""
    monkeypatch.setattr(CT, "ANCHORS", {"a": (CT.SCRIPT, r"^  function a\(", CT.FUNC_END, 1)})
    for rel in IN.READ:
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text('const VERSION = "0.6.7"; const BUILD = "10-04 23:12";\n  function a(x) {\n  }\n' if rel == CT.SCRIPT else f"{rel}\n", encoding="utf-8")
    git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *a], cwd=tmp_path, check=True, capture_output=True, text=True).stdout.strip()
    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "files")
    return git


def tree_hashes(root):
    return {str(p.relative_to(root)): sha(p) for p in sorted(Path(root).rglob("*")) if p.is_file() and ".git" not in p.parts}


def test_inputs_come_from_the_last_commit_that_touched_a_file_read_and_nothing_is_written(tmp_path, monkeypatch):
    git = toy_checkout(tmp_path, monkeypatch)
    first = git("rev-parse", "HEAD")
    (tmp_path / "tests").mkdir(exist_ok=True)
    (tmp_path / "tests" / "audit.py").write_text("later\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "a later commit that changes no file the build reads")
    before = tree_hashes(tmp_path)
    inp = IN.make(tmp_path, drafted="2026-10-05 00:00 EDT")
    assert inp["speeds_kit"]["commit"] == first and inp["speeds_kit"]["checkout_head"] == git("rev-parse", "HEAD") != first
    assert inp["speeds_kit"]["script"]["version"] == "0.6.7" and inp["speeds_kit"]["script"]["build"] == "10-04 23:12" and inp["citations"]["a"]["lines"] == [2, 3]
    assert IN.problems(inp, tmp_path) == []
    assert tree_hashes(tmp_path) == before, "the checkout is read, never written"


def test_a_checkout_with_local_changes_in_a_file_read_is_refused(tmp_path, monkeypatch):
    toy_checkout(tmp_path, monkeypatch)
    (tmp_path / "docs" / "TAPGRADE.md").write_text("edited\n", encoding="utf-8")
    with pytest.raises(IN.InputsError, match="local changes"):
        IN.make(tmp_path)
    inp = IN.make(tmp_path, commit="a" * 40)                       # a commit named by hand is taken as said
    assert inp["speeds_kit"]["commit"] == "a" * 40
    assert any("TAPGRADE.md" in x for x in IN.problems({**inp, "speeds_kit": {**inp["speeds_kit"], "read": {**inp["speeds_kit"]["read"], "docs/TAPGRADE.md": "0" * 64}}}, tmp_path))


def test_a_folder_that_is_not_a_checkout_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(CT, "ANCHORS", {})
    with pytest.raises(IN.InputsError, match="not a speeds-kit checkout"):
        IN.make(tmp_path)
    toy = tmp_path / "toy"
    for rel in IN.READ:
        (toy / rel).parent.mkdir(parents=True, exist_ok=True)
        (toy / rel).write_text('const VERSION = "1";\n', encoding="utf-8")
    with pytest.raises(IN.InputsError, match="git checkout"):
        IN.make(toy)
    with pytest.raises(IN.InputsError, match="40-character"):
        IN.make(toy, commit="cac0dc8")


# --- 3c. what changed since the first draft ---------------------------------------------------------------------------------------------
def test_the_first_draft_baseline_is_the_first_drafts():
    summary = json.loads((BASE / "summary.json").read_text(encoding="utf-8"))
    old = json.loads((BASE / "measured.json").read_text(encoding="utf-8"))
    keys = json.loads((BASE / "new-keys.json").read_text(encoding="utf-8"))
    assert summary["artifact"]["commit"].startswith("ca80695") and summary["artifact"]["script_sha256"] == old["script"]["sha256"] == keys["script_sha256"]
    assert len(summary["events"]) == 39 and len(summary["findings"]) == 20
    assert keys["predictors"]["two_pages"]["stale_page_save"]["the_other_pages_pick_is_kept"] is False, "the first-draft script lost the other page's pick (B-1)"
    new = json.loads((KIT / REG["measured"]["path"]).read_text(encoding="utf-8"))
    assert new["predictors"]["two_pages"]["stale_page_save"]["the_other_pages_pick_is_kept"] is True


def moved_items(key="changes_since_first_draft"):
    return [m for ch in REG[key]["changes"] for m in ch["moved"]]


@pytest.mark.parametrize("key", list(COMPARISONS))
def test_every_difference_is_explained_and_its_amount_is_the_two_sides(key):
    ch = REG[key]
    assert [c["id"] for c in ch["changes"]] == [c["id"] for c in CHANGES_OF[key]]
    assert ch["moved_count"] == len(moved_items(key)) > 0
    assert len({m["key"] for m in moved_items(key)}) == len(moved_items(key)), "no item is listed under two changes"
    for m in moved_items(key):
        assert m["why"] and (m["before"] != m["after"] or m.get("banks")), m["key"]
        try:
            b, a = float(m["before"].replace(",", "")), float(m["after"].replace(",", ""))
        except ValueError:
            continue
        assert m["delta"] and float(m["delta"].replace(",", "")) == pytest.approx(a - b, abs=0.006), m["key"]


@pytest.mark.parametrize("key", list(COMPARISONS))
def test_the_numbers_that_moved_are_the_ones_the_registration_holds(key):
    """the baseline's value and this registration's value, read from their own files, for each kind of item"""
    summary = json.loads((KIT / REG[key]["baseline"]["path"] / "summary.json").read_text(encoding="utf-8"))
    by_key = {m["key"]: m for m in moved_items(key)}
    for e in REG["events"]:
        old = summary["events"].get(e["id"])
        if old and old["p"] != e["p"]:
            m = by_key[f"event:{e['id']}:p"]
            assert (float(m["before"]), float(m["after"])) == (old["p"], e["p"])
        if old and old["basis"] != e["basis"]:
            m = by_key[f"event:{e['id']}:basis"]
            assert (m["before"], m["after"]) == (old["basis"], e["basis"])
        if old is None:
            assert f"event:{e['id']}:added" in by_key
    for s in REG["segments"]:
        old = summary["segments"][s["id"]]
        if round(s["load"], 2) != old["load"]:
            m = by_key[f"number:{s['id'].split('-sample-')[-1]}:load"]
            assert (float(m["before"]), float(m["after"])) == (old["load"], round(s["load"], 2))


def test_the_replaced_registration_is_the_one_that_was_replaced():
    """its folder is named by its commit, its summary says what it was, and what is claimed unchanged since it is checked against its numbers"""
    comparison = REG["changes_since_replaced_registration"]
    folder = KIT / comparison["baseline"]["path"]
    summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    measured = json.loads((folder / "measured.json").read_text(encoding="utf-8"))
    assert folder.name == "replaced-" + summary["artifact"]["commit"][:7] and summary["artifact"]["script_sha256"] == measured["script"]["sha256"]
    assert summary["artifact"]["commit"] != REG["artifact"]["commit"], "it was built against another head than this registration"
    assert len(summary["events"]) >= 39 and "declared.json" in {p.name for p in folder.iterdir()}
    assert not any("note" in step for steps in json.loads((folder / "declared.json").read_text(encoding="utf-8")).values() for step in steps), "declared properties only, no text"


def test_a_snapshot_of_a_registration_holds_its_numbers_and_no_text():
    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    snap = CH.snapshot(REG, fx, "a registration")
    summary, declared = json.loads(snap["summary.json"]), json.loads(snap["declared.json"])
    assert summary["events"].keys() == {e["id"]: 1 for e in REG["events"]}.keys() and all(summary["events"][e["id"]]["p"] == e["p"] for e in REG["events"])
    assert {k: v["load"] for k, v in summary["segments"].items()} == {s["id"]: round(s["load"], 2) for s in REG["segments"]}
    assert summary["artifact"]["script_sha256"] == REG["artifact"]["script_sha256"] and len(summary["findings"]) == sum(len(c["findings"]) for c in REG["chain_check_json"]["files"][0]["chains"])
    assert all("note" not in step and "target" not in step for steps in declared.values() for step in steps)


def test_the_registration_that_is_replaced_is_kept_as_data(tmp_path, monkeypatch):
    """rebuild --replace-previous keeps what the last commit holds in docs/predictions/replaced-<commit>/, drops an older such folder, and leaves new-keys.json alone"""
    git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *a], cwd=tmp_path, check=True, capture_output=True, text=True).stdout.strip()
    for rel in (RG.PRED, RG.FIXTURE, RG.MEASURED, RG.MEASURED_EXAMPLE):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_bytes((KIT / rel).read_bytes())
    old = tmp_path / "docs/predictions/replaced-0000000"
    old.mkdir(parents=True)
    (old / "summary.json").write_text("{}", encoding="utf-8")
    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "a registration")
    monkeypatch.setattr(RB, "REPO", tmp_path)
    dest = RB.snapshot_replaced()
    folder = tmp_path / dest
    assert folder.name == "replaced-" + REG["artifact"]["commit"][:7] and not old.exists()
    assert sorted(p.name for p in folder.iterdir()) == sorted(CH.BASELINE_FILES)
    assert json.loads((folder / "new-keys.json").read_text(encoding="utf-8"))["predictors"] == {}
    assert (folder / "measured.json").read_bytes() == (KIT / RG.MEASURED).read_bytes()
    (folder / "new-keys.json").write_text('{"predictors": {"x": 1}}', encoding="utf-8")
    assert RB.snapshot_replaced() == dest and json.loads((folder / "new-keys.json").read_text(encoding="utf-8")) == {"predictors": {"x": 1}}, "a second snapshot of the same registration keeps what someone added"


def test_amending_the_same_snapshot_keeps_the_earlier_replaced_folder_and_makes_no_new_one(tmp_path, monkeypatch):
    """rebuild --replace-previous on the speeds-kit commit the registration in HEAD was built against only amends it: the folder of the registration it replaced stays, nothing new is kept"""
    git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *a], cwd=tmp_path, check=True, capture_output=True, text=True).stdout.strip()
    monkeypatch.setattr(RB, "REPO", tmp_path)
    git("init", "-q")
    assert RB.head_registration_commit() is None, "no commit yet, no registration"
    for rel in (RG.PRED, RG.FIXTURE, RG.MEASURED, RG.MEASURED_EXAMPLE):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_bytes((KIT / rel).read_bytes())
    old = tmp_path / "docs/predictions/replaced-0000000"
    old.mkdir(parents=True)
    (old / "summary.json").write_text("{}", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "a registration")
    commit = REG["artifact"]["commit"]
    assert RB.head_registration_commit() == commit
    before = sorted(p.name for p in (tmp_path / "docs/predictions").iterdir())
    assert RB.snapshot_replaced(commit) == "docs/predictions/replaced-0000000"
    assert sorted(p.name for p in (tmp_path / "docs/predictions").iterdir()) == before and (old / "summary.json").read_text(encoding="utf-8") == "{}"
    shutil.rmtree(old)
    assert RB.snapshot_replaced(commit) is None and not (tmp_path / "docs/predictions" / ("replaced-" + commit[:7])).exists(), "nothing was replaced before: nothing is kept"
    kept = RB.snapshot_replaced("f" * 40)                         # another speeds-kit commit: the registration in HEAD is kept as data
    assert kept == f"docs/predictions/replaced-{commit[:7]}" and (tmp_path / kept / "summary.json").is_file()


def test_a_difference_nobody_explains_stops_the_build():
    item = {"key": "event:ZZ:p", "what": "ZZ p", "before": "0.10", "after": "0.20", "delta": "+0.10"}
    with pytest.raises(CH.Unattributed, match="no change claims them"):
        CH.attribute([item])


def test_a_claim_that_nothing_moved_is_checked():
    item = {"key": "measured:export.copy_as_json.picks", "what": "picks", "before": "3", "after": "4", "delta": "+1"}
    with pytest.raises(CH.Unattributed, match="says nothing moved"):
        CH.attribute([item])


def test_a_text_of_a_change_cites_the_docs_by_placeholder_and_a_placeholder_that_names_nothing_stops_the_build():
    fill = CH.filler(INPUTS)
    rb = INPUTS["citations"]["rbRoute"]
    assert fill("at {this}: {rbRoute}") == f"at {INPUTS['speeds_kit']['commit'][:7]}: {rb['file']}:{rb['lines'][0]}" + (f"-{rb['lines'][1]}" if rb["lines"][1] != rb["lines"][0] else "")
    with pytest.raises(CH.Unattributed, match="no anchor"):
        fill("{nope}")
    for text in [c["change"] + " " + c["effect"] for c in CH.CHANGES + CH.CHANGES_SINCE_REPLACED] + list(CH.WHY.values()) + list(CH.WHY_SINCE_REPLACED.values()):
        fill(text)                                                    # every text of the module can be filled
    md = MD.read_text(encoding="utf-8")
    assert not re.search(r"\{(?:this|" + "|".join(CT.ANCHORS) + r")\}", md + PRED.read_text(encoding="utf-8")), "a placeholder was printed as it stands"


def test_an_item_claimed_by_two_changes_or_without_a_reason_is_refused(monkeypatch):
    item = {"key": "event:Q1:p", "what": "Q1 p", "before": "0.45", "after": "0.35", "delta": "-0.10"}
    two = [dict(id="a", change="a", effect="", moved=["event:Q1:*"], nothing_moved_in=[]), dict(id="b", change="b", effect="", moved=["event:*:p"], nothing_moved_in=[])]
    monkeypatch.setattr(CH, "CHANGES", two)
    with pytest.raises(CH.Unattributed, match="claimed by two changes"):
        CH.attribute([dict(item)])
    monkeypatch.setattr(CH, "CHANGES", two[:1])
    monkeypatch.setattr(CH, "WHY", {})
    with pytest.raises(CH.Unattributed, match="no reason"):
        CH.attribute([dict(item)])


def test_the_md_lists_every_difference_and_every_change():
    md = MD.read_text(encoding="utf-8")
    assert f"## What changed in TapGrade between the first draft ({REG['changes_since_first_draft']['scripts']['before']['commit'][:7]}) and this registration" in md
    if REG.get("changes_since_replaced_registration"):
        assert f"## What changed in TapGrade since the registration for {REG['changes_since_replaced_registration']['scripts']['before']['commit'][:7]} that this one replaces" in md
    for comparison in COMPARISONS.values():
        for c in comparison["changes"]:
            assert c["change"] in md, c["id"]
            for m in c["moved"]:
                assert m["what"] in md, m["key"]


# --- 4. must-fire ---------------------------------------------------------------------------------------------------------------------
def _copy_with(tmp_path, fx, edit, indent=2):
    doc = copy.deepcopy(fx)
    edit(doc)
    path = tmp_path / "copy.json"
    path.write_text(json.dumps(doc, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _step(doc, suffix, n):
    return next(c for c in doc["chains"] if c["id"] == PFX + suffix)["steps"][n - 1]


def test_an_untouched_copy_passes_and_a_reformatted_one_fails_only_the_sha(tmp_path, fx):
    """the fixture is written with indent 2: the same declarations in other bytes keep the numbers and lose the sha, which also pins the notes"""
    assert registration_problems(_copy_with(tmp_path, fx, lambda d: None), REG) == ([], [])
    file_problems, number_problems = registration_problems(_copy_with(tmp_path, fx, lambda d: None, indent=1), REG)
    assert file_problems and not number_problems


def test_a_changed_note_is_caught_by_the_sha_alone(tmp_path, fx):
    def edit(d):
        _step(d, "pair", 7)["note"] += " (edited later)"
    file_problems, number_problems = registration_problems(_copy_with(tmp_path, fx, edit), REG)
    assert file_problems and not number_problems


@pytest.mark.parametrize("suffix,step,change,what", [
    ("pair", 9, {"everything_on_screen": True}, "findings"),                  # the colocation finding goes
    ("pair", 1, {"progress_visible": True}, "findings"),                      # the progress finding goes
    ("pair", 7, {"amount": 9}, "load"),                                       # more to read: the load moves
    ("pair", 7, {"times": 1}, "load"),
    ("queue", 1, {"origin_stated": True}, "findings"),
    ("pair-reload", 9, {"restores": ["position", "goal", "partial"]}, "findings"),
    ("export", 6, {"verify_after": "none"}, "findings"),                      # a silent chain gains a finding
])
def test_a_changed_declared_property_is_detected(tmp_path, fx, suffix, step, change, what):
    path = _copy_with(tmp_path, fx, lambda d: _step(d, suffix, step).update(change))
    file_problems, number_problems = registration_problems(path, REG)
    assert file_problems, "the sha must differ"
    assert any(f"{PFX}{suffix}: {what} " in p for p in number_problems), (what, number_problems)


def test_a_changed_held_item_is_detected(tmp_path, fx):
    """drop the key from the held list of the chip decision: the working set falls to 3 and the memory finding goes"""
    def edit(d):
        st = _step(d, "pair", 7)
        st["held"] = st["held"][:1]
    _, number_problems = registration_problems(_copy_with(tmp_path, fx, edit), REG)
    assert any("pair: findings" in p for p in number_problems) and any("pair: over_budget_steps" in p for p in number_problems)


def test_a_changed_budget_in_the_file_is_detected(tmp_path, fx):
    _, number_problems = registration_problems(_copy_with(tmp_path, fx, lambda d: d.update(budget=4)), REG)
    assert any(": budget " in p for p in number_problems)


def test_a_missing_or_added_chain_is_detected(tmp_path, fx):
    _, number_problems = registration_problems(_copy_with(tmp_path, fx, lambda d: d["chains"].pop()), REG)
    assert any("are not in both" in p for p in number_problems)


def test_a_tampered_registration_is_detected():
    bad = copy.deepcopy(REG)
    bad["chain_check_json"]["files"][0]["chains"][2]["load"] += 0.01
    _, number_problems = registration_problems(FIXTURE, bad)
    assert any("pair: load" in p for p in number_problems)
    bad = copy.deepcopy(REG)
    bad["fixture"]["sha256"] = "0" * 64
    file_problems, _ = registration_problems(FIXTURE, bad)
    assert file_problems
    bad = copy.deepcopy(REG)
    bad["over_budget_steps"]["2"][PFX + "pair"] = [6]
    _, number_problems = registration_problems(FIXTURE, bad)
    assert any("B=2" in p for p in number_problems)


def test_a_moved_weight_or_lookalike_is_detected():
    bad = copy.deepcopy(REG)
    bad["parameters"]["weights"]["reload"] = 5.0
    assert any("weights" in p for p in params_problems(bad))
    bad = copy.deepcopy(REG)
    bad["parameters"]["lookalike"] = 0.4
    assert any("look-alike" in p for p in params_problems(bad))
    bad = copy.deepcopy(REG)
    bad["parameters"]["verifiers"] = bad["parameters"]["verifiers"][:-1]
    assert any("verifiers" in p for p in params_problems(bad))


def test_the_failure_message_is_the_one_the_brief_asked_for():
    assert MSG == "the fixture changed after registration: write a NEW dated registration, do not edit this one"
    with pytest.raises(AssertionError, match="the fixture changed after registration: write a NEW dated registration, do not edit this one"):
        bad = copy.deepcopy(REG)
        bad["fixture"]["sha256"] = "1" * 64
        file_problems, _ = registration_problems(FIXTURE, bad)
        assert not file_problems, MSG + "\n  " + "\n  ".join(file_problems)


# --- 5. the scorer, on toy data ---------------------------------------------------------------------------------------------------------
def toy():
    """five segments (A longest), one predicted onset in B (step 7 of 9, at B=3 and B=2), two events at a finding step, two not"""
    ids = ["A", "B", "C", "D", "E"]
    steps = {"A": 9, "B": 6, "C": 5, "D": 4, "E": 3}
    return {
        "id": "toy", "parameters": {"budget": 3, "budget_sensitivity": [2, 4], "p_basis": ["measured", "declared", "carried-from-HW1", "guess"],
                                    "rank_ties": {"unstable_pairs": [{"a": "D", "b": "E", "a_above_b_share": 0.6}]}},
        "segments": [{"id": i, "steps": steps[i], "predicted_loss_onsets_at_B": {"2": [7] if i == "A" else [], "3": [7] if i == "A" else [], "4": []}} for i in ids],
        "ranking": {"rank": {"A": 1, "B": 2, "C": 3, "D": 4.5, "E": 4.5}, "excluded_from_tau": [], "baseline_by_step_count": {"rank": {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}}},
        "events": [
            {"id": "e1", "segment": "A", "steps": [{"chain": "A", "step": 7}], "p": 0.8, "basis": "declared"},
            {"id": "e2", "segment": "A", "steps": [{"chain": "A", "step": 2}], "p": 0.2, "basis": "measured"},
            {"id": "e3", "segment": "B", "steps": [{"chain": "B", "step": 1}], "p": 0.5, "basis": "guess"},
            {"id": "e4", "segment": "B", "steps": [{"chain": "B", "step": 2}], "p": 0.9, "basis": "measured"},
        ],
        "chain_check_json": {"files": [{"chains": [{"id": "A", "findings": [{"step": 7, "verifier": "memory_budget"}]}, {"id": "B", "findings": []}]}]},
    }


def outcomes(**kw):
    d = {"schema": "emu-outcomes/1", "prediction": "toy", "events": {}}
    d.update(kw)
    return d


def test_brier_by_hand():
    r = P.score(toy(), outcomes(events={"e1": 1, "e2": 0, "e3": None, "e4": 0}))["brier"]
    assert r["n"] == 3
    assert r["brier"] == pytest.approx(((0.8 - 1) ** 2 + (0.2 - 0) ** 2 + (0.9 - 0) ** 2) / 3)
    mean_p = (0.8 + 0.2 + 0.9) / 3
    assert r["reference_constant_mean_p"] == pytest.approx(((mean_p - 1) ** 2 + mean_p ** 2 + mean_p ** 2) / 3)
    assert r["reference_constant_half"] == pytest.approx(0.25)
    assert r["by_basis"]["measured"] == {"n": 2, "brier": pytest.approx((0.04 + 0.81) / 2), "agree": 1}      # e2 right (0.2 and 0), e4 wrong (0.9 and 0)
    assert r["by_basis"]["declared"]["agree"] == 1 and "guess" not in r["by_basis"]
    assert P.score(toy(), outcomes())["brier"] == {"n": 0}


def test_tau_b_by_hand():
    assert P.tau_b([1, 2, 3, 4], [1, 2, 3, 4]) == 1.0 and P.tau_b([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0
    assert P.tau_b([1, 2, 3, 4], [1, 1, 2, 2]) == pytest.approx(4 / 24 ** 0.5)       # C=4, D=0, ties in y only: 2
    assert P.tau_b([1, 2, 3], [5, 5, 5]) is None
    assert P.permutation_p([4, 3, 2, 1], [4, 3, 2, 1]) == pytest.approx(1 / 24)
    assert P.permutation_p([1, 2, 3, 4, 5], [9, 9, 9, 9, 9]) is None


def test_kendall_on_toy_segments():
    pred = toy()
    k = P.score(pred, outcomes(durations_min={"A": 10, "B": 8, "C": 5, "D": 3, "E": 1}))["kendall"]
    # D and E tie in the prediction: C = 9 pairs, D = 0, tied in x only = 1 (D, E), tied in y only = 0
    assert k["scored"] and k["tau_b_load"] == pytest.approx(9 / 90 ** 0.5) and k["tau_b_step_count"] == 1.0
    assert k["p_permutation_step_count"] == pytest.approx(1 / 120) and k["reversals"] == []
    k = P.score(pred, outcomes(durations_min={"A": 4, "B": 8, "C": 3, "D": 2, "E": 1}))["kendall"]
    assert k["reversals"] == [{"predicted_longer": "A", "measured_longer": "B", "minutes": [4, 8]}]        # B is 4 minutes (50%) longer than A, and the weights put A above B
    assert k["tau_b_load"] < 1 and k["tau_b_step_count"] < 1
    pred["parameters"]["rank_ties"]["unstable_pairs"].append({"a": "A", "b": "B", "a_above_b_share": 0.5})
    assert P.score(pred, outcomes(durations_min={"A": 4, "B": 8, "C": 3, "D": 2, "E": 1}))["kendall"]["reversals"] == [], "a pair the weights do not order stably is not a reversal"
    k = P.score(toy(), outcomes(durations_min={"A": 10, "B": 8, "C": 5}))["kendall"]
    assert not k["scored"] and "fewer than 4" in k["why"]


def test_measured_minutes_are_whole_minutes_and_half_rounds_up():
    assert P._whole(2.5) == 3 and P._whole(2.49) == 2 and P._whole(0.4) == 0
    k = P.score(toy(), outcomes(durations_min={"A": 10, "B": 5.5, "C": 5.4, "D": 3, "E": 1}))["kendall"]
    assert k["measured_minutes"]["B"] == 6 and k["measured_minutes"]["C"] == 5


def test_excluded_segments_are_left_out_of_tau():
    pred = toy()
    pred["ranking"]["excluded_from_tau"] = ["E"]
    k = P.score(pred, outcomes(durations_min={"A": 10, "B": 8, "C": 5, "D": 3, "E": 99}))["kendall"]
    assert k["segments"] == ["A", "B", "C", "D"] and k["tau_b_load"] == 1.0


def test_onsets_hits_chance_and_false_alarms():
    pred = toy()
    r = P.score(pred, outcomes(losses=[{"chain": "A", "step": 6}, {"chain": "A", "step": 1}, {"chain": "B", "step": 3}]))["onsets"]
    b3 = r["3"]
    assert b3["losses_in_chains_with_a_predicted_onset"] == 2 and b3["hits_within_two_steps"] == 1       # step 6 is within two of 7, step 1 is not
    assert b3["hits_expected_by_chance"] == pytest.approx(2 * 5 / 9, abs=1e-3)                            # steps 5..9 of 9
    assert b3["false_alarms"] == 1 and b3["predicted_onsets"] == {"A": [7]}
    assert r["4"]["false_alarms"] == 3 and r["4"]["losses_in_chains_with_a_predicted_onset"] == 0
    assert r["2"]["hits_within_two_steps"] == 1


def test_p02be_rates_and_counts():
    r = P.score(toy(), outcomes(events={"e1": 1, "e2": 0, "e3": 1, "e4": 1},
                                unregistered_frictions=[{"chain": "B", "step": 4}, {"chain": "A", "step": 7}],
                                false_findings=[{"chain": "A", "step": 7, "verifier": "memory_budget"}]))["p02be"]
    assert r["events_at_a_step_with_a_finding"] == {"n": 1, "observed_rate": 1.0}                         # e1 only: A step 7 has the finding
    assert r["events_at_steps_without_a_finding"] == {"n": 3, "observed_rate": pytest.approx(2 / 3)}
    assert r["unregistered_frictions"] == 2 and r["unregistered_at_a_silent_step"] == 1 and r["false_findings"] == 1 and r["findings_registered"] == 1


@pytest.mark.parametrize("bad,why", [
    (outcomes(schema="emu-outcomes/2"), "schema"),
    (outcomes(prediction="other"), "prediction"),
    (outcomes(events={"nope": 1}), "unknown event id"),
    (outcomes(events={"e1": 2}), "must be 1, 0 or null"),
    (outcomes(durations_min={"Z": 3}), "unknown segment"),
    (outcomes(losses=[{"chain": "A", "step": 10}]), "names no step"),
    (outcomes(unregistered_frictions=[{"chain": "A", "step": 0}]), "names no step"),
    (outcomes(false_findings=[{"chain": "Q", "step": 1}]), "names no step"),
])
def test_the_scorer_refuses_what_it_cannot_score(bad, why):
    with pytest.raises(P.OutcomesError, match=why):
        P.score(toy(), bad)


def test_the_scorer_on_the_real_registration_and_its_cli(tmp_path):
    out = {"schema": "emu-outcomes/1", "prediction": REG["id"], "events": {e["id"]: (1 if e["p"] >= 0.5 else 0) for e in REG["events"]},
           "durations_min": {s["id"]: 20 - round(s["rank"] * 2) for s in REG["segments"] if s["comparable_by_duration"]},
           "losses": [{"chain": PFX + "pair", "step": 6}], "unregistered_frictions": [], "false_findings": []}
    f = tmp_path / "o.json"
    f.write_text(json.dumps(out), encoding="utf-8")
    run = lambda *a: subprocess.run([sys.executable, str(HERE / "prediction_score.py"), str(PRED), str(f), *a], capture_output=True, text=True, timeout=60)
    t = run()
    assert t.returncode == 0, t.stderr
    assert "brier" in t.stdout and "kendall tau-b load" in t.stdout and "onsets at B=3: 1 hits of 1 losses" in t.stdout
    j = json.loads(run("--json").stdout)
    assert j["brier"]["n"] == len(REG["events"]) and j["kendall"]["tau_b_load"] > 0.9      # durations were made to follow the predicted ranks
    out["events"]["zzz"] = 1
    f.write_text(json.dumps(out), encoding="utf-8")
    bad = run()
    assert bad.returncode == 2 and "unknown event id" in bad.stderr
    assert subprocess.run([sys.executable, str(HERE / "prediction_score.py")], capture_output=True, text=True).returncode == 2


# --- 6. the one command ----------------------------------------------------------------------------------------------------------------
def test_rebuild_refuses_what_it_should(tmp_path):
    with pytest.raises(SystemExit, match="trailer lines"):
        RB.rebuild(tmp_path, make_commits=True)
    with pytest.raises(SystemExit, match="not this repository"):
        RB.rebuild(KIT / "docs")
    with pytest.raises(SystemExit, match="8881"):
        RB.measure(tmp_path, 8000, tmp_path)
    with pytest.raises(IN.InputsError, match="not a speeds-kit checkout"):
        RB.rebuild(tmp_path, port=8881, measured={"large": tmp_path / "a.json", "example": tmp_path / "b.json"})


def test_a_port_that_is_in_use_is_refused(tmp_path):
    import socket
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", 8883))
        s.listen(1)
    except OSError:
        pass                                           # busy already: the refusal below is what is tested
    try:
        with pytest.raises(SystemExit, match="already in use"):
            RB.measure(tmp_path, 8883, tmp_path)
    finally:
        s.close()


def test_the_ops_section_is_replaced_in_place_or_put_before_the_p_2a7c_section():
    from checks.hw2_sample_prediction import markdown as MK
    doc = "# Doc\n\n## One\n\ntext\n\n## A prediction registered before the pass\n\nold\n\n## P-2a7c integration point (design only)\n\nlater\n"
    new = "## A prediction registered before the pass\n\nnew\n"
    out = MK.splice_ops(doc, new)
    assert "old" not in out and "new" in out and out.count("## A prediction registered before the pass") == 1 and out.index("new") < out.index("## P-2a7c") and "later" in out
    fresh = MK.splice_ops("# Doc\n\n## One\n\ntext\n\n## P-2a7c integration point (design only)\n\nlater\n", new)
    assert fresh.index("new") < fresh.index("## P-2a7c") and fresh.index("text") < fresh.index("new")
    assert MK.splice_ops(out, new) == out, "splicing twice changes nothing"


def test_a_changed_file_read_is_listed_with_what_cites_it():
    old = json.loads(json.dumps(INPUTS))
    new = json.loads(json.dumps(INPUTS))
    new["speeds_kit"]["read"]["docs/HW2-HW3-RUNBOOK.md"] = "0" * 64
    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    evs = REG["events"]
    lines = RB.changed_reads(old, new, fx, evs)
    assert len(lines) == 1 and "docs/HW2-HW3-RUNBOOK.md changed" in lines[0] and "queue:1" in lines[0] and "Q1" in lines[0]
    assert RB.changed_reads(old, old, fx, evs) == [] and RB.changed_reads(None, new, fx, evs) == []


def test_a_changed_line_of_the_docs_is_listed_with_the_notes_and_events_that_cite_it():
    old = json.loads(json.dumps(INPUTS["citations"]))
    old["rbRoute"]["text"] = "- The pass: Grade, then the Sample tab, then Next pair."
    old["rbStderr"]["lines"] = [1, 1]
    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    changed, shifted = RB.moved_citations(old, INPUTS["citations"], fx, REG["events"])
    line = next(x for x in changed if x.startswith("rbRoute:"))
    assert "Grade, then the Sample tab" in line and "queue:1" in line and "Q1" in line, line
    assert "rbStderr" in shifted and RB.moved_citations(None, INPUTS["citations"], fx, REG["events"]) == ([], [])


def test_the_command_line_checks_what_the_generator_made():
    run = lambda *a: subprocess.run([sys.executable, "-m", "checks.hw2_sample_prediction", *a], cwd=str(KIT), capture_output=True, text=True, timeout=120)
    r = run("build", "--check")
    assert r.returncode == 0 and "is what the generator makes" in r.stdout, r.stdout + r.stderr
    r = run("verify", "--speeds-kit", "/nonexistent")
    assert r.returncode == 2 and "not a speeds-kit checkout" in r.stderr
    assert run("rebuild").returncode == 2


def test_the_text_is_a_function_of_the_registration_and_the_inputs():
    """the md is what the generator makes from the JSON; other inputs give another text, so a hand edit or a changed generator cannot pass for the registered one"""
    from checks.hw2_sample_prediction import markdown as MK
    md = MD.read_text(encoding="utf-8")
    MJ = json.loads((KIT / REG["measured"]["path"]).read_text(encoding="utf-8"))
    AJ = json.loads((KIT / REG["measured_example_bank"]["path"]).read_text(encoding="utf-8"))
    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert MK.render(REG, MJ, AJ, fx, INPUTS) == md
    other = {**INPUTS, "citations": {**INPUTS["citations"], "rbStderr": {**INPUTS["citations"]["rbStderr"], "lines": [1, 1]}}}          # the same commit, another line cited
    assert MK.render(REG, MJ, AJ, fx, other) != md


# --- 7. the docs ----------------------------------------------------------------------------------------------------------------------
def test_the_md_tables_are_the_jsons():
    md = MD.read_text(encoding="utf-8")
    short = {s["id"]: s["short"] for s in REG["segments"]}
    for s in REG["segments"]:
        c = next(x for x in REG["chain_check_json"]["files"][0]["chains"] if x["id"] == s["id"])
        row = f"| {s['short']} `{s['id'][len(PFX):]}` | {s['steps']} | {c['load']:.2f} | {c['peak_slots']} | {len(c['findings'])} | {s['rank']:g} | {'yes' if s['comparable_by_duration'] else 'no'} |"
        assert row in md, row
    for e in REG["events"]:
        steps = ", ".join(f"{short[r['chain']]}:{r['step']}" for r in e["steps"])
        row = f"| {e['id']} | {short[e['segment']]} | {steps} | {e['event']} | {e['p']:.2f} | {e['basis']} |"
        assert row in md, row
    for needle in (REG["fixture"]["sha256"], REG["artifact"]["script_sha256"], REG["measured"]["sha256"], REG["measured_example_bank"]["sha256"], REG["inputs"]["sha256"], REG["drunken_emu"]["commit"], REG["scorer"]["sha256"], REG["measured"]["tool_sha256"]):
        assert needle in md, needle
    for h in ("## 1. Parameters", "## 2. Dataflow", "## 3. Predictors", "### 3b. The bank's size is unknown", "## 4. Predicted loss onsets", "## 5. Predicted ranking", "## 6. Scoring", "## 7. What would falsify", "## 8. Limits",
              "## What changed in TapGrade between the first draft", "## Re-running on the final code", "## What changed while drafting"):
        assert h in md, h
    assert "python3 -m checks.hw2_sample_prediction rebuild --speeds-kit" in md


def test_the_docs_point_at_the_registration():
    ops = (KIT / "docs" / "OPERATION-CHAINS.md").read_text(encoding="utf-8")
    assert "## A prediction registered before the pass" in ops and "docs/predictions/" in ops and "docs/predictions/hw2-sample-pass.md" in ops
    assert "checks.hw2_sample_prediction rebuild" in ops and "<!-- /hw2-sample-prediction -->" in ops
    readme = (KIT / "README.md").read_text(encoding="utf-8")
    for name in ("docs/predictions/", "measure_sample_predictors.py", "prediction_score.py", "test_prediction.py", "hw2_sample_prediction"):
        assert name in readme, name
    tree = (KIT / "docs" / "TREE.md").read_text(encoding="utf-8")
    for name in ("hw2-sample-pass.md", "hw2-sample-pass.prediction.json", "hw2-sample-pass.measured.json", "hw2-sample-pass.inputs.json", "first-draft-ca80695", "tapgrade_0_6_7_sample_pass.json", "test_prediction.py", "prediction_score.py", "hw2_sample_prediction", "rebuild.py"):
        assert name in tree, name


# --- 8. the second registration: the rule, the judgments, the baselines ------------------------------------------------------------------
def _replaced_folder() -> Path:
    return KIT / REG["changes_since_replaced_registration"]["baseline"]["path"]


def _replaced_json(name):
    return json.loads((_replaced_folder() / name).read_text(encoding="utf-8"))


def _measured_pair():
    return (json.loads((KIT / REG["measured"]["path"]).read_text(encoding="utf-8")), json.loads((KIT / REG["measured_example_bank"]["path"]).read_text(encoding="utf-8")))


def test_half_way_goes_to_the_lower_step_and_the_line_is_worked_out_by_hand():
    from checks.hw2_sample_prediction import events as EV
    assert EV.half_down(0.325) == 0.30 and EV.half_down(0.375) == 0.35 and EV.half_down(0.55) == 0.55 and EV.half_down(0.5249) == 0.50 and EV.half_down(0.5251) == 0.55
    assert EV.half_down(0.04) == 0.05 and EV.half_down(0.0) == 0.0
    # P2 was judged 0.60 at 4.0 screens (example-size bank) and 0.80 at 10.9 (large bank): at 10.0 the line reads 0.80 - 0.9 * 0.2 / 6.9, the middle with 0.60 is 0.687, which rounds to 0.70
    assert EV.read_off("P2", 4.0) == pytest.approx(0.60) and EV.read_off("P2", 10.9) == pytest.approx(0.80)
    assert EV.read_off("P2", 10.0) == pytest.approx(0.80 - 0.9 * 0.2 / 6.9)
    p, small, large = EV.by_rule("P2", 4.0, 10.0)
    assert (p, small) == (0.70, pytest.approx(0.60)) and large == pytest.approx(0.7739, abs=1e-4)
    assert EV.read_off("P2", 100) == 0.95 and EV.read_off("P2", -100) == 0.05, "never below 0.05 or above 0.95"
    # P8 (0.25 at 4.0, 0.40 at 10.9): at 10.0 the line reads 0.25 + 6 * 0.15 / 6.9 = 0.3804; the middle with 0.25 is 0.315, which rounds to 0.30
    assert EV.by_rule("P8", 4.0, 10.0)[0] == 0.30
    # P1 (0.45 at 41%, 0.65 at 71%): at 68% the line reads 0.45 + 0.27 * 0.2 / 0.3 = 0.63; the middle with 0.45 is 0.54, which rounds to 0.55
    assert EV.read_off("P1", 0.68) == pytest.approx(0.63) and EV.by_rule("P1", 0.41, 0.68)[0] == 0.55


def test_p1_p2_and_p8_are_what_the_rule_gives_at_the_measured_numbers_and_the_rule_starts_from_the_replaced_registration():
    from checks.hw2_sample_prediction import events as EV
    MJ, AJ = _measured_pair()
    M, A = MJ["predictors"], AJ["predictors"]
    ev = {e["id"]: e for e in REG["events"]}
    key_out, a_key_out = 1 - M["chips"]["at_the_default_sheet"]["key_in_view_with_a_chip"]["share"], 1 - A["chips"]["at_the_default_sheet"]["key_in_view_with_a_chip"]["share"]
    assert ev["P1"]["p"] == EV.by_rule("P1", a_key_out, key_out)[0]
    assert ev["P2"]["p"] == EV.by_rule("P2", A["window"]["screens_per_question"]["median"], M["window"]["screens_per_question"]["median"])[0]
    assert ev["P8"]["p"] == EV.by_rule("P8", A["window"]["screens_per_question"]["median"], M["window"]["screens_per_question"]["median"])[0]
    for eid in EV.CALIBRATION:
        assert "p follows the rule at the top of events.py" in ev[eid]["rests_on"] and f"that registration set {EV.registered_before(eid):.2f}" in ev[eid]["rests_on"], eid
    summary = _replaced_json("summary.json")
    if summary["artifact"]["commit"].startswith("cec1bba"):                      # the rule is calibrated on that registration: at its own numbers it gives its own p
        assert {eid: EV.registered_before(eid) for eid in EV.CALIBRATION} == {eid: summary["events"][eid]["p"] for eid in EV.CALIBRATION}
        old_large, old_example = _replaced_json("measured.json")["predictors"], _replaced_json("measured-example-bank.json")["predictors"]
        (_, (xs1, _), (xl1, _)), (_, (xs2, _), (xl2, _)) = EV.CALIBRATION["P1"], EV.CALIBRATION["P2"]
        assert xs1 == pytest.approx(1 - old_example["chips"]["at_the_default_sheet"]["key_in_view_with_a_chip"]["share"], abs=0.005)
        assert xl1 == pytest.approx(1 - old_large["chips"]["at_the_default_sheet"]["key_in_view_with_a_chip"]["share"], abs=0.005)
        assert (xs2, xl2) == (old_example["window"]["screens_per_question"]["median"], old_large["window"]["screens_per_question"]["median"])
        assert EV.CEC1BBA == {"message_shift_px": old_large["view_stability"]["load_toast"]["content_moves_when_it_goes_px"], "window_large_px": old_large["window"]["pair_view"]["body_h"],
                              "window_with_message_large_px": old_large["window"]["pair_view_with_toast"]["body_h"], "window_with_message_example_px": old_example["window"]["pair_view_with_toast"]["body_h"],
                              "head_with_a_wrapped_tag_px": old_large["window"]["pair_view"]["head_h"]}, "the numbers typed for the cec1bba build are that registration's measured numbers"


def test_the_example_banks_old_chip_shift_was_the_wrapped_head_growing():
    """the claim that the chip-tap shift belongs to the head change, not to the list: the shift the example-size bank measured before is the growth of the head"""
    from checks.hw2_sample_prediction import events as EV
    summary = _replaced_json("summary.json")
    if not summary["artifact"]["commit"].startswith("cec1bba"):
        pytest.skip("written for the registration against cec1bba")
    MJ, AJ = _measured_pair()
    old_shift = _replaced_json("measured-example-bank.json")["predictors"]["view_stability"]["chip_tap"]["max_chip_shift_px"]
    assert old_shift == pytest.approx(EV.CEC1BBA["head_with_a_wrapped_tag_px"] - MJ["predictors"]["window"]["pair_view"]["head_h"], abs=0.15)
    assert AJ["predictors"]["view_stability"]["chip_tap"]["max_chip_shift_px"] < old_shift


@pytest.mark.parametrize("key", list(COMPARISONS))
def test_the_current_tool_reproduces_each_baselines_own_numbers_on_its_script(key):
    """new-keys.json is made by the current tool on the baseline's own script; it must give the baseline's numbers back for every key the baseline has (timings aside)"""
    folder = KIT / REG[key]["baseline"]["path"]
    keys = json.loads((folder / "new-keys.json").read_text(encoding="utf-8"))
    chk = keys["checked_against_the_baseline"]
    assert chk["keys_different"] == 0 and chk["keys_compared"] > 0 and keys["script_sha256"] == json.loads((folder / "measured.json").read_text(encoding="utf-8"))["script"]["sha256"]
    assert REG[key]["baseline"]["new_keys_check"] == chk


def test_an_event_changed_by_judgment_names_the_value_it_had_and_who_judged_it():
    from checks.hw2_sample_prediction import events as EV
    ev = {e["id"]: e for e in REG["events"]}
    comparison = REG["changes_since_replaced_registration"]
    moved = {m["key"]: m for c in comparison["changes"] for m in c["moved"]}
    judged = [k.split(":")[1] for k, m in moved.items() if k.startswith("event:") and k.endswith(":p")]
    assert judged, "the third round moved the p of some event"
    for eid in judged:
        m = moved[f"event:{eid}:p"]
        assert eid not in EV.CALIBRATION, f"{eid} follows the rule: a change of its p is the rule's"
        text = ev[eid]["rests_on"]
        assert f"{float(m['before']):.2f}" in text and "judgment" in text and "has now seen" in text, f"{eid}: the replaced value, the word judgment and who has seen the change"
        assert "expected to remove" in text or "now tests the fix" in text, f"{eid}: what the fix is expected to do to the event"
    md = MD.read_text(encoding="utf-8")
    assert "is expected to take away, and what it is not" in md and "the pass may show other frictions that nothing here predicts" in md and "Nothing was lowered to make the prediction look right" in md
    old_summary = _replaced_json("summary.json")
    was, now = CH.top_five(old_summary["events"]), CH.top_five({e["id"]: e for e in REG["events"]})
    assert ("The top five changed since" in md) == (was != now) and ("These are the same five as in the registration for" in md) == (was == now)
    assert ("number:events:top_five" in moved) == (was != now), "the changes table lists the top five when it moved"


def test_a_round_without_a_list_of_expected_effects_or_a_history_entry_stops_the_text(monkeypatch):
    from checks.hw2_sample_prediction import markdown as MK
    MJ, AJ = _measured_pair()
    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    th = REG["artifact"]["commit"][:7]
    assert MK.render(REG, MJ, AJ, fx, INPUTS) == MD.read_text(encoding="utf-8")
    rows = MK.EXPECTED[th]
    monkeypatch.setattr(MK, "EXPECTED", {})
    with pytest.raises(ValueError, match="no list for the round"):
        MK.render(REG, MJ, AJ, fx, INPUTS)
    monkeypatch.setattr(MK, "EXPECTED", {th: [r for r in rows if r[0] != "P5"]})
    with pytest.raises(ValueError, match="no entry for P5"):
        MK.render(REG, MJ, AJ, fx, INPUTS)
    monkeypatch.setattr(MK, "EXPECTED", {th: rows})
    monkeypatch.setattr(MK, "HISTORY", [h for h in MK.HISTORY if h[0] != th])
    with pytest.raises(ValueError, match="no entry for the snapshot"):
        MK.render(REG, MJ, AJ, fx, INPUTS)


def test_no_note_or_event_says_none_throws_the_list_to_the_top_while_the_measurement_says_it_does_not(fx):
    """the pair chain's save note said it for the cec1bba build and went on saying it after the build changed: a sentence that claims it must be about an earlier build"""
    MJ, _ = _measured_pair()
    if MJ["predictors"]["view_stability"]["none_tap"]["jumps_to_the_top"]:
        pytest.skip("the measurement says the list is thrown to the top: the statement is true")
    texts = [stp["note"] for ch in fx["chains"] for stp in ch["steps"]] + [e["rests_on"] for e in REG["events"]] + [r["value"] for r in REG["predictors"]]
    for text in texts:
        for sentence in re.split(r"(?<=[.;]) ", text):
            if re.search(r"\bNone\b", sentence) and re.search(r"\b(jumps|throws|thrown)\b[^.;]*\bto the top\b", sentence):
                assert re.search(r"none of|: no\b|cec1bba|ca80695|before|earlier|first draft", sentence, re.I), f"a sentence says None throws the list to the top: {sentence[:200]}"


# the one command, for a registration that was pushed
def _git_in(path):
    return lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *a], cwd=path, check=True, capture_output=True, text=True).stdout.strip()


def test_supersede_and_replace_previous_exclude_each_other_and_supersede_needs_an_older_registration(tmp_path, monkeypatch):
    with pytest.raises(SystemExit, match="exclude each other"):
        RB.rebuild(tmp_path, supersede=True, replace_previous=True)
    repo, kit = tmp_path / "repo", tmp_path / "kit"
    repo.mkdir()
    kit.mkdir()
    git = _git_in(repo)
    git("init", "-q")
    (repo / "README").write_text("nothing registered yet\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "files")
    monkeypatch.setattr(RB, "REPO", repo)
    toy_checkout(kit, monkeypatch)
    with pytest.raises(SystemExit, match="HEAD holds no registration to supersede"):
        RB.rebuild(kit, commit="a" * 40, supersede=True)
    (repo / RG.PRED).parent.mkdir(parents=True)
    (repo / RG.PRED).write_bytes(PRED.read_bytes())
    git("add", "-A")
    git("commit", "-q", "-m", "a registration")
    assert RB.head_registration_commit() == REG["artifact"]["commit"] and RB.registration_commit() == git("rev-parse", "HEAD")
    with pytest.raises(SystemExit, match="built against this very speeds-kit commit"):
        RB.rebuild(kit, commit=REG["artifact"]["commit"], supersede=True)


def test_a_superseded_registration_keeps_the_commit_that_registered_it_and_its_folder_leaves_the_index_when_an_older_one_goes(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    git = _git_in(repo)
    git("init", "-q")
    for rel in (RG.PRED, RG.FIXTURE, RG.MEASURED, RG.MEASURED_EXAMPLE):
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_bytes((KIT / rel).read_bytes())
    old = repo / "docs/predictions/replaced-0000000"
    old.mkdir(parents=True)
    (old / "summary.json").write_text("{}", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "the registration, and an older one kept as data")
    registered = git("rev-parse", "HEAD")
    monkeypatch.setattr(RB, "REPO", repo)
    kept = RB.snapshot_replaced("f" * 40, supersede=True)
    assert kept == f"docs/predictions/replaced-{REG['artifact']['commit'][:7]}" and not old.exists()
    summary = json.loads((repo / kept / "summary.json").read_text(encoding="utf-8"))
    assert summary["registered_in"] == registered and "stays in the history" in summary["what"] and "superseded" in summary["what"]
    assert RB.drop_removed_replaced() == ["docs/predictions/replaced-0000000/summary.json"]
    assert "D  docs/predictions/replaced-0000000/summary.json" in git("status", "--porcelain")
    assert RB.drop_removed_replaced() == [], "nothing left to drop"
    fresh = RB.snapshot_replaced("f" * 40, supersede=False)
    assert json.loads((repo / fresh / "summary.json").read_text(encoding="utf-8"))["registered_in"] is None, "a registration replaced before any commit has no commit"


def test_the_commit_messages_of_a_superseding_run_say_which_registration_they_supersede(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    folder = repo / "docs/predictions/replaced-cec1bba"
    folder.mkdir(parents=True)
    (folder / "summary.json").write_text(json.dumps({"registered_in": "74118b521fada830b44f12531acad568b4b2afaf"}), encoding="utf-8")
    monkeypatch.setattr(RB, "REPO", repo)
    MJ, AJ = _measured_pair()
    b1, b2 = RB.commit_messages(INPUTS, MJ, AJ, {"events": 41, "fine": 8}, supersede=True)
    assert "second registration" in b1 and "committed as 74118b5" in b1 and "stays in the history" in b1
    assert "supersedes the one against speeds-kit cec1bba (committed as 74118b5)" in b2 and "Both stay in the history" in b2
    c1, c2 = RB.commit_messages(INPUTS, MJ, AJ, {"events": 41, "fine": 8}, supersede=False)
    assert "second registration" not in c1 + c2


def test_a_second_registration_pair_is_amended_against_the_same_head_only(tmp_path, monkeypatch):
    """--replace-previous on a pair that --supersede made keeps it a second registration; against another head it would lose the comparison with the pushed one, so it refuses"""
    repo, kit = tmp_path / "repo", tmp_path / "kit"
    repo.mkdir()
    kit.mkdir()
    git = _git_in(repo)
    git("init", "-q")
    (repo / "README").write_text("base\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    (repo / "a.txt").write_text("1\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", RB.SUBJECT1_NEXT.format(short="be4e324"))
    (repo / RG.PRED).parent.mkdir(parents=True)
    (repo / RG.PRED).write_bytes(PRED.read_bytes())
    git("add", "-A")
    git("commit", "-q", "-m", RB.SUBJECT2_NEXT.format(short="be4e324"))
    assert RB.SECOND_MARK in RB.SUBJECT2_NEXT and RB.SECOND_MARK not in RB.SUBJECT2
    monkeypatch.setattr(RB, "REPO", repo)
    toy_checkout(kit, monkeypatch)
    with pytest.raises(SystemExit, match="second registration"):
        RB.rebuild(kit, commit="b" * 40, make_commits=True, replace_previous=True, trailers=["Key: value"])
    # a pair made for a first registration is not touched by that refusal: its subjects are the first ones
    assert RB.SUBJECT1.startswith(RB.PRIOR_SUBJECTS[0]) and RB.SUBJECT2.startswith(RB.PRIOR_SUBJECTS[1])
    assert RB.SUBJECT1_NEXT.startswith(RB.PRIOR_SUBJECTS[0]) and RB.SUBJECT2_NEXT.startswith(RB.PRIOR_SUBJECTS[1]), "--replace-previous knows both kinds of pair"


def test_the_registration_says_which_version_of_the_file_it_is_when_it_supersedes_a_committed_one():
    base = REG["changes_since_replaced_registration"]["baseline"]
    reg_in = base["registered_in"]
    if not reg_in:
        pytest.skip("the registration it replaces was never committed")
    was = REG["changes_since_replaced_registration"]["scripts"]["before"]["commit"][:7]
    assert "this version of this file" in REG["registered_by"] and reg_in[:7] in REG["registered_by"] and was in REG["registered_by"] and "stays in the history" in REG["registered_by"]
    md = MD.read_text(encoding="utf-8")
    assert "**The commit that adds this version of this file is the registration**" in md and f"was committed as `{reg_in[:7]}` and stays in the history; this one supersedes it" in md
    ops = (KIT / "docs" / "OPERATION-CHAINS.md").read_text(encoding="utf-8")
    assert f"(committed as `{reg_in[:7]}`) is superseded by this one: both stay in the history" in ops
    assert subprocess.run(["git", "cat-file", "-t", reg_in], cwd=str(KIT), capture_output=True, text=True).stdout.strip() in ("commit", ""), "the commit named is one of this repository's (or the clone is shallow)"
