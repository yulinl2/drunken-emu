#!/usr/bin/env python3
"""
timetravel.py — render the page as if it were another day, and check that what
it says about "now" is true on that day.

Anything that reads the clock has branches that only one date can reach. They
are the branches least likely to have been looked at, because the person writing
them was, by definition, standing on a different day. A term calendar makes this
sharp: Labor Day is closed, one Tuesday runs Monday's schedule and one Wednesday
runs Friday's, so the weekday a date *is* and the schedule it *runs* come apart
on three days out of seventy-five. A component that answers "what is next" from
`Date.getDay()` is right on the other seventy-two and cannot be caught there.

What it asserts, for each date:

  closed day    nothing may be announced as happening today
  swap day      anything announced today must belong to the schedule that
                actually runs, not to the weekday the date falls on
  normal day    anything announced today must belong to that weekday

It drives the real artifact through emu-kit rather than re-implementing the
rule, because a re-implementation agrees with itself.

  python3 checks/timetravel.py --artifact ../stat-fall2026-grid.jsx \\
                               --term ../docs/facts/rutgers-nb-fall2026.json

Exit status is 1 on any finding, so it drops straight into a gate.
"""

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent


def find_kit():
    env = os.environ.get("EMU_KIT")
    cands = [pathlib.Path(env)] if env else []
    cands += [HERE.parent / "emu-kit",
              HERE.parent.parent / "emu-kit",
              pathlib.Path.home() / "kit" / "emu-kit",
              pathlib.Path("/home/claude/kit/emu-kit")]  # search path, not a dependency
    for c in cands:
        if c and (c / "harness").is_dir():
            return c
    sys.exit("cannot find the drunken-emu harness.\n"
             "  git clone https://github.com/yulinl2/drunken-emu ./emu-kit\n"
             "  or set EMU_KIT=/path/to/emu-kit")


# Read the pattern days straight out of the artifact rather than restating them.
def events_from(artifact: pathlib.Path):
    src = artifact.read_text(encoding="utf-8")
    body = re.search(r"^const EVENTS = \[(.*?)^\];", src, re.S | re.M)
    if not body:
        sys.exit("could not find the EVENTS array")
    out = {}
    for m in re.finditer(r"\{[^{}]*?id:\s*\"([^\"]+)\"[^{}]*?\}", body.group(1), re.S):
        blob, eid = m.group(0), m.group(1)
        days = re.search(r"days:\s*\[([0-9,\s]*)\]", blob)
        short = re.search(r"short:\s*\"([^\"]*)\"", blob)
        if days:
            out[eid] = {
                "days": [int(x) for x in days.group(1).split(",") if x.strip()],
                "short": short.group(1) if short else "",
            }
    if not out:
        sys.exit("parsed no events out of EVENTS")
    return out


PROBE = r"""
import sys, json
from playwright.sync_api import sync_playwright
url, iso, hhmm, shot = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 390, "height": 844})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    # Fix the clock before any script runs, so module-level reads see it too.
    # set_fixed_time fakes Date only. clock.install() also takes over the
    # timers, which freezes React's scheduler and the page never mounts.
    pg.clock.set_fixed_time(iso + "T" + hhmm + ":00")
    pg.goto(url)
    pg.wait_for_timeout(2000)
    if shot:
        pg.screenshot(path=shot, full_page=False)
    JS = ("() => ({"
          " mounted: !!document.querySelector('.rg-root'),"
          " nextup: (document.querySelector('.rg-nextup')||{}).textContent || null,"
          " when: (document.querySelector('.rg-nextup-when')||{}).textContent || null"
          "})")
    out = pg.evaluate(JS)
    out["nextup"] = (out["nextup"] or "").strip() or None
    out["when"] = (out["when"] or "").strip() or None
    out["js_errors"] = errs
    print(json.dumps(out))
    b.close()
"""

# "in 47 min" / "in 3 h" mean today. A weekday name means a later day.
TODAY_RE = re.compile(r"^in\s+\d+\s*(min|h)$")


def dated_in_artifact(path=None):
    """Every ISO date the artifact singles out, whatever block it lives in.

    A regex over the whole file rather than three block parsers: the point is
    to notice a date a future block introduces, and a parser that knows the
    block names by heart cannot do that. False positives cost one extra render.
    """
    import re
    p = pathlib.Path(path or (HERE.parent.parent / "stat-fall2026-grid.jsx"))
    if not p.exists():
        return []
    return sorted(set(re.findall(r'"(20\d\d-[01]\d-[0-3]\d)"',
                                 p.read_text(encoding="utf-8"))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", default=str(HERE.parent.parent / "stat-fall2026-grid.jsx"))
    ap.add_argument("--term", default=str(HERE.parent.parent / "docs/facts/rutgers-nb-fall2026.json"))
    ap.add_argument("--at", default="09:00", help="wall clock time on each date")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--dates", default="", help="comma-separated ISO dates; default picks the interesting ones")
    ap.add_argument("--shots", action="store_true")
    a = ap.parse_args()

    artifact = pathlib.Path(a.artifact).resolve()
    term = json.loads(pathlib.Path(a.term).read_text(encoding="utf-8"))
    events = events_from(artifact)
    kit = find_kit()

    no_class = term["no_class"]
    swaps = {k: v["runs"] for k, v in term["swaps"].items()}
    first = dt.date.fromisoformat(term["term"]["first_day"])
    last = dt.date.fromisoformat(term["term"]["last_day"])

    if a.dates.strip():
        dates = [d.strip() for d in a.dates.split(",") if d.strip()]
    else:
        # Every date whose schedule differs from its weekday, plus one ordinary
        # control so a check that fails on everything is distinguishable from
        # one that found the three days that matter.
        #
        # Plus every date the artifact itself singles out. A branch that only
        # runs on one date of the term is unreachable on the other seventy-four,
        # which is how `nextUp` stayed wrong until the term started. `SPEAKERS`,
        # `ONE_OFFS` and `EXCEPTIONS` each add such a date, and each was added
        # after this check was written — so the dates are read out of the file
        # rather than listed here, and the next one is covered for free.
        dates = sorted(set(list(no_class) + list(swaps)
                           + dated_in_artifact() + [first.isoformat()]))
    dates = [d for d in dates if first <= dt.date.fromisoformat(d) <= last]

    probe = pathlib.Path(tempfile.gettempdir()) / "timetravel_probe.py"
    probe.write_text(PROBE, encoding="utf-8")

    sync = subprocess.run([sys.executable, str(kit / "bin/sync_artifact.py"),
                           str(artifact), str(kit / "harness/app.jsx")],
                          capture_output=True, text=True)
    if sync.returncode != 0:
        sys.exit("sync failed: " + (sync.stdout or sync.stderr).strip())

    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(a.port),
                            "--bind", "127.0.0.1"], cwd=kit,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)

    findings, rows = [], []
    try:
        for iso in dates:
            d = dt.date.fromisoformat(iso)
            if iso in no_class:
                runs, kind = None, "closed"
            elif iso in swaps:
                runs, kind = swaps[iso], "swap"
            else:
                runs, kind = d.weekday(), "ok"

            shot = str(kit / "out" / f"tt_{iso}.png") if a.shots else ""
            r = subprocess.run([sys.executable, str(probe),
                                f"http://127.0.0.1:{a.port}/harness/harness.html",
                                iso, a.at, shot],
                               capture_output=True, text=True)
            if r.returncode != 0:
                findings.append(f"{iso}: probe failed — {r.stderr.strip()[:200]}")
                continue
            out = json.loads(r.stdout)
            if not out["mounted"]:
                findings.append(f"{iso}: component did not mount")
                continue
            if out["js_errors"]:
                findings.append(f"{iso}: js error — {out['js_errors'][0][:120]}")

            when, text = out["when"], out["nextup"] or ""
            claims_today = bool(when and TODAY_RE.match(when))
            named = None
            for eid, ev in events.items():
                token = ev["short"] or eid
                if token and token in text:
                    named = eid
                    break

            rows.append((iso, d.strftime("%a"), kind,
                         "—" if runs is None else "MTWTFSU"[runs],   # 7, not 5: Rutgers runs
            # regular Saturday classes, and widening the date list to every
            # date the artifact names was the first thing ever to pass one in.
                         when or "—", named or "—", claims_today))

            if not claims_today:
                continue
            if kind == "closed":
                findings.append(
                    f"{iso} ({d:%a}) is closed — {no_class[iso]} — but the page says "
                    f"{when!r} about {named or text[:40]!r}")
            elif named and runs is not None and runs not in events[named]["days"]:
                findings.append(
                    f"{iso} ({d:%a}) runs {'MTWTF'[runs]}'s schedule, but the page says "
                    f"{when!r} about {named}, which meets on "
                    f"{[ 'MTWTF'[x] for x in events[named]['days'] ]}")
    finally:
        srv.terminate()

    w = max(len(r[5]) for r in rows) if rows else 4
    print(f"{'date':11} {'is':4} {'kind':7} {'runs':4} {'says':12} {'about':{w}}  today?")
    print("-" * (46 + w))
    for iso, isday, kind, runs, when, named, today in rows:
        print(f"{iso:11} {isday:4} {kind:7} {runs:4} {when:12} {named:{w}}  {'yes' if today else 'no'}")
    print()
    if findings:
        for f in findings:
            print("  FAIL " + f)
        print(f"\n{len(findings)} finding(s)")
        return 1
    print(f"{len(rows)} date(s) checked, all consistent with the term calendar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
