#!/usr/bin/env python3
"""
ci_claims.py -- assert that README.md is still telling the truth.

The README carries falsifiable claims. Code drift can silently invalidate them,
and the failure mode of a toolkit maintained by many sessions is exactly that:
behaviour changes, README does not, the next session inherits a stale brain.

Design constraint that shapes everything here: ABSOLUTE TIMINGS ARE NOT PORTABLE.
The README's "0.18 s + 0.55 ms/node" was measured in one sandbox; a GitHub
runner has different silicon and would fail a constant-based assertion for
reasons that say nothing about correctness. So CI asserts RELATIONSHIPS, which
survive a hardware change:

  C1  node count drives mount cost, source bytes do not
      -> 80 KB of comments (2 nodes) mounts FASTER than 19 KB of 500 spans.
         This is the exact comparison that falsified the original
         "linear-ish in source bytes" claim, so it is the one CI must keep.
  C2  mount time is monotone increasing in dom_nodes
  C3  a linear fit in dom_nodes explains the variation (R^2 above threshold)
  C4  positive control: the overflow check FIRES on known-bad input and stays
      SILENT on known-good input. A check that never fires proves nothing.

Exit 0 = every claim holds. Exit 1 = README and reality have diverged; either
the code regressed or the README needs updating. Both require a human.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
R2_MIN = 0.90


# --------------------------------------------------------------------------- #
# fixtures: each is (name, jsx_source, expected_dom_nodes_roughly)
# --------------------------------------------------------------------------- #
def fixture_comments(kb: int = 80) -> str:
    """Huge source, tiny DOM. The counter-example to 'bytes drive cost'."""
    filler = "\n".join(f"// {'x' * 76}" for _ in range(kb * 1024 // 80))
    return (
        'import React from "react";\n'
        f"{filler}\n"
        "export default function App() {\n"
        '  return <div className="p-4">one element</div>;\n'
        "}\n"
    )


def fixture_spans(n: int) -> str:
    """Small-ish source, large DOM. Also overflows horizontally on purpose."""
    spans = "".join(f"<span>s{i} </span>" for i in range(n))
    return (
        'import React from "react";\n'
        "export default function App() {\n"
        f'  return <div style={{{{whiteSpace:"nowrap"}}}}>{spans}</div>;\n'
        "}\n"
    )


def fixture_wellformed() -> str:
    """Known-good: modest DOM, no overflow. The silent half of C4."""
    rows = "".join(
        f'<li key={{{i}}} className="py-2">item {i}</li>' for i in range(20)
    )
    return (
        'import React from "react";\n'
        "export default function App() {\n"
        '  return <div className="p-4 max-w-md mx-auto">'
        f'<ul>{rows}</ul></div>;\n'
        "}\n"
    )


FIXTURES = [
    ("comments80k", fixture_comments(80)),
    ("spans500", fixture_spans(500)),
    ("spans2000", fixture_spans(2000)),
    ("wellformed", fixture_wellformed()),
]


# --------------------------------------------------------------------------- #
def run_smoke(src: str, tmp: Path, name: str) -> dict:
    art = tmp / f"{name}.jsx"
    art.write_text(src)
    proc = subprocess.run(
        ["bash", str(KIT / "bin" / "emu"), "smoke", str(art)],
        capture_output=True, text=True, cwd=str(KIT), timeout=180,
    )
    # emu prints the sync line then one JSON line; take the last JSON object
    payload = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                pass
    if payload is None:
        raise RuntimeError(
            f"{name}: no JSON from emu (rc={proc.returncode})\n"
            f"stdout: {proc.stdout[-500:]}\nstderr: {proc.stderr[-500:]}"
        )
    return payload


def linfit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """Least squares y = a + b x, plus R^2. No numpy dependency on purpose."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx if sxx else 0.0
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 1.0
    return a, b, r2


def main() -> int:
    results: dict[str, dict] = {}
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for name, src in FIXTURES:
            results[name] = run_smoke(src, tmp, name)
            r = results[name]
            print(
                f"  {name:12} dom_nodes={r['dom_nodes']:>5}  "
                f"mount={r['phases_s']['babel_compile_and_mount']:>5.2f}s  "
                f"h_overflow={r['h_overflow_px']:>6}  "
                f"js_errors={len(r['js_errors'])}"
            )

    failures: list[str] = []

    def claim(tag: str, ok: bool, detail: str) -> None:
        print(f"{'PASS' if ok else 'FAIL'}  {tag}  {detail}")
        if not ok:
            failures.append(f"{tag}: {detail}")

    m = {k: v["phases_s"]["babel_compile_and_mount"] for k, v in results.items()}
    d = {k: v["dom_nodes"] for k, v in results.items()}

    # C0 -- nothing threw. A silent JS error would invalidate every timing.
    bad = [k for k, v in results.items() if v["js_errors"]]
    claim("C0 no-js-errors", not bad, f"clean={sorted(results)}" if not bad else f"errors in {bad}")

    # C1 -- the falsifying comparison: bytes are not the driver
    claim(
        "C1 nodes-not-bytes",
        m["comments80k"] < m["spans500"],
        f"80KB/2-node {m['comments80k']:.2f}s < 19KB/500-node {m['spans500']:.2f}s",
    )

    # C2 -- monotone in node count
    order = ["comments80k", "spans500", "spans2000"]
    mono = all(m[a] <= m[b] for a, b in zip(order, order[1:]))
    claim("C2 monotone", mono, " <= ".join(f"{m[k]:.2f}" for k in order))

    # C3 -- linear in node count
    a, b, r2 = linfit([d[k] for k in order], [m[k] for k in order])
    claim(
        "C3 linear-fit",
        r2 >= R2_MIN and b > 0,
        f"mount ~ {a:.3f}s + {b*1000:.3f}ms/node, R^2={r2:.4f} (min {R2_MIN})",
    )

    # C4 -- positive control: fires on bad, silent on good
    claim(
        "C4a control-fires",
        results["spans2000"]["h_overflow_px"] > 10000,
        f"spans2000 h_overflow_px={results['spans2000']['h_overflow_px']}",
    )
    claim(
        "C4b control-silent",
        results["wellformed"]["h_overflow_px"] == 0,
        f"wellformed h_overflow_px={results['wellformed']['h_overflow_px']}",
    )

    print()
    if failures:
        print("README and reality have diverged:")
        for f in failures:
            print(f"  - {f}")
        print("\nEither the code regressed, or README.md needs updating.")
        print("If a claim is genuinely obsolete, move it to the ## Falsified")
        print("section with the measurement that killed it. Do not delete it.")
        return 1

    print(f"all {6} claims hold; measured slope {b*1000:.3f} ms/node "
          f"(this runner; README quotes 0.55 for its own sandbox)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
