#!/usr/bin/env python3
"""
scenarios.py — run a component against hostile data, from fixtures that cannot
go stale.

The usual way to stress a component is to save copies of it with different data
in them. Those copies keep passing while the component moves out from under
them, which is worse than having nothing: they read as coverage. This splices a
named array into the *live* file at run time, so a fixture is never older than
the thing it tests.

A scenario is a JSON file:

    { "name": "triple",
      "why":  "three blocks stacked on one day",
      "array": "EVENTS",
      "body": "  { id:\"a\", days:[0], start:\"13:00\", end:\"16:00\" },\n...",
      "expect": { "mounted": true, "minNodes": 20, "noClipping": true } }

Tap-target checking is off unless a scenario asks for it — the page chrome is
not what a data scenario is testing, and failing every fixture on the same
toolbar button teaches you to skim the output.

`expect.contains` is how you write a positive control: list substrings that MUST
appear, feed data that is wrong in several ways, and assert the component's own
validation names every one. A suite where nothing ever fails proves nothing.

  python3 checks/scenarios.py <component.jsx> --scenarios scenarios/*.json
  python3 checks/scenarios.py <component.jsx> --scenarios s/*.json --keep
"""

import argparse
import glob
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
PORT = 8155
PROBE = KIT / "checks" / "_scenario_probe.py"


def splice(component: Path, array: str, body: str) -> str:
    src = component.read_text(encoding="utf-8")
    new, n = re.subn(rf"^const {array} = \[.*?^\];",
                     f"const {array} = [\n{body}\n];", src, count=1, flags=re.S | re.M)
    if n != 1:
        sys.exit(f"could not find `const {array} = [ ... ];` in {component.name}")
    return new


PROBE_SRC = r'''
import sys, json
from playwright.sync_api import sync_playwright
url, shot = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 390, "height": 1400}, device_scale_factor=2)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(2200)
    pg.screenshot(path=shot, full_page=True)
    out = pg.evaluate("""() => {
      const clipped = [];
      const HTML = 'http://www.w3.org/1999/xhtml';
      document.querySelectorAll('*').forEach(e => {
        // SVG children report clientWidth 0 and a className object; their
        // overflow means nothing here.
        if (e.namespaceURI !== HTML) return;
        if (!e.children.length && e.clientHeight > 0) {
          // 2px, not 1: sub-pixel line-height rounding puts a single row one
            // over. A real clip is a whole line and never under 9px.
            // Height needs a line's worth. A line-height tighter than the
            // font's natural line box overflows by a few pixels on text that
            // renders perfectly; a row that actually fell out is a whole line.
            const fs = parseFloat(getComputedStyle(e).fontSize) || 12;
            if (e.scrollWidth > e.clientWidth + 2 ||
                e.scrollHeight - e.clientHeight >= fs * 0.7)
            clipped.push((e.className||'') + ' ' + (e.textContent||'').trim().slice(0,26));
        }
      });
      const small = [];
      document.querySelectorAll('button,a[href],[role=button]').forEach(e => {
        const r = e.getBoundingClientRect();
        if (r.width > 0 && (r.width < 44 || r.height < 44))
          small.push(((e.textContent||'').trim()||e.tagName).slice(0,18));
      });
      return { nodes: document.querySelectorAll('*').length, clipped, small,
               text: document.body.innerText,
               overflow: Math.max(0, document.documentElement.scrollWidth - window.innerWidth) };
    }""")
    out["errors"] = errs
    print(json.dumps(out)); b.close()
'''


def check(d, exp):
    fails = []
    if exp.get("mounted", True) and d["nodes"] < exp.get("minNodes", 20):
        fails.append(f"did not mount ({d['nodes']} nodes)")
    if d["errors"]:
        fails.append("js error: " + d["errors"][0][:110])
    if exp.get("noClipping", True):
        fails += [f"clipped {c!r}" for c in d["clipped"]]
    if exp.get("tapTargets", False):
        fails += [f"tap target {s!r} under 44px" for s in d["small"]]
    if d["overflow"] > 0:
        fails.append(f"page overflows by {d['overflow']}px")
    for want in exp.get("contains", []):
        if want not in d["text"]:
            fails.append(f"expected the page to say {want!r} and it did not")
    for bad in exp.get("absent", []):
        if bad in d["text"]:
            fails.append(f"expected {bad!r} to be absent")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("component")
    ap.add_argument("--scenarios", nargs="+", required=True)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()

    comp = Path(a.component).resolve()
    files = [Path(f) for pat in a.scenarios for f in sorted(glob.glob(pat))]
    if not files:
        sys.exit("no scenario files matched")
    PROBE.write_text(PROBE_SRC, encoding="utf-8")

    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT),
                            "--bind", "127.0.0.1"], cwd=KIT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    results = []
    try:
        for f in files:
            sc = json.loads(f.read_text(encoding="utf-8"))
            name = sc.get("name", f.stem)
            tmp = Path(tempfile.gettempdir()) / f"scen_{name}.jsx"
            tmp.write_text(splice(comp, sc.get("array", "EVENTS"), sc.get("body", "")),
                           encoding="utf-8")
            sync = subprocess.run([sys.executable, str(KIT / "bin" / "sync_artifact.py"),
                                   str(tmp), str(KIT / "harness" / "app.jsx")],
                                  capture_output=True, text=True)
            if sync.returncode:
                results.append((name, sc.get("why", ""), ["sync failed: " + sync.stdout.strip()]))
                continue
            shot = KIT / "out" / f"scen_{name}.png"
            r = subprocess.run([sys.executable, str(PROBE),
                                f"http://127.0.0.1:{PORT}/harness/harness.html", str(shot)],
                               capture_output=True, text=True)
            if r.returncode:
                results.append((name, sc.get("why", ""), ["probe crashed: " + r.stderr[-160:]]))
                continue
            results.append((name, sc.get("why", ""),
                            check(json.loads(r.stdout.strip().splitlines()[-1]),
                                  sc.get("expect", {}))))
            if not a.keep:
                tmp.unlink(missing_ok=True)
    finally:
        srv.terminate()

    w = max(len(n) for n, _, _ in results)
    print()
    for name, why, fails in results:
        print(f"  {'FAIL' if fails else 'pass'}  {name:<{w}}  {fails[0] if fails else why}")
        for extra in fails[1:]:
            print(f"        {'':<{w}}  {extra}")
    bad = sum(1 for _, _, f in results if f)
    print(f"\n{len(results) - bad}/{len(results)} clean")
    print(f"screenshots: {KIT / 'out'}/scen_*.png")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
