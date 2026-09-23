"""checks/test_explore_text.py -- the test that turns RED when the explore layer is absent.

P1 in docs/OPEN-PROBLEMS.md records why the explore layer stayed unbuilt across sessions: its
requirement lived in prose and each fresh session re-read it as the content-blind, intention-less
smoke layer (README, Falsified row 3). Nothing failed when the layer was missing. This file is
that failure. It calls no model, so it is deterministic and fit for a red/green gate.

The three assertions are the original requirement, restated by the author on 2026-08-30
(docs/EXPLORE-SPEC.md): long recursive click chains; each step carrying an intention formed from
what is visible on the page; state carried across steps. Concretely:
  1. recursion depth >= 3 (three `open` actions in one click chain)
  2. an observation from step k is referenced by a decision at step > k+1 (memory carried)
  3. every `open` targeted a node that was in the previous observation's affordances
A stateless tapper (fixed action sequence, no memory, no affordance parsing) must FAIL here.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from explore_text import (Action, Explorer, Page, ScriptedPolicy,
                          answer_from_memory, note_matching, open_where, zoom_out)

DOC = """# Fixture
Intro line.

## Setup
The session token is 4711 and must be quoted in the results.
See [Results](#results) after setup.

## Results
### Table
Some numbers.
### Discussion
The answer must repeat the token from Setup.

## Appendix
Nothing here.
"""


def goal_directed_policy():
    return ScriptedPolicy([
        zoom_out(),                                            # step 1: look at the TOC
        open_where(lambda t: "Setup" in t),                    # step 2: choose by visible affordance
        note_matching(r"token is (\d+)"),                      # step 3: read a value into memory
        open_where(lambda t: "Results" in t),                  # step 4: follow a visible link/affordance
        open_where(lambda t: "Discussion" in t),               # step 5: recurse one level deeper
        answer_from_memory(3, "token {note}"),                 # step 6: decide using step-3 memory
    ])


def stateless_tapper_policy():
    """The falsified 'blind by default' model: fixed sequence, no memory, no affordance parsing."""
    seq = [Action("open", 2), Action("open", 3), Action("answer", "no idea")]
    it = iter(seq)
    return lambda obs: next(it)


def test_goal_directed_explorer_passes_the_three_frozen_assertions():
    ex = Explorer(Page(DOC), w=10, mem_capacity=5)
    out = ex.run("Quote the session token from Setup inside Discussion.",
                 goal_directed_policy(), max_steps=10, expected="4711")
    assert out["correct"], out
    assert out["depth"] >= 3, "assertion 1: recursion depth >= 3"
    assert 6 in out["memory_refs"], "assertion 2: step-6 decision referenced the step-3 note"
    assert out["affordance_ok"], "assertion 3: every open came from visible affordances"


def test_stateless_tapper_fails():
    ex = Explorer(Page(DOC), w=10)
    out = ex.run("Quote the session token from Setup inside Discussion.",
                 stateless_tapper_policy(), max_steps=10, expected="4711")
    assert not out["correct"]
    assert out["depth"] < 3 or not out["memory_refs"]


def test_affordances_are_parsed_not_hardcoded():
    """Removing the link and the heading from view must make the affordance disappear."""
    ex = Explorer(Page(DOC), w=10)
    obs_toc = ex.observe("t", 1)
    assert any(a["title"] == "Results" for a in obs_toc["affordances"])
    ex.act(Action("open", 2), 2)          # inside Setup: window shows the [Results](#results) link
    obs = ex.observe("t", 3)
    assert any(a.get("via") == "link" and a["title"] == "Results" for a in obs["affordances"])
    ex2 = Explorer(Page(DOC.replace("See [Results](#results) after setup.", "")), w=10)
    ex2.act(Action("open", 2), 2)
    assert not any(a["title"] == "Results" for a in ex2.observe("t", 3)["affordances"])


def test_memory_decay_breaks_long_range_dependence():
    """Dose curve, memory axis: with capacity 1 the step-3 note is gone by step 6 -> LookupError."""
    ex = Explorer(Page(DOC), w=10, mem_capacity=1)
    pol = ScriptedPolicy([
        zoom_out(), open_where(lambda t: "Setup" in t), note_matching(r"token is (\d+)"),
        lambda obs: Action("note", "distractor A"), lambda obs: Action("note", "distractor B"),
        answer_from_memory(3, "token {note}"),
    ])
    with pytest.raises(LookupError):
        ex.run("t", pol, max_steps=10, expected="4711")


def test_window_dropout_can_hide_the_value():
    """Dose curve, attention axis: heavy dropout makes the value invisible -> LookupError."""
    ex = Explorer(Page(DOC), w=10, p_drop=1.0, seed=1)
    pol = ScriptedPolicy([zoom_out(), lambda obs: Action("open", 2), note_matching(r"token is (\d+)")])
    with pytest.raises(LookupError):
        ex.run("t", pol, max_steps=5)
