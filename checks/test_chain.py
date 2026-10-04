"""checks/test_chain.py -- the operation-chain layer: format, load, ten verifiers, fixtures, CLI.

No browser, no model, no network; the whole file runs in about a second (CI job `chains`).
Every verifier has a must-fire case and a must-hold case: a check that cannot fail proves nothing.

  1. the HW1 fixtures: the cheap chain is silent, the expensive chain trips EVERY verifier at exact steps
     (the lists below were worked out by hand from the fixture before any code ran), the fixed flow is silent;
  2. one minimal synthetic chain per verifier: a bad one fires that verifier and no other, a good one is silent;
  3. mutation controls: take the fixed chain, break ONE property, exactly the matching verifier fires;
  4. the format: loud errors naming the step, defaults, shorthand, round trip, blind view, YAML optional;
  5. content-blindness: a tripwire where free text lives, and a mutation of every free-text field;
  6. the load and the budget: every term, the order cheap < fixed < expensive, length never scored;
  7. the CLI `bin/emu chain check`: exit codes 0 / 1 / 2;
  8. the docs cannot rot: the worked example, the flagged-step table, the verifier table, the weights, the ledger ids.
"""
import copy
import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import chain as C                      # noqa: E402
import chain_load as L                 # noqa: E402
import chain_verifiers as V            # noqa: E402

KIT = HERE.parent
FIX = HERE / "fixtures" / "chains"
PROV = {"source": "designed", "date": "2026-10-04", "who": "test"}


# --- helpers -----------------------------------------------------------------------------------------------------
def chain1(*steps, **chain_kw):
    return C.parse({"provenance": PROV, "steps": list(steps), **chain_kw})["chains"][0]


def fired(chain, **kw):
    """{verifier: [steps]} for every verifier that fired on the chain."""
    return V.steps_by_verifier(V.run_chain(chain, **kw)["findings"])


def commit(**kw):
    d = {"op": "COMMIT", "reversibility": "reversible", "preview_before": True, "everything_on_screen": True,
         "verify_after": "correctness"}
    d.update(kw)
    return d


CHECKED = {"op": "VERIFY", "kind": "correctness"}


@pytest.fixture(scope="module")
def hw1():
    return {c["id"]: c for c in C.load(FIX / "hw1_correction_pass.json")["chains"]}


@pytest.fixture(scope="module")
def fixed():
    return C.load(FIX / "hw1_correction_pass_fixed.json")["chains"][0]


# worked out by hand from the fixture (step numbers = lines of the "expensive" chain), then compared with the code
EXPENSIVE = {
    "anchoring": [6, 7, 15, 16, 17, 24, 25],       # SCAN tabs, DISCRIMINATE tabs, ENUMERATE, SCAN names, .js/.json, SCAN Apply, Apply/Scan first
    "memory_budget": [7, 8, 9],                    # demand 5, demand 5, the RELOAD
    "candidate_set": [15],                         # the folder, paged
    "interruption": [2, 4, 9, 20, 28, 31],         # five REFRESH that restore nothing, and leaving to the chat (step 9)
    "colocation": [26],                            # Apply with no preview and not everything on screen
    "progress": [18, 19, 27],                      # TAP with no feedback, two silent WAIT
    "causal": [22],                                # the list of changes: no origin, no exclusions
    "single_path": [14],                           # corrections picker, after Re-sync (step 7) did the same job
    "commit_correctness": [26],                    # Apply: consistency only
    "separators": [11, 12],                        # narrow paragraph, narrow sentence
}


# --- 1. the HW1 fixtures -----------------------------------------------------------------------------------------
def test_hw1_expensive_chain_trips_every_verifier_at_the_exact_steps(hw1):
    got = fired(hw1["expensive"])
    assert set(got) == set(V.VERIFIERS), f"verifiers that did not fire: {set(V.VERIFIERS) - set(got)}"
    assert got == EXPENSIVE


def test_hw1_cheap_chain_has_no_findings(hw1):
    assert V.run_chain(hw1["cheap"])["findings"] == []


def test_fixed_flow_has_no_findings_and_its_memory_stays_within_budget(fixed):
    res = V.run_chain(fixed)
    assert res["findings"] == []
    ld = res["load"]
    assert ld["peak_slots"] <= 3
    assert ld["counts"]["reloads"] == 0 and ld["counts"]["reorients"] == 0     # no RELOAD, no RE-ORIENT


def test_fixed_flow_keeps_the_interruption_probe(fixed):
    """The silence above is only worth something if the fixed chain still contains what the verifiers look at."""
    ops = [s["op"] for s in fixed["steps"]]
    assert "REFRESH" in ops and "WAIT" in ops and ops.count("COMMIT") >= 1 and "VERIFY" in ops
    refresh = next(s for s in fixed["steps"] if s["op"] == "REFRESH")
    assert set(refresh["restores"]) == set(C.LOSSES)


def test_findings_are_one_per_step_per_verifier_sorted_and_in_range(hw1):
    for ch in hw1.values():
        fs = V.run_chain(ch)["findings"]
        keys = [(f["verifier"], f["step"]) for f in fs]
        assert len(keys) == len(set(keys))
        assert [f["step"] for f in fs] == sorted(f["step"] for f in fs)
        assert all(1 <= f["step"] <= len(ch["steps"]) and set(f) == {"verifier", "step", "message"} for f in fs)


def test_repairing_one_property_of_the_expensive_chain_silences_only_that_check(hw1):
    raw = json.loads((FIX / "hw1_correction_pass.json").read_text())
    steps = raw["chains"][1]["steps"]
    steps[14]["set_visibly_complete"] = True                       # step 15: the folder says "all 12 shown"
    got = fired(C.parse(raw)["chains"][1])
    assert "candidate_set" not in got and got["anchoring"] == EXPENSIVE["anchoring"]    # anchoring still fires at 15
    steps[25].update(everything_on_screen=True, preview_before=True)   # step 26: Apply shows everything, previews
    got = fired(C.parse(raw)["chains"][1])
    assert "colocation" not in got and got["commit_correctness"] == [26]


# --- 2. one minimal synthetic chain per verifier ------------------------------------------------------------------
BAD = [   # (case, verifier, steps, steps it must flag)  -- and NO other verifier may fire
    ("anchoring/keyword-among-lookalikes", "anchoring", [{"op": "SCAN", "confusables": [5, 0.9], "anchor": "text-keyword"}], [1]),
    ("anchoring/no-anchor", "anchoring", [{"op": "SCAN", "confusables": [5, 0.9]}], [1]),
    ("anchoring/exactly-at-threshold", "anchoring", [{"op": "DISCRIMINATE", "confusables": [1, 0.5], "anchor": "none"}], [1]),
    ("memory/over-budget", "memory_budget", [{"op": "HOLD", "held": ["a", "b", "c"], "need": 0}, {"op": "READ"}], [2]),
    ("memory/reload-needed", "memory_budget", [{"op": "HOLD", "held": ["a"]}, {"op": "RELOAD", "source": "notes", "held": ["b"]}], [2]),
    ("enumerate/paged", "candidate_set", [{"op": "ENUMERATE", "pages": 3}], [1]),
    ("enumerate/defaults-are-not-visibly-complete", "candidate_set", [{"op": "ENUMERATE"}], [1]),
    ("refresh/restores-nothing", "interruption", [{"op": "REFRESH", "restores": []}], [1]),
    ("refresh/loses-partial-work", "interruption", [{"op": "REFRESH", "restores": ["position", "goal"]}], [1]),
    ("step/declares-interruption", "interruption", [{"op": "READ", "interruption": ["partial"]}], [1]),
    ("reorient/restores-goal-only", "interruption", [{"op": "RE-ORIENT", "restores": ["goal"]}], [1]),
    ("navigate-back/restores-nothing", "interruption", [{"op": "NAVIGATE", "restores": []}], [1]),
    ("commit/not-everything-on-screen", "colocation", [commit(everything_on_screen=False), CHECKED], [1]),
    ("commit/no-preview", "colocation", [commit(preview_before=False), CHECKED], [1]),
    ("wait/no-progress", "progress", [{"op": "WAIT", "progress_visible": False, "view_stable": True}], [1]),
    ("wait/view-moves", "progress", [{"op": "WAIT", "progress_visible": True, "view_stable": False}], [1]),
    ("wait/partial-result-silent", "progress", [{"op": "WAIT", "progress_visible": True, "view_stable": True, "partial_result_says_left": False}], [1]),
    ("tap/no-feedback", "progress", [{"op": "TAP", "feedback": "none"}], [1]),
    ("list/no-origin", "causal", [{"op": "READ", "origin_stated": False, "exclusions_stated": True}], [1]),
    ("list/no-exclusions", "causal", [{"op": "READ", "origin_stated": True, "exclusions_stated": False}], [1]),
    ("prompt/then-infer", "causal", [{"op": "RE-ORIENT", "origin_stated": False, "exclusions_stated": False}, {"op": "INFER"}], [1]),
    ("intent/two-views", "single_path", [{"op": "NAVIGATE", "intent": "load", "view": "a"}, {"op": "NAVIGATE", "intent": "load", "view": "b"}], [2]),
    ("intent/three-views-one-finding", "single_path", [{"op": "NAVIGATE", "intent": "load", "view": v} for v in "abc"], [2]),
    ("commit/consistency-only", "commit_correctness", [commit(verify_after="consistency"), CHECKED], [1]),
    ("commit/never-checked", "commit_correctness", [commit()], [1]),
    ("commit/only-a-consistency-verify-follows", "commit_correctness", [commit(), {"op": "VERIFY", "kind": "consistency"}], [1]),
    ("text/boundary-hidden", "separators", [{"op": "READ", "boundary_visible": False}], [1]),
]

GOOD = [   # every verifier must stay silent
    ("anchoring/anchored-by-position", [{"op": "SCAN", "confusables": [5, 0.9], "anchor": "unique-visual"}]),
    ("anchoring/items-differ-enough", [{"op": "SCAN", "confusables": [5, 0.49], "anchor": "text-keyword"}]),
    ("anchoring/no-lookalikes", [{"op": "SCAN", "anchor": "text-keyword"}]),
    ("memory/exactly-at-budget", [{"op": "HOLD", "held": ["a", "b", "c"], "need": 0}, {"op": "READ", "need": 0}]),
    ("enumerate/visibly-complete", [{"op": "ENUMERATE", "set_visibly_complete": True}]),
    ("refresh/restores-everything", [{"op": "REFRESH", "restores": ["position", "goal", "partial"]}]),
    ("navigate/claims-nothing", [{"op": "NAVIGATE"}, {"op": "RE-ORIENT"}]),
    ("commit/clean", [commit(), CHECKED]),
    ("commit/idempotent-needs-no-preview", [commit(reversibility="idempotent", preview_before=False, verify_after="consistency"),
                                            {"op": "VERIFY", "kind": "consistency"}]),
    ("wait/clean", [{"op": "WAIT", "progress_visible": True, "view_stable": True, "partial_result_says_left": True}]),
    ("wait/yields-no-partial-result", [{"op": "WAIT", "progress_visible": True, "view_stable": True}]),
    ("list/origin-and-exclusions-stated", [{"op": "READ", "origin_stated": True, "exclusions_stated": True}]),
    ("intent/one-view", [{"op": "NAVIGATE", "intent": "load", "view": "a"}, {"op": "TAP", "intent": "load", "view": "a"}]),
    ("intent/two-intents", [{"op": "NAVIGATE", "intent": "load", "view": "a"}, {"op": "NAVIGATE", "intent": "save", "view": "b"}]),
    ("text/boundary-visible", [{"op": "READ", "boundary_visible": True}]),
    ("text/not-declared-block-structured", [{"op": "READ"}]),
]


@pytest.mark.parametrize("case,verifier,steps,expected", BAD, ids=[b[0] for b in BAD])
def test_bad_synthetic_chain_fires_exactly_that_verifier(case, verifier, steps, expected):
    assert fired(chain1(*steps)) == {verifier: expected}


@pytest.mark.parametrize("case,steps", GOOD, ids=[g[0] for g in GOOD])
def test_good_synthetic_chain_is_silent(case, steps):
    assert fired(chain1(*steps)) == {}


def test_anchoring_threshold_is_a_parameter():
    ch = chain1({"op": "SCAN", "confusables": [5, 0.9], "anchor": "text-keyword"})
    assert fired(ch) == {"anchoring": [1]}
    assert fired(ch, lookalike=0.95) == {}


def test_memory_budget_is_a_parameter_and_precedence_is_override_then_chain_then_default():
    held3 = [{"op": "HOLD", "held": ["a", "b", "c"], "need": 0}, {"op": "READ", "need": 0}]
    assert fired(chain1(*held3)) == {}                                  # default B = 3
    assert fired(chain1(*held3), budget=2) == {"memory_budget": [1, 2]}  # override
    assert fired(chain1(*held3, budget=2)) == {"memory_budget": [1, 2]}  # the chain's own budget
    assert fired(chain1(*held3, budget=2), budget=5) == {}               # the override beats the chain's


def test_causal_names_the_infer_only_when_it_is_close():
    near = V.run_chain(chain1({"op": "READ", "origin_stated": False, "exclusions_stated": False}, {"op": "TAP"}, {"op": "INFER"}))
    far = V.run_chain(chain1({"op": "READ", "origin_stated": False, "exclusions_stated": False}, {"op": "TAP"}, {"op": "TAP"},
                             {"op": "TAP"}, {"op": "INFER"}))
    assert "INFER its cause (step 3)" in near["findings"][0]["message"]
    assert "INFER" not in far["findings"][0]["message"]


def test_one_finding_joins_all_reasons_at_a_step():
    fs = V.run_chain(chain1(commit(preview_before=False, everything_on_screen=False), CHECKED))["findings"]
    assert [f["verifier"] for f in fs] == ["colocation"]
    assert "not everything" in fs[0]["message"] and "no preview" in fs[0]["message"]


def test_every_verifier_states_what_it_cannot_see_and_the_order_is_section_5():
    assert list(V.VERIFIERS) == ["anchoring", "memory_budget", "candidate_set", "interruption", "colocation",
                                 "progress", "causal", "single_path", "commit_correctness", "separators"]
    assert [sec for _, sec, _ in V.VERIFIERS.values()] == [f"5.{i}" for i in range(1, 11)]
    for name, (fn, _, _) in V.VERIFIERS.items():
        assert "cannot see" in (fn.__doc__ or "").lower(), f"{name}: the docstring must say what it cannot see"


# --- 3. mutation controls on the fixed flow: break ONE property, exactly the matching verifier fires ----------------
def raw_fixed():
    return json.loads((FIX / "hw1_correction_pass_fixed.json").read_text())


def find(raw, op=None, key=None, nth=1):
    """1-based number of the nth step with the given op and/or carrying the given key."""
    seen = 0
    for i, s in enumerate(raw["chains"][0]["steps"], 1):
        if (op is None or s["op"] == op) and (key is None or key in s):
            seen += 1
            if seen == nth:
                return i
    raise AssertionError(f"the fixed flow has no step with op={op} key={key} (#{nth}); the mutation controls need one")


def _step(raw, i):
    return raw["chains"][0]["steps"][i - 1]


def mut_anchoring(raw):
    i = find(raw, "ANCHOR")           # the button is no longer found by position: it is read among look-alikes,
    _step(raw, i).update(op="SCAN", anchor="text-keyword", confusables=[3, 0.8])   # i.e. a SCAN (an ANCHOR step may not be read)
    return {"anchoring": [i]}


def mut_memory(raw):
    i = find(raw, "COMMIT")
    _step(raw, i)["need"] = 3                                       # 3 needed + 1 held = 4 > B
    return {"memory_budget": [i]}


def mut_candidate_set(raw):
    i = find(raw, "READ")
    raw["chains"][0]["steps"].insert(i, {"op": "ENUMERATE", "pages": 2})   # a paged list appears after the first READ
    return {"candidate_set": [i + 1]}


def mut_interruption(raw):
    i = find(raw, "REFRESH")
    _step(raw, i)["restores"] = ["position", "goal"]
    return {"interruption": [i]}


def mut_colocation(raw):
    i = find(raw, "COMMIT")
    _step(raw, i)["everything_on_screen"] = False
    return {"colocation": [i]}


def mut_progress(raw):
    i = find(raw, "WAIT")
    _step(raw, i)["view_stable"] = False
    return {"progress": [i]}


def mut_causal(raw):
    i = find(raw, key="origin_stated")
    _step(raw, i)["origin_stated"] = False
    return {"causal": [i]}


def mut_single_path(raw):
    i = find(raw, "COMMIT", nth=2)
    _step(raw, i)["view"] = "somewhere-else"
    return {"single_path": [i]}


def mut_commit_correctness(raw):
    i = find(raw, "COMMIT")
    _step(raw, i)["verify_after"] = "consistency"
    return {"commit_correctness": [i]}


def mut_separators(raw):
    i = find(raw, key="boundary_visible")
    _step(raw, i)["boundary_visible"] = False
    return {"separators": [i]}


MUTATIONS = [mut_anchoring, mut_memory, mut_candidate_set, mut_interruption, mut_colocation, mut_progress,
             mut_causal, mut_single_path, mut_commit_correctness, mut_separators]


@pytest.mark.parametrize("mutate", MUTATIONS, ids=[m.__name__[4:] for m in MUTATIONS])
def test_breaking_one_property_of_the_fixed_flow_fires_exactly_the_matching_verifier(mutate):
    raw = raw_fixed()
    expected = mutate(raw)
    assert fired(C.parse(raw)["chains"][0]) == expected


def test_mutation_controls_cover_every_verifier():
    covered = set()
    for m in MUTATIONS:
        covered |= set(m(raw_fixed()))
    assert covered == set(V.VERIFIERS)


# --- 4. the format ------------------------------------------------------------------------------------------------
def raw1(*steps, **kw):
    return {"provenance": PROV, "steps": list(steps), **kw}


def problems(raw):
    with pytest.raises(C.ChainError) as e:
        C.parse(raw)
    return e.value.problems


def test_unknown_op_names_the_step_and_suggests_the_right_one():
    p = problems(raw1({"op": "READ"}, {"op": "ANCOR"}))
    assert len(p) == 1 and "step 2" in p[0] and "unknown op" in p[0] and "did you mean 'ANCHOR'" in p[0]


BAD_VALUES = [   # (step, what the message must contain)
    ({"op": "READ", "anchor": "left"}, "`anchor`"),
    ({"op": "READ", "reading": "loud"}, "`reading`"),
    ({"op": "READ", "feedback": "slow"}, "`feedback`"),
    ({"op": "READ", "reversibility": "maybe"}, "`reversibility`"),
    ({"op": "READ", "interruption": ["mood"]}, "`interruption`"),
    ({"op": "READ", "times": 0}, "`times`"),
    ({"op": "READ", "amount": -1}, "`amount`"),
    ({"op": "READ", "amount": True}, "`amount`"),                       # bool is not a number here
    ({"op": "READ", "need": "two"}, "`need`"),
    ({"op": "READ", "held": ["a", "a"]}, "`held`"),
    ({"op": "READ", "held": [""]}, "`held`"),
    ({"op": "READ", "reading": "none", "amount": 3}, "`amount`"),
    ({"op": "SCAN", "confusables": [3]}, "`confusables`"),
    ({"op": "SCAN", "confusables": [3, 1.5]}, "`confusables`"),
    ({"op": "SCAN", "confusables": [-1, 0.5]}, "`confusables`"),
    ({"op": "SCAN", "confusables": {"count": 3}}, "`confusables`"),     # a count without a similarity
    ({"op": "WAIT", "progress_visible": "yes", "view_stable": True}, "`progress_visible`"),
    ({"op": "COMMIT", "reversibility": "reversible", "preview_before": True, "everything_on_screen": True,
      "verify_after": "perfect"}, "`verify_after`"),
    ({"op": "VERIFY", "kind": "vibes"}, "`kind`"),
    ({"op": "REFRESH", "restores": ["position", "position"]}, "`restores`"),
    ({"op": "ENUMERATE", "pages": 0}, "`pages`"),
    ({"op": "READ", "origin_stated": "no", "exclusions_stated": True}, "`origin_stated`"),
]


@pytest.mark.parametrize("step,needle", BAD_VALUES, ids=[f"{s['op']}:{n}" for s, n in BAD_VALUES])
def test_bad_property_value_is_a_loud_error_naming_the_step(step, needle):
    p = problems(raw1({"op": "TAP"}, step))
    assert p and all("step 2" in x for x in p) and any(needle in x for x in p)


REQUIRED_MISSING = [
    ({"op": "ANCHOR"}, "anchor"), ({"op": "DISCRIMINATE"}, "confusables"), ({"op": "RELOAD", "held": ["a"]}, "source"),
    ({"op": "REFRESH"}, "restores"), ({"op": "VERIFY"}, "kind"), ({"op": "WAIT", "view_stable": True}, "progress_visible"),
    ({"op": "WAIT", "progress_visible": True}, "view_stable"), ({"op": "COMMIT"}, "preview_before"),
    ({"op": "COMMIT"}, "everything_on_screen"), ({"op": "COMMIT"}, "verify_after"), ({"op": "COMMIT"}, "reversibility"),
]


@pytest.mark.parametrize("step,key", REQUIRED_MISSING, ids=[f"{s['op']}-{k}" for s, k in REQUIRED_MISSING])
def test_a_missing_required_key_is_loud_and_names_the_step(step, key):
    p = problems(raw1({"op": "TAP"}, {"op": "TAP"}, step))
    assert any("step 3" in x and f"missing required key `{key}`" in x for x in p)


def test_unknown_key_is_rejected_with_a_hint_and_a_key_on_the_wrong_op_too():
    p = problems(raw1({"op": "READ", "anchro": "edge"}))
    assert "unknown key `anchro`" in p[0] and "did you mean 'anchor'" in p[0]
    p = problems(raw1({"op": "READ", "preview_before": True}))
    assert "only applies to COMMIT" in p[0] and "step 1" in p[0]


def test_an_anchor_step_cannot_be_found_by_reading():
    for a in ("text-keyword", "none"):
        assert "make it a SCAN" in problems(raw1({"op": "ANCHOR", "anchor": a}))[0]
    assert chain1({"op": "ANCHOR", "anchor": "edge"})["steps"][0]["anchor"] == "edge"


def test_discriminate_needs_a_lookalike():
    assert "at least one look-alike" in problems(raw1({"op": "DISCRIMINATE", "confusables": [0, 0]}))[0]


def test_hold_keyify_and_reload_must_change_what_is_held():
    for step in ({"op": "HOLD"}, {"op": "KEYIFY"}, {"op": "RELOAD", "source": "chat"}, {"op": "HOLD", "held": []}):
        assert "must change what is held" in problems(raw1(step))[0]
    ok = chain1({"op": "HOLD", "held": ["goal"]}, {"op": "KEYIFY", "held": ["key"]})
    assert ok["steps"][1]["held"] == ["key"]


def test_intent_needs_a_view_and_a_list_step_needs_both_stated_keys():
    assert "`intent` needs `view`" in problems(raw1({"op": "NAVIGATE", "intent": "load"}))[0]
    assert "BOTH" in problems(raw1({"op": "READ", "origin_stated": True}))[0]
    assert "BOTH" in problems(raw1({"op": "READ", "exclusions_stated": True}))[0]


def test_provenance_is_required_and_checked():
    base = {"steps": [{"op": "READ"}]}
    assert len(problems(base)) == 3                                           # source, date, who
    for bad in ({"source": "dreamt", "date": "2026-10-04", "who": "x"}, {"source": "narrated", "date": "2026-02-30", "who": "x"},
                {"source": "narrated", "date": "yesterday", "who": "x"}, {"source": "narrated", "date": "2026-10-04", "who": " "},
                {"source": "narrated", "date": "2026-10-04", "who": "x", "colour": "red"}):
        assert problems({**base, "provenance": bad})
    # a file-level provenance is inherited by each chain; a chain's own keys override it key by key
    d = C.parse({"provenance": PROV, "chains": [{"id": "a", "steps": ["READ x"]},
                                                 {"id": "b", "provenance": {"source": "captured"}, "steps": ["READ x"]}]})
    assert [c["provenance"]["source"] for c in d["chains"]] == ["designed", "captured"]
    assert d["chains"][1]["provenance"]["date"] == "2026-10-04"


def test_file_level_problems():
    assert "non-empty list" in problems(raw1())[0]
    assert any("not both" in x for x in problems({"provenance": PROV, "steps": ["READ x"], "chains": [{"id": "a", "steps": ["READ x"]}]}))
    assert any("more than once" in x for x in problems({"provenance": PROV, "chains": [{"id": "a", "steps": ["READ x"]}, {"id": "a", "steps": ["READ x"]}]}))
    assert any("need an `id`" in x for x in problems({"provenance": PROV, "chains": [{"steps": ["READ x"]}, {"steps": ["READ y"]}]}))
    assert any("unknown key `stepz`" in x and "did you mean 'steps'" in x for x in problems({"provenance": PROV, "stepz": []}))
    assert any("unknown `format`" in x for x in problems({**raw1("READ x"), "format": "emu-chain/9"}))
    assert any("must be a JSON object" in x for x in problems([]))
    assert any("`budget`" in x for x in problems({**raw1("READ x"), "budget": 0}))


def test_all_problems_are_reported_in_one_pass_each_naming_its_step():
    p = problems(raw1({"op": "READ"}, {"op": "ANCOR"}, {"op": "COMMIT"}, "TAPP the thing", {"op": "WAIT"}))
    for n in (2, 3, 4, 5):
        assert any(f"step {n}" in x for x in p), f"no problem names step {n}: {p}"
    assert len(p) >= 8


def test_n_must_match_the_position_and_ops_may_be_written_in_lower_case_or_as_reorient():
    assert "`n` is 7" in problems(raw1({"op": "READ", "n": 7}))[0]
    ch = chain1("read the list", "reorient where am I", {"op": "re-orient"})
    assert [s["op"] for s in ch["steps"]] == ["READ", "RE-ORIENT", "RE-ORIENT"]


def test_shorthand_string_step_is_op_then_free_text():
    s = chain1("READ the first line")["steps"][0]
    assert s["op"] == "READ" and s["text"]["target"] == "the first line"
    assert "step 1" in problems(raw1("TAPP the thing"))[0]


def test_json_text_errors_are_loud_and_duplicate_keys_do_not_win_silently():
    with pytest.raises(C.ChainError, match="not valid JSON"):
        C.load_text('{"steps": [')
    with pytest.raises(C.ChainError, match="duplicate key 'held'"):
        C.load_text('{"steps": [{"op": "READ", "held": ["a"], "held": []}]}')
    with pytest.raises(C.ChainError, match="NaN"):
        C.load_text('{"steps": [{"op": "READ", "amount": NaN}]}')
    with pytest.raises(C.ChainError, match="cannot read"):
        C.load(FIX / "no_such_file.json")


def test_plain_step_defaults():
    s = chain1({"op": "READ"}, {"op": "ANCHOR", "anchor": "edge"}, {"op": "SCAN"}, {"op": "TAP"},
               {"op": "DISCRIMINATE", "confusables": [2, 0.7]})["steps"]
    r, a, sc, tap, d = s
    assert (r["need"], r["reading"], r["amount"], r["feedback"], r["reversibility"], r["held"], r["interruption"],
            r["times"], r["anchor"], r["intent"], r["view"]) == (1, "fine", 1.0, "immediate", "idempotent", [], [], 1, "none", None, None)
    assert (a["need"], a["reading"], a["amount"]) == (0, "none", 0.0)
    assert (sc["need"], sc["reading"]) == (1, "coarse") and (tap["need"], tap["reading"]) == (0, "none")
    assert d["need"] == 3 and d["confusables"] == {"count": 2, "similarity": 0.7}      # the target plus its look-alikes


def test_held_is_inherited_until_changed_and_an_empty_list_clears_it():
    ch = chain1({"op": "HOLD", "held": ["goal"]}, {"op": "READ"}, {"op": "READ", "held": ["goal", "x"]}, {"op": "READ"},
                {"op": "READ", "held": []}, {"op": "READ"})
    assert [len(s["held"]) for s in ch["steps"]] == [1, 1, 2, 2, 0, 0]


def test_round_trip_is_idempotent():
    for name in ("hw1_correction_pass.json", "hw1_correction_pass_fixed.json"):
        d = C.load(FIX / name)
        assert C.parse(json.loads(C.dumps(d))) == d
    every_key = chain1({"op": "HOLD", "held": ["g"], "intent": "i", "view": "v", "target": "t", "note": "n"},
                       {"op": "ENUMERATE", "pages": 2, "set_visibly_complete": True, "origin_stated": True, "exclusions_stated": False},
                       {"op": "RELOAD", "source": "chat", "held": ["h"], "interruption": ["goal"]},
                       {"op": "REFRESH", "restores": ["goal"]}, {"op": "RE-ORIENT", "restores": []},
                       {"op": "WAIT", "progress_visible": True, "view_stable": False, "partial_result_says_left": True},
                       commit(), {"op": "VERIFY", "kind": "correctness", "boundary_visible": True}, budget=4)
    d = {"format": C.FORMAT, "chains": [every_key]}
    assert C.parse(json.loads(C.dumps(d))) == d


def test_blind_removes_free_text_and_keeps_structure():
    d = C.load(FIX / "hw1_correction_pass.json")
    ch = d["chains"][1]
    assert ch["steps"][0]["text"]["target"] and ch["text"]["task"] and ch["provenance"]["text"]["who"]
    b = C.blind(ch)
    assert "text" not in b and "text" not in b["provenance"] and all("text" not in s for s in b["steps"])
    assert b["provenance"] == {"source": "narrated", "date": "2026-10-03"}
    assert [{k: v for k, v in s.items() if k != "text"} for s in ch["steps"]] == b["steps"]
    assert "text" in ch["steps"][0]                      # the original is untouched


def test_yaml_is_optional_never_required(monkeypatch):
    text = "provenance: {source: designed, date: '2026-10-04', who: test}\nsteps:\n  - {op: READ, target: x}\n  - SCAN a list\n"
    monkeypatch.setitem(sys.modules, "yaml", None)          # `import yaml` now raises ImportError
    with pytest.raises(C.ChainError, match="PyYAML"):
        C.load_text(text, "yaml")
    monkeypatch.undo()
    try:
        import yaml                                          # noqa: F401  (optional; its absence is the normal case in CI)
    except ImportError:
        pytest.skip("PyYAML is not installed: the loud error above is the whole contract then")
    assert [s["op"] for s in C.load_text(text, "yaml")["chains"][0]["steps"]] == ["READ", "SCAN"]


# --- 5. content-blindness -------------------------------------------------------------------------------------------
def test_verifiers_and_load_never_read_free_text(hw1, fixed):
    for ch in list(hw1.values()) + [fixed]:
        trapped = C.blind(ch, trap=True)
        for name, (fn, _, _) in V.VERIFIERS.items():
            fn(trapped, V.Config())                          # an AssertionError here means this verifier peeked
        L.chain_load(trapped)
        L.working_sets(trapped)


def test_the_tripwire_fires_on_every_way_of_peeking(hw1):
    peeks = [lambda t: t["target"], lambda t: t.get("target"), lambda t: list(t), lambda t: "target" in t,
             lambda t: len(t), lambda t: bool(t), lambda t: t.items()]
    for peek in peeks:
        trapped = C.blind(hw1["cheap"], trap=True)
        with pytest.raises(AssertionError, match="content-blind"):
            peek(trapped["steps"][0]["text"])
    with pytest.raises(KeyError):                             # the plain blind view has no text at all
        C.blind(hw1["cheap"])["steps"][0]["text"]


def test_run_chain_hands_every_verifier_the_blind_chain_only(monkeypatch, hw1):
    """The tripwire above calls verifiers directly; this one proves the RUNNER blinds before it calls them."""
    def nosy(chain, cfg):
        return [{"verifier": "anchoring", "step": 1, "message": chain["steps"][0]["text"]["target"]}]
    full = hw1["cheap"]
    assert nosy(full, V.Config())[0]["message"]                          # control: on the full chain the peek works
    monkeypatch.setitem(V.VERIFIERS, "nosy", (nosy, "5.x", "#0"))
    with pytest.raises(KeyError):                                         # on the runner's view the text is gone
        V.run_chain(full)


def _scramble(raw, rng):
    def noise():
        return "".join(rng.choice("abcxyz ") for _ in range(30))
    raw["provenance"]["who"], raw["provenance"]["note"] = noise(), noise()
    for ch in raw["chains"]:
        ch["task"], ch["notes"] = noise(), noise()
        for s in ch["steps"]:
            s["target"], s["note"] = noise(), noise()
    return raw


@pytest.mark.parametrize("name", ["hw1_correction_pass.json", "hw1_correction_pass_fixed.json"])
def test_findings_and_load_do_not_depend_on_any_free_text(name):
    raw = json.loads((FIX / name).read_text())
    before = V.check_doc(C.parse(copy.deepcopy(raw)))
    after = V.check_doc(C.parse(_scramble(copy.deepcopy(raw), random.Random(7))))
    assert before == after                                    # findings (messages included) and the whole load


# --- 6. the load and the budget -----------------------------------------------------------------------------------
def load_of(*steps, **kw):
    return L.chain_load(chain1(*steps, **kw))


def test_reading_weights_fine_and_coarse_items_differently():
    ld = load_of({"op": "SCAN", "amount": 8}, {"op": "READ", "amount": 3})
    assert (ld["counts"]["read_coarse"], ld["counts"]["read_fine"]) == (8, 3)
    assert ld["terms"]["reading"] == pytest.approx(8 * L.WEIGHTS["read_coarse"] + 3 * L.WEIGHTS["read_fine"])


def test_slot_steps_sum_what_is_held_across_each_step_times_repeats():
    ld = load_of({"op": "HOLD", "held": ["a", "b"], "need": 0}, {"op": "ANCHOR", "anchor": "edge"},
                 {"op": "ANCHOR", "anchor": "edge", "times": 4})
    assert ld["counts"]["slot_steps"] == 2 + 2 + 2 * 4 and ld["terms"]["slot_steps"] == 12 * L.WEIGHTS["slot_step"]


def test_reload_and_reorient_are_counted_with_repeats():
    ld = load_of({"op": "HOLD", "held": ["a"]}, {"op": "RELOAD", "source": "chat", "held": ["b"], "times": 2}, {"op": "RE-ORIENT", "times": 3})
    assert (ld["counts"]["reloads"], ld["counts"]["reorients"]) == (2, 3)
    assert ld["terms"]["reload"] == 2 * L.WEIGHTS["reload"] and ld["terms"]["reorient"] == 3 * L.WEIGHTS["reorient"]


def test_discriminate_is_weighted_by_similarity():
    ld = load_of({"op": "DISCRIMINATE", "confusables": [1, 0.8], "anchor": "edge"},
                 {"op": "DISCRIMINATE", "confusables": [2, 0.5], "anchor": "edge", "times": 2})
    assert ld["counts"]["discriminate_similarity"] == pytest.approx(0.8 + 0.5 * 2)
    assert ld["terms"]["discriminate"] == pytest.approx(1.8 * L.WEIGHTS["discriminate"])


def test_a_loop_is_a_refresh_right_after_a_wait_or_a_verify():
    wait = {"op": "WAIT", "progress_visible": True, "view_stable": True}
    ld = load_of(wait, {"op": "REFRESH", "restores": []}, commit(), {"op": "REFRESH", "restores": []},
                 {"op": "VERIFY", "kind": "consistency"}, {"op": "REFRESH", "restores": [], "times": 3})
    assert ld["counts"]["loops"] == 1 + 0 + 3            # after the WAIT, not after the COMMIT, after the VERIFY (x3)


def test_length_is_reported_never_scored():
    short, long_ = load_of(*[{"op": "ANCHOR", "anchor": "edge"}] * 3), load_of(*[{"op": "ANCHOR", "anchor": "edge"}] * 50)
    assert (short["steps"], long_["steps"]) == (3, 50) and short["load"] == long_["load"] == 0
    assert "steps" not in L.chain_load(chain1("READ x"))["terms"]


def test_weights_are_explicit_and_overridable():
    assert set(L.WEIGHTS) == {"read_fine", "read_coarse", "slot_step", "reload", "reorient", "discriminate", "loop"}
    ch = chain1({"op": "HOLD", "held": ["a"]}, {"op": "RELOAD", "source": "chat", "held": ["b"]})
    assert L.chain_load(ch)["terms"]["reload"] == L.WEIGHTS["reload"]
    assert L.chain_load(ch, weights={"reload": 0})["terms"]["reload"] == 0


def test_hw1_load_components_are_the_hand_computed_numbers(hw1):
    cheap, exp = L.chain_load(hw1["cheap"]), L.chain_load(hw1["expensive"])
    assert cheap["load"] == pytest.approx(2.5) and cheap["peak_slots"] == 1 and cheap["steps"] == 6
    assert exp["terms"] == pytest.approx({"reading": 70.75, "slot_steps": 46.0, "reload": 6.0, "reorient": 18.0,
                                          "discriminate": 7.65, "loops": 12.0})
    assert exp["load"] == pytest.approx(160.4) and exp["steps"] == 34
    assert (exp["peak_slots"], exp["peak_held"], exp["over_budget_steps"]) == (5, 4, [7, 8])
    assert (exp["counts"]["reloads"], exp["counts"]["reorients"], exp["counts"]["loops"]) == (1, 6, 6)


def test_load_order_is_cheap_then_fixed_then_expensive(hw1, fixed):
    cheap, fx, exp = (L.chain_load(c)["load"] for c in (hw1["cheap"], fixed, hw1["expensive"]))
    assert 0 < cheap < fx < exp


# --- 7. the CLI: bin/emu chain check ----------------------------------------------------------------------------------
def emu(*args):
    p = subprocess.run(["bash", str(KIT / "bin" / "emu"), "chain", *map(str, args)], capture_output=True, text=True,
                       cwd=str(KIT), timeout=60)
    return p.returncode, p.stdout, p.stderr


def test_cli_exits_0_on_the_fixed_flow_and_1_on_the_recorded_chain():
    rc, out, _ = emu("check", FIX / "hw1_correction_pass_fixed.json")
    assert rc == 0 and "no findings" in out and out.rstrip().splitlines()[-1].startswith("PASS")
    rc, out, _ = emu("check", FIX / "hw1_correction_pass.json")
    assert rc == 1 and "26 finding(s)" in out and "FAIL" in out
    rc, out, _ = emu("check", FIX / "hw1_correction_pass.json", "--chain", "cheap")
    assert rc == 0 and "26 finding" not in out
    rc, _, _ = emu("check", FIX / "hw1_correction_pass_fixed.json", FIX / "hw1_correction_pass.json")
    assert rc == 1                                           # several files: any finding fails the run


def test_cli_json_is_the_same_findings_without_any_free_text():
    rc, out, _ = emu("check", FIX / "hw1_correction_pass.json", "--json")
    d = json.loads(out)
    assert rc == 1 and d["ok"] is False and d["findings"] == 26
    cheap, exp = d["files"][0]["chains"]
    assert cheap["ok"] and not cheap["findings"] and not exp["ok"] and len(exp["findings"]) == 26
    assert all(set(f) == {"verifier", "step", "message"} for f in exp["findings"])
    assert exp["findings"] == V.run_chain(C.load(FIX / "hw1_correction_pass.json")["chains"][1])["findings"]
    assert exp["peak_slots"] == 5 and exp["over_budget_steps"] == [7, 8] and exp["budget"] == 3


def test_cli_budget_overrides_the_default():
    rc, out, _ = emu("check", FIX / "hw1_correction_pass_fixed.json", "--budget", 1)
    assert rc == 1 and "memory_budget" in out and "B=1" in out
    assert emu("check", FIX / "hw1_correction_pass_fixed.json", "--budget", 0)[0] == 2


def test_cli_exits_2_on_an_invalid_file_and_lists_the_problems_with_their_steps(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(raw1({"op": "READ"}, {"op": "ANCOR"}, {"op": "COMMIT"})))
    rc, out, err = emu("check", bad)
    assert rc == 2 and "step 2" in err and "step 3" in err and out == ""
    rc, out, _ = emu("check", bad, "--json")
    assert rc == 2 and json.loads(out)["ok"] is False and len(json.loads(out)["error"]["problems"]) >= 2
    assert emu("check", tmp_path / "missing.json")[0] == 2
    assert emu("check", FIX / "hw1_correction_pass.json", "--chain", "nope")[0] == 2
    assert emu()[0] == 2


def test_nested_text_must_be_strings_so_a_bad_value_is_exit_2_and_never_a_crash(tmp_path):
    """Codex review of PR #43: {"text": {"target": 123}} used to parse, and the report's len() then crashed with a
    traceback, whose exit code (1) is the code for "findings".  The normalised form is checked like the written one."""
    bad_commit = commit(reversibility="irreversible", preview_before=False, everything_on_screen=False, verify_after="none")
    cases = [({"target": 123}, "text.target"), ({"note": ["x"]}, "text.note"), ({"targt": "x"}, "text.targt"),
             ("oops", "`text` must be an object")]
    f = tmp_path / "t.json"
    for bad, needle in cases:
        raw = raw1({**bad_commit, "text": bad})
        with pytest.raises(C.ChainError) as e:
            C.parse(raw)
        assert needle in str(e.value) and "step 1" in str(e.value)
        f.write_text(json.dumps(raw))
        rc, out, err = emu("check", f)
        assert rc == 2 and needle in err and "Traceback" not in err and out == ""
    with pytest.raises(C.ChainError) as e:                              # the same hole in the provenance's note
        C.parse(raw1(CHECKED, **{"provenance": {**PROV, "note": 5}}))
    assert "provenance `note` must be a string" in str(e.value)
    ok = C.parse(raw1({**bad_commit, "target": "Apply", "note": "n"}))   # the normalised form still round-trips
    assert C.parse(json.loads(C.dumps(ok))) == ok
    f.write_text(json.dumps(raw1({**bad_commit, "text": {"target": "Apply", "note": "n"}})))
    assert emu("check", f)[0] == 1                                       # valid text, real findings: still exit 1


def test_cli_chain_selector_spans_all_the_input_files():
    """Codex review of PR #43: `--chain cheap a.json b.json` was refused because b.json has no `cheap`."""
    a, b = FIX / "hw1_correction_pass.json", FIX / "hw1_correction_pass_fixed.json"      # a: cheap + expensive; b: fixed
    rc, out, _ = emu("check", a, b, "--chain", "cheap")
    assert rc == 0 and "cheap" in out and "expensive" not in out and b.name not in out
    rc, out, _ = emu("check", a, b, "--chain", "cheap", "--chain", "fixed")
    assert rc == 0 and "cheap" in out and "fixed" in out
    rc, out, _ = emu("check", b, a, "--chain", "expensive")                              # file order does not matter
    assert rc == 1 and "26 finding(s)" in out and b.name not in out
    rc, out, err = emu("check", a, b, "--chain", "nosuch")
    assert rc == 2 and "'nosuch'" in err and "in any file" in err and out == ""
    rc, out, _ = emu("check", a, b, "--chain", "cheap", "--chain", "nosuch", "--json")   # one unknown id refuses the run
    assert rc == 2 and json.loads(out)["error"]["file"] is None and "'nosuch'" in json.loads(out)["error"]["problems"][0]


def test_a_crash_in_the_checker_is_exit_2_never_exit_1(monkeypatch, capsys):
    """An uncaught exception exits 1 in Python, and exit 1 here means "the chain has findings"."""
    import chain_check as K
    fixed = str(FIX / "hw1_correction_pass_fixed.json")

    def boom(*a, **k):
        raise RuntimeError("deliberate")
    monkeypatch.setattr(K.V, "run_chain", boom)
    assert K.cli(["check", fixed]) == 2
    err = capsys.readouterr().err
    assert "chain-internal" in err and "RuntimeError" in err and "not a finding" in err
    monkeypatch.undo()
    assert K.cli(["check", fixed]) == 0
    with pytest.raises(SystemExit) as e:                                                  # usage errors keep argparse's exit 2
        K.cli(["check"])
    assert e.value.code == 2


def test_bin_emu_dispatches_chain_before_it_needs_an_artifact_and_keeps_its_other_modes():
    src = (KIT / "bin" / "emu").read_text()
    assert src.index('"$MODE" = chain') < src.index('ART="${1:?')            # no artifact, no sync, no server
    for mode in ("smoke)", "audit)", "shots)", "step)"):
        assert mode in src
    p = subprocess.run(["bash", str(KIT / "bin" / "emu")], capture_output=True, text=True, cwd=str(KIT), timeout=30)
    assert p.returncode != 0 and "chain" in p.stderr



# --- 8. the docs cannot rot -------------------------------------------------------------------------------------------
DOC = (KIT / "docs" / "OPERATION-CHAINS.md").read_text(encoding="utf-8")
LEDGER = [("operation chains cannot yet be captured from a driven session", "9d8b"),
          ("chain verifiers read declared properties, so a chain can pass by omission", "02be"),
          ("the chain load weights are ordinal and uncalibrated", "67a1")]


def _block(marker, fence):
    m = re.search(rf"<!-- {marker} -->\n```{fence}\n(.*?)\n```", DOC, re.S)
    assert m, f"docs/OPERATION-CHAINS.md lost its {marker} block"
    return m.group(1)


def test_docs_worked_example_is_the_fixture_and_its_report_is_the_real_output():
    assert json.loads(_block("worked-example:json", "json")) == json.loads((FIX / "worked_example.json").read_text())
    rc, out, _ = emu("check", "checks/fixtures/chains/worked_example.json")
    assert rc == 1 and out.rstrip("\n") == _block("worked-example:output", "")
    assert fired(C.load(FIX / "worked_example.json")["chains"][0]) == {"anchoring": [3], "progress": [7], "interruption": [8]}


def test_docs_captured_chain_example_loads_and_shows_the_budget_at_n_equals_2():
    ch = C.parse(json.loads(_block("captured-example:json", "json")))["chains"][0]
    assert ch["budget"] == 2 and ch["provenance"]["source"] == "captured"
    assert fired(ch) == {"anchoring": [2], "memory_budget": [2, 5]}      # the SCAN overflows N=2; the RELOAD
    assert fired(ch, budget=5) == {"anchoring": [2], "memory_budget": [5]}   # only the RELOAD remains with room to spare


def test_docs_flagged_step_table_is_the_one_this_file_asserts():
    rows = {m.group(1): [int(x) for x in m.group(2).split(",")]
            for m in re.finditer(r"^\| `(\w+)` \| ([0-9, ]+) \|", DOC, re.M) if m.group(1) in V.VERIFIERS}
    assert rows == EXPENSIVE


def test_docs_verifier_table_names_every_verifier_with_its_section_and_issue():
    for name, (_, sec, issue) in V.VERIFIERS.items():
        assert re.search(rf"^\| `{name}` \| {re.escape(sec)} \| {re.escape(issue)}", DOC, re.M), f"{name} {sec} {issue}"


def test_docs_state_every_weight_with_its_value():
    for k, v in L.WEIGHTS.items():
        m = re.search(rf"`{k}` ([0-9.]+)", DOC)
        assert m and float(m.group(1)) == v, f"docs disagree with WEIGHTS[{k!r}] = {v}"


def test_docs_numbers_for_the_recorded_chains_match_the_run(hw1):
    for cid in ("cheap", "expensive"):
        m = re.search(rf"^\| `{cid}` \| (\d+) \| ([0-9.]+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|", DOC, re.M)
        assert m, f"no numbers row for {cid} in the docs"
        ld, n = L.chain_load(hw1[cid]), len(V.run_chain(hw1[cid])["findings"])
        assert (int(m[1]), float(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6])) == (
            ld["steps"], round(ld["load"], 2), ld["peak_slots"], ld["counts"]["reloads"], ld["counts"]["reorients"], n)


def test_ledger_entries_exist_with_content_derived_ids_and_the_docs_name_them():
    ledger = (KIT / "docs" / "OPEN-PROBLEMS.md").read_text(encoding="utf-8")
    for title, pid in LEDGER:
        assert hashlib.sha1(title.encode()).hexdigest()[:4] == pid                    # CONTRIBUTING rule 6
        assert re.search(rf"^## P-{pid} — .* `OPEN`$", ledger, re.M)
        assert f'sha1("{title}")' in ledger and f"`P-{pid}`" in DOC
    assert "P-2a7c" in DOC and "## P-2a7c" not in ledger     # PR #42 owns that entry: referenced here, not duplicated


def test_readme_tree_and_ci_point_at_the_layer():
    readme = (KIT / "README.md").read_text(encoding="utf-8")
    for needle in ("step | chain", "chain.py", "chain_verifiers.py", "docs/OPERATION-CHAINS.md", "bin/emu chain check"):
        assert needle in readme, needle
    assert "OPERATION-CHAINS.md" in (KIT / "docs" / "TREE.md").read_text(encoding="utf-8")    # gen_tree --check asserts the rest
    ci = (KIT / ".github" / "workflows" / "claims.yml").read_text(encoding="utf-8")
    seg = ci.split("\n  chains:")[1].split("\n  figbank:")[0]
    cmds = [l for l in seg.splitlines() if l.strip().startswith("- ")]
    assert any("pytest -q checks/test_chain.py" in l for l in cmds)
    assert not any("playwright" in l.lower() or "chromium" in l.lower() for l in cmds)        # no browser in this job
