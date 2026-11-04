#!/usr/bin/env python3
"""figbank/examples/gen_majority_vote.py — spec generator for the `plot` kind's first instance.

Writes figbank/examples/majority-vote-curve.json: a PURE ANALYTIC curve, no research data. The
function is the beta-binomial majority vote — P(more than m/2 of m exchangeable Bernoulli(p) voters
are correct) with pairwise error correlation rho — a textbook model, reproduced here so this generic
tooling repo has a real curve to draw. It is the same formula as panel (a) of HAN's
paper/figures/make_figures.py (majority_acc / beta_tail_half), ported line for line (no scipy: the
continued-fraction incomplete beta HAN falls back to); HAN itself is not imported or modified.

Every number in the spec is computed here from (p, rho, m); nothing is typed in. `--selfcheck`
(default on) asserts the port against independent facts before writing anything.

    python3 figbank/examples/gen_majority_vote.py
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def lbeta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def majority_acc(m, p, rho):
    ks = range(m // 2 + 1, m + 1)
    if rho <= 0:
        return sum(math.comb(m, k) * p ** k * (1 - p) ** (m - k) for k in ks)
    a, b = p * (1 - rho) / rho, (1 - p) * (1 - rho) / rho
    return sum(math.exp(math.log(math.comb(m, k)) + lbeta(k + a, m - k + b) - lbeta(a, b)) for k in ks)


def _betacf(a, b, x, itmax=400, eps=3e-14):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e300
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def reg_inc_beta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1 - x) / b


def beta_tail_half(p, rho):
    """lim m->inf majority accuracy = P(Beta(a, b) > 1/2)."""
    a, b = p * (1 - rho) / rho, (1 - p) * (1 - rho) / rho
    return 1.0 - reg_inc_beta(a, b, 0.5)


P = 0.70
MS = list(range(1, 26, 2))
# Okabe-Ito colour-blind-safe (same hexes as HAN's panel)
CURVES = [(0.0, "#000000", "independent (ρ = 0)"), (0.06, "#009E73", "ρ = 0.06"), (0.36, "#E69F00", "ρ = 0.36"),
          (0.55, "#D55E00", "ρ = 0.55"), (0.80, "#CC79A7", "ρ = 0.80")]


def selfcheck():
    # 1. m = 1 is a single voter: accuracy p, for every rho
    for rho, _, _ in CURVES:
        assert abs(majority_acc(1, P, rho) - P) < 1e-12, rho
    # 2. rho -> 0+ converges to the binomial curve
    assert abs(majority_acc(25, P, 1e-7) - majority_acc(25, P, 0.0)) < 1e-5
    # 3. the ceiling is the m -> infinity limit: bounds every finite m and is approached by a large one
    for rho, _, _ in CURVES[1:]:
        c = beta_tail_half(P, rho)
        assert c >= majority_acc(25, P, rho) - 1e-9 and abs(majority_acc(1999, P, rho) - c) < 0.01, rho
    # 4. the two ceilings HAN's own panel annotates (0.721 and 0.703, paper/figures/make_figures.py)
    assert round(beta_tail_half(P, 0.55), 3) == 0.721 and round(beta_tail_half(P, 0.80), 3) == 0.703
    # 5. independent voters approach 1
    assert majority_acc(25, P, 0.0) > 0.98


def main():
    selfcheck()
    series = []
    for rho, col, lab in CURVES:
        series.append({"id": f"rho-{rho}", "kind": "curve", "label": lab, "color": col, "dots": True,
                       "x": MS, "y": [round(majority_acc(m, P, rho), 6) for m in MS]})
    # m -> infinity: independent voters tend to 1 (Condorcet); correlated ones to P(Beta(a, b) > 1/2)
    for rho, col, _ in CURVES:
        c = 1.0 if rho <= 0 else round(beta_tail_half(P, rho), 6)
        series.append({"id": f"ceiling-{rho}", "kind": "curve", "color": col, "dashed": True, "x": [MS[0], MS[-1]], "y": [c, c],
                       "end_label": "1" if rho <= 0 else f"{c:.3f}"})
    spec = {
        "id": "majority-vote-curve",
        "message": "Majority-vote accuracy climbs toward 1 with more independent voters, but when the voters' errors are correlated it saturates at a ceiling barely above one voter's 0.70 accuracy.",
        "provenance": {
            "generated_by": "figbank/examples/gen_majority_vote.py",
            "source": "analytic: beta-binomial majority vote, p = 0.70; formula as in HAN paper/figures/make_figures.py panel (a); no research data",
        },
        "canvas": {"width": 780, "height": 440},
        "word_budget": 50,
        "must_not_contain": ["…"],
        "title": {"text": "Majority vote of m voters, each right 70% of the time; dotted lines: ceiling as m grows without bound.", "x": 16, "y": 14, "w": 740},
        "plot": {
            "box": {"x": 16, "y": 70, "w": 748, "h": 354},
            "x_axis": {"label": "number of voters m (odd)"},
            "y_axis": {"label": "majority-vote accuracy", "domain": [0.68, 1.0]},
            "series": series,
        },
        "acceptance": {
            "must_mention": [["voters", "vote"], ["correlat", "ρ", "rho"], ["ceiling", "saturat", "plateau", "level", "flatten", "limit"]],
            "unreadable_max": 0,
            "legibility": {"width": 780, "min_px": 10, "surface": "one column of a two-column paper, roughly"},
            "rounds_max": 3,
        },
    }
    out = os.path.join(HERE, "majority-vote-curve.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {out}: {len(series)} series, selfcheck passed")


if __name__ == "__main__":
    sys.exit(main())
