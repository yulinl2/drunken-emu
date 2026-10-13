#!/usr/bin/env python3
"""
prediction_score.py -- score a registered prediction against what happened (theory/RECORD-THEORY.md section 8, step 4).

Point: the scoring protocol of docs/predictions/hw2-sample-pass.md as code, committed BEFORE the pass, so the way of scoring is not chosen after it.
Stdlib only. It reads two files and decides nothing the registration did not fix.

    python3 checks/prediction_score.py docs/predictions/hw2-sample-pass.prediction.json OUTCOMES.json [--json]

OUTCOMES.json (schema emu-outcomes/1) is written by whoever transcribes the narration and screenshots. Code the events WITHOUT reading the p column.

    {"schema": "emu-outcomes/1", "prediction": "hw2-sample-pass",
     "events":       {"P1": 1, "P2": 0, "I7": null},               # 1 = the observable happened; 0 = the segment was narrated or shown and it did not; null = not scored
     "durations_min": {"<chain id>": 2},                            # per segment: the median minutes of its dated instances (clock resolution: one minute)
     "losses":       [{"chain": "<chain id>", "step": 7}],          # every loss narrated (forgot, lost the goal, went back to re-read), at the step it started
     "unregistered_frictions": [{"chain": "<chain id>", "step": 3}],  # a friction narrated that no registered event describes
     "false_findings": [{"chain": "<chain id>", "step": 9, "verifier": "colocation"}]}   # a finding of `bin/emu chain check` whose step is narrated as smooth

What it computes (each is defined in the registration's `scoring` block):
  brier     mean (p - o)^2 over scored events: overall, per basis (with how often p was on the right side of 0.5), per segment; against the
            constant forecast at the mean p, and against 0.5
  kendall   tau-b between the predicted ranks and the measured minutes (whole minutes, equal = tied), over the segments that are comparable by
            duration and have a measured value; needs 4; also the exact one-sided permutation p; also tau-b of the step-count baseline;
            also the pairs the weights order stably that were measured the other way by at least 1 minute and 25%
  onsets    for B = 2, 3, 4: narrated losses that fall within two steps of a predicted onset of the same chain, against the hits chance gives
            (the share of that chain's steps within two steps of an onset); losses in chains with no predicted onset are false alarms
  p02be     the observed rate of events whose steps carry a verifier finding against events whose steps carry none; unregistered frictions; false findings

Exit codes: 0 scored, 2 a file is not what it should be (unknown event id, bad schema).
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

WINDOW = 2                       # steps; theory section 8, step 4
MIN_SEGMENTS = 4                 # Kendall's tau means nothing under this
REVERSAL_MIN, REVERSAL_SHARE = 1, 0.25
PERMUTATION_MAX = 8              # exact permutation p up to 8 segments (40,320 orders)


class OutcomesError(ValueError):
    pass


def _whole(x) -> int:
    return int(float(x) + 0.5)                       # clock resolution is one minute; no banker's rounding


def tau_b(x: list[float], y: list[float]) -> float | None:
    """Kendall's tau-b of two equal-length lists (ties in either list allowed). None when one list is constant."""
    n = len(x)
    c = d = tx = ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            a, b = x[i] - x[j], y[i] - y[j]
            if a == 0 and b == 0:
                continue
            if a == 0:
                tx += 1
            elif b == 0:
                ty += 1
            elif (a > 0) == (b > 0):
                c += 1
            else:
                d += 1
    den = ((c + d + tx) * (c + d + ty)) ** 0.5
    return None if den == 0 else (c - d) / den


def permutation_p(pred: list[float], meas: list[float]) -> float | None:
    """One-sided exact p: the share of orders of the measured values whose tau-b is at least the observed one."""
    obs = tau_b(pred, meas)
    if obs is None or len(pred) > PERMUTATION_MAX:
        return None
    hits = total = 0
    for perm in itertools.permutations(meas):
        t = tau_b(pred, list(perm))
        total += 1
        hits += t is not None and t >= obs - 1e-12
    return hits / total


def load_outcomes(pred: dict, out: dict) -> None:
    if out.get("schema") != "emu-outcomes/1":
        raise OutcomesError("outcomes: schema must be emu-outcomes/1")
    if out.get("prediction") != pred["id"]:
        raise OutcomesError(f"outcomes: prediction must be {pred['id']!r}")
    known = {e["id"] for e in pred["events"]}
    chains = {s["id"]: s for s in pred["segments"]}
    for k, v in (out.get("events") or {}).items():
        if k not in known:
            raise OutcomesError(f"outcomes: unknown event id {k!r}")
        if v not in (0, 1, None):
            raise OutcomesError(f"outcomes: event {k!r} must be 1, 0 or null, got {v!r}")
    for k in out.get("durations_min") or {}:
        if k not in chains:
            raise OutcomesError(f"outcomes: unknown segment {k!r} in durations_min")
    for key in ("losses", "unregistered_frictions", "false_findings"):
        for row in out.get(key) or []:
            if row.get("chain") not in chains or not isinstance(row.get("step"), int) or not 1 <= row["step"] <= chains[row["chain"]]["steps"]:
                raise OutcomesError(f"outcomes: {key} row {row!r} names no step of a registered chain")


def _findings(pred: dict) -> set[tuple[str, int]]:
    return {(c["id"], f["step"]) for c in pred["chain_check_json"]["files"][0]["chains"] for f in c["findings"]}


def brier(pred: dict, out: dict) -> dict:
    scored = [(e, out["events"][e["id"]]) for e in pred["events"] if (out.get("events") or {}).get(e["id"]) in (0, 1)]
    if not scored:
        return {"n": 0}
    sq = lambda rows: sum((e["p"] - o) ** 2 for e, o in rows) / len(rows)
    mean_p = sum(e["p"] for e, _ in scored) / len(scored)
    ref = sum((mean_p - o) ** 2 for _, o in scored) / len(scored)
    res = {"n": len(scored), "brier": sq(scored), "observed_rate": sum(o for _, o in scored) / len(scored), "mean_p": mean_p,
           "reference_constant_mean_p": ref, "reference_constant_half": sum((0.5 - o) ** 2 for _, o in scored) / len(scored),
           "skill_vs_mean_p": (1 - sq(scored) / ref) if ref else None, "by_basis": {}, "by_segment": {}}
    for basis in pred["parameters"]["p_basis"]:
        rows = [(e, o) for e, o in scored if e["basis"] == basis]
        if rows:
            res["by_basis"][basis] = {"n": len(rows), "brier": sq(rows), "agree": sum((e["p"] >= 0.5) == (o == 1) for e, o in rows)}
    for seg in sorted({e["segment"] for e, _ in scored}):
        rows = [(e, o) for e, o in scored if e["segment"] == seg]
        res["by_segment"][seg] = {"n": len(rows), "brier": sq(rows)}
    return res


def kendall(pred: dict, out: dict) -> dict:
    rank, base = pred["ranking"]["rank"], pred["ranking"]["baseline_by_step_count"]["rank"]
    excl = set(pred["ranking"]["excluded_from_tau"])
    meas = {k: _whole(v) for k, v in (out.get("durations_min") or {}).items() if k not in excl}
    segs = sorted(meas)
    res = {"segments": segs, "measured_minutes": meas, "n": len(segs)}
    if len(segs) < MIN_SEGMENTS:
        res["scored"] = False
        res["why"] = f"fewer than {MIN_SEGMENTS} comparable segments have a measured duration"
        return res
    m = [meas[k] for k in segs]
    p_load, p_base = [-rank[k] for k in segs], [-base[k] for k in segs]
    res.update(scored=True, tau_b_load=tau_b(p_load, m), p_permutation_load=permutation_p(p_load, m),
               tau_b_step_count=tau_b(p_base, m), p_permutation_step_count=permutation_p(p_base, m))
    unstable = {frozenset((u["a"], u["b"])) for u in pred["parameters"]["rank_ties"]["unstable_pairs"]}
    rev = []
    for a, b in itertools.permutations(segs, 2):          # a predicted longer than b, the weights order them stably
        if rank[a] < rank[b] and frozenset((a, b)) not in unstable:
            gap = meas[b] - meas[a]
            if gap >= REVERSAL_MIN and gap >= REVERSAL_SHARE * meas[b]:
                rev.append({"predicted_longer": a, "measured_longer": b, "minutes": [meas[a], meas[b]]})
    res["reversals"] = rev
    return res


def onsets(pred: dict, out: dict) -> dict:
    segs = {s["id"]: s for s in pred["segments"]}
    losses = out.get("losses") or []
    res = {}
    for b in pred["parameters"]["budget_sensitivity"] + [pred["parameters"]["budget"]]:
        pts, hits, expected, in_pred, alarms = {}, 0, 0.0, 0, []
        for cid, s in segs.items():
            pts[cid] = s["predicted_loss_onsets_at_B"][str(b)]
        for row in losses:
            cid, step = row["chain"], row["step"]
            if not pts[cid]:
                alarms.append(row)
                continue
            n = segs[cid]["steps"]
            near = lambda t: any(abs(t - o) <= WINDOW for o in pts[cid])
            in_pred += 1
            hits += near(step)
            expected += sum(near(t) for t in range(1, n + 1)) / n
        res[str(b)] = {"losses_in_chains_with_a_predicted_onset": in_pred, "hits_within_two_steps": hits, "hits_expected_by_chance": round(expected, 3),
                       "false_alarms": len(alarms), "predicted_onsets": {k: v for k, v in pts.items() if v}}
    return res


def p02be(pred: dict, out: dict) -> dict:
    found = _findings(pred)
    rows = {True: [], False: []}
    for e in pred["events"]:
        o = (out.get("events") or {}).get(e["id"])
        if o in (0, 1):
            rows[any((r["chain"], r["step"]) in found for r in e["steps"])].append(o)
    rate = lambda xs: (sum(xs) / len(xs)) if xs else None
    unreg = out.get("unregistered_frictions") or []
    return {"events_at_a_step_with_a_finding": {"n": len(rows[True]), "observed_rate": rate(rows[True])},
            "events_at_steps_without_a_finding": {"n": len(rows[False]), "observed_rate": rate(rows[False])},
            "unregistered_frictions": len(unreg), "unregistered_at_a_silent_step": sum((r["chain"], r["step"]) not in found for r in unreg),
            "false_findings": len(out.get("false_findings") or []), "findings_registered": len(found)}


def score(pred: dict, out: dict) -> dict:
    load_outcomes(pred, out)
    return {"prediction": pred["id"], "brier": brier(pred, out), "kendall": kendall(pred, out), "onsets": onsets(pred, out), "p02be": p02be(pred, out)}


def _fmt(x):
    return "none" if x is None else f"{x:.3f}" if isinstance(x, float) else str(x)


def report(r: dict) -> str:
    b, k, o, p = r["brier"], r["kendall"], r["onsets"], r["p02be"]
    out = [f"prediction {r['prediction']}"]
    if b["n"]:
        out.append(f"brier {_fmt(b['brier'])} over {b['n']} events (constant at mean p {_fmt(b['reference_constant_mean_p'])}, constant 0.5 {_fmt(b['reference_constant_half'])}; skill {_fmt(b['skill_vs_mean_p'])}; observed rate {_fmt(b['observed_rate'])})")
        out += [f"  basis {name}: brier {_fmt(v['brier'])} over {v['n']}; the side of 0.5 was right {v['agree']} times" for name, v in b["by_basis"].items()]
    else:
        out.append("brier: no scored event")
    if k.get("scored"):
        out.append(f"kendall tau-b load {_fmt(k['tau_b_load'])} (exact one-sided p {_fmt(k['p_permutation_load'])}) over {k['n']} segments; step-count baseline {_fmt(k['tau_b_step_count'])} (p {_fmt(k['p_permutation_step_count'])}); reversals {len(k['reversals'])}")
    else:
        out.append(f"kendall: not scored ({k.get('why', '')})")
    for bb in sorted(o):
        v = o[bb]
        out.append(f"onsets at B={bb}: {v['hits_within_two_steps']} hits of {v['losses_in_chains_with_a_predicted_onset']} losses (chance {v['hits_expected_by_chance']}); false alarms {v['false_alarms']}")
    out.append(f"p02be: rate at steps with a finding {_fmt(p['events_at_a_step_with_a_finding']['observed_rate'])} (n {p['events_at_a_step_with_a_finding']['n']}), without {_fmt(p['events_at_steps_without_a_finding']['observed_rate'])} (n {p['events_at_steps_without_a_finding']['n']}); "
               f"unregistered frictions {p['unregistered_frictions']} ({p['unregistered_at_a_silent_step']} at a silent step); false findings {p['false_findings']} of {p['findings_registered']}")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        return 2
    try:
        r = score(json.loads(Path(args[0]).read_text(encoding="utf-8")), json.loads(Path(args[1]).read_text(encoding="utf-8")))
    except (OutcomesError, OSError, json.JSONDecodeError, KeyError) as e:
        print(f"prediction_score: {e}", file=sys.stderr)
        return 2
    print(json.dumps(r, indent=1) if "--json" in argv else report(r))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
