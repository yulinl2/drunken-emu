#!/usr/bin/env python3
"""checks/chain_load.py -- what a chain costs a person: the load, and the working-memory budget.  Stdlib only.

OPERATION-MODEL section 3:

    chain load ~ reading + sum(slots x steps held) + RELOADs + RE-ORIENTs
                 + DISCRIMINATEs x similarity + WAIT/VERIFY loops

This file turns each term into a number with an explicit weight, and reports the components next to ONE number.

    term           what is counted                                              weight (WEIGHTS)
    -------------  -----------------------------------------------------------  ----------------
    reading        fine-read items x 1.0, coarse-read items x 0.25              read_fine / read_coarse
    slot_steps     sum over steps of (items held across the step) x times        slot_step
    reload         RELOAD steps (x times)                                        reload
    reorient       RE-ORIENT steps (x times)                                     reorient
    discriminate   sum of the look-alike similarity (0..1) of DISCRIMINATE steps discriminate
    loops          REFRESH steps directly after a WAIT, a VERIFY, or a REFRESH that was one (x times)   loop

`times: n` on a step is n consecutive copies of it in EVERY row above: a chain with `times` and the same chain written
out step by step have the same components (a test asserts it), so "WAIT, REFRESH x3" and "WAIT, REFRESH, REFRESH, REFRESH"
are both 3 loops.

Where the weights come from (read this before quoting the number):
  * reload = 6: the model says a RELOAD is itself a chain (ANCHOR, SCAN, ANCHOR, READ, KEYIFY: five steps) and
    it interrupts the task, so five steps plus the interruption;
  * reorient = 3: the model says ENUMERATE of the local options, "often" plus a RELOAD; set to half a RELOAD;
  * read_coarse = 0.25: the model calls a SCAN "shallow" reading; a coarse item costs a quarter of a fine one;
  * the rest (slot_step 1, discriminate 3, loop 2) are ordinal judgement.
  THE WEIGHTS ARE NOT MEASURED.  They make the order the source narration reports (RELOAD and RE-ORIENT loops
  dominate, not any single hard step) come out right.  Use the number to compare chains of the SAME task, as the
  tests do (the recorded chain > the fixed chain > the cheap chain); never as a threshold, a score, or minutes.
  The only gate in this layer is the budget flag below.  Calibration is an open problem (docs/OPEN-PROBLEMS.md).

Length is reported, never optimised: `steps` is returned next to the number and is not a term of it.  Fifty steps
that need no slot and read nothing add nothing; test_chain.py holds that.

The budget (section 3): working memory is B slots, B small exactly when help is needed.  A step's working set is
what it needs itself (`need`) plus what is held across it (`held`).  demand = need + len(held).  When demand
exceeds B something falls out and the chain gains a RELOAD.  peak_slots is the largest demand;
over_budget_steps lists the steps with demand > B.  B defaults to 3 (chain.DEFAULT_BUDGET), the chain's own
`budget` overrides it, and the CLI's --budget overrides both.

What this cannot see: what the person really held.  `held` is the narrator's list of items; a chain that forgets
to list one under-reports its memory load, and this file has no way to notice.
"""
from __future__ import annotations

from chain import resolve_budget

WEIGHTS = {
    "read_fine": 1.0,
    "read_coarse": 0.25,
    "slot_step": 1.0,
    "reload": 6.0,
    "reorient": 3.0,
    "discriminate": 3.0,
    "loop": 2.0,
}


def working_sets(chain: dict) -> list[dict]:
    """Per step: the slots it needs now, the items held across it, and their sum (the demand on working memory)."""
    return [{"step": s["n"], "op": s["op"], "need": s["need"], "held": len(s["held"]),
             "demand": s["need"] + len(s["held"])} for s in chain["steps"]]


def chain_load(chain: dict, budget: int | None = None, weights: dict | None = None) -> dict:
    """Components, the one number, and the budget verdict for one (blind or full) chain."""
    w = {**WEIGHTS, **(weights or {})}
    b = resolve_budget(chain, budget)
    fine = coarse = sim_sum = 0.0
    slot_steps = reloads = reorients = loops = 0
    peak = peak_held = 0
    over: list[int] = []
    prev_op, prev_looped = None, False
    for s in chain["steps"]:
        t = s["times"]
        looped = False
        if s["reading"] == "fine":
            fine += s["amount"] * t
        elif s["reading"] == "coarse":
            coarse += s["amount"] * t
        held = len(s["held"])
        slot_steps += held * t
        demand = s["need"] + held
        peak, peak_held = max(peak, demand), max(peak_held, held)
        if demand > b:
            over.append(s["n"])
        if s["op"] == "RELOAD":
            reloads += t
        elif s["op"] == "RE-ORIENT":
            reorients += t
        elif s["op"] == "DISCRIMINATE":
            sim_sum += s["confusables"]["similarity"] * t
        elif s["op"] == "REFRESH":
            # a refresh is one turn of a wait/verify loop when it follows the WAIT or VERIFY, or a refresh that was one;
            # the copies a `times` stands for follow each other, so they count like separate steps would
            looped = prev_op in ("WAIT", "VERIFY") or (prev_op == "REFRESH" and prev_looped)
            if looped:
                loops += t
        prev_op, prev_looped = s["op"], looped
    terms = {
        "reading": fine * w["read_fine"] + coarse * w["read_coarse"],
        "slot_steps": slot_steps * w["slot_step"],
        "reload": reloads * w["reload"],
        "reorient": reorients * w["reorient"],
        "discriminate": sim_sum * w["discriminate"],
        "loops": loops * w["loop"],
    }
    return {
        "steps": len(chain["steps"]),             # reported, never a term of the number
        "budget": b,
        "peak_slots": peak,
        "peak_held": peak_held,
        "over_budget_steps": over,
        "counts": {"read_fine": fine, "read_coarse": coarse, "slot_steps": slot_steps, "reloads": reloads,
                   "reorients": reorients, "discriminate_similarity": sim_sum, "loops": loops},
        "terms": terms,
        "load": sum(terms.values()),
    }


def summary_line(res: dict) -> str:
    """One short line of components for humans, in the order of the formula."""
    t = res["terms"]
    return (f"reading {t['reading']:.2f} + slot-steps {t['slot_steps']:.0f} + RELOAD {t['reload']:.0f} "
            f"+ RE-ORIENT {t['reorient']:.0f} + discriminate {t['discriminate']:.2f} + loops {t['loops']:.0f}")
