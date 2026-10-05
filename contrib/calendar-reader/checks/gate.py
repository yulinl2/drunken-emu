#!/usr/bin/env python3
"""
gate.py — every check, one browser, one verdict.

Running the checks separately means launching Chromium three times, starting a
server three times, and remembering three sets of selector arguments. Over one
session that came to fifteen hand-started servers, one of which was started
wrong in a way `bin/emu` already had a comment warning about.

This loads the page once and asks everything of it. Findings are grouped by what
they cost rather than by which file found them, because that is the order you
fix them in:

  BROKEN   it does not run, or a whole row of text fell out of its box
  COSTLY   it runs and reads badly — repeats, decode-at-a-distance, walls
  ROUGH    it reads fine and is awkward to hit

Selectors live in `emu.json` beside the artifact, so they are stated once
instead of retyped per run:

    { "content": ".rg-root",
      "key":     ".rg-roomchip",
      "selector": "button,a[href],.rg-ev-num,.rg-ev-name",
      "minTap": 44 }

  python3 checks/gate.py <url> <outdir> [--config path/to/emu.json]
"""

import argparse
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent


def load(name, symbol="PROBE"):
    """Reuse a check's own probe rather than keeping a second copy of it.

    A copy would drift, and a drifted probe is the kind of thing that passes
    for months. The slice runs from the assignment to the next top-level `def`,
    which is where every probe in this kit ends.
    """
    src = (HERE / name).read_text(encoding="utf-8")
    start = src.index(f"{symbol} = ")
    ns = {}
    exec(src[start:src.index("\ndef ", start)], ns)
    return ns[symbol]


DEFAULTS = {"content": "body", "key": ".legend,.key,[data-key]",
            "selector": "*", "minTap": 44, "width": 390, "height": 1400,
            "settle": 2200, "wall": 320, "travel": 420, "echoSpread": 120}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("outdir", nargs="?", default=str(HERE.parent / "out"))
    ap.add_argument("--config")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    cfg = dict(DEFAULTS)
    if a.config and pathlib.Path(a.config).exists():
        cfg.update(json.loads(pathlib.Path(a.config).read_text(encoding="utf-8")))
        print(f"config: {a.config}")

    clip_probe = load("clipping.py")
    read_probe = load("reading.py")

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": cfg["width"], "height": cfg["height"]},
                        device_scale_factor=2)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(a.url)
        pg.wait_for_timeout(cfg["settle"])
        mounted = pg.evaluate("() => document.body.innerText.trim().length > 40")
        geo = pg.evaluate(clip_probe.replace("MIN", str(cfg["minTap"])), cfg["selector"])
        rd = pg.evaluate(read_probe, {"content": cfg["content"], "key": cfg["key"],
                                      "echoWords": 3})
        shot = pathlib.Path(a.outdir) / "gate.png"
        shot.parent.mkdir(parents=True, exist_ok=True)
        pg.screenshot(path=str(shot), full_page=True)
        b.close()

    broken, costly, rough = [], [], []
    if not mounted:
        broken.append("the page rendered nothing")
    for e in errs:
        broken.append(f"js error: {e[:120]}")
    for c in geo["clipped"]:
        broken.append(f"clipped .{c['cls']} {c['txt']!r} — "
                      f"{c['overTall'] or c['overWide']}px past its {c['box']} box")
    if geo["pageOverflow"]:
        broken.append(f"page is {geo['pageOverflow']}px wider than the viewport")

    for e in [x for x in rd["echo"] if x["spread"] >= cfg["echoSpread"]]:
        costly.append(f"said twice, {e['spread']}px apart: \"{e['phrase']}\"")
    for t in [x for x in rd["travel"] if x["px"] >= cfg["travel"]]:
        costly.append(f"{t['token']!r} colours something {t['px']}px away "
                      f"that never says it: {t['farthest']!r}")
    for w in [x for x in rd["wall"] if x["chars"] >= cfg["wall"]]:
        costly.append(f"{w['chars']} characters unbroken (~{w['chars']/5/200*60:.0f}s): "
                      f"{w['txt']!r}")
    if rd["first"] and rd["first"]["y"] / rd["viewport"] > 1.0:
        costly.append(f"nothing to act on until {rd['first']['y']/rd['viewport']:.1f} "
                      f"viewports down ({rd['first']['txt']!r})")

    for s in geo["small"]:
        rough.append(f"{s['txt']!r} is {s['w']}x{s['h']}, under {cfg['minTap']}")

    if a.json:
        print(json.dumps({"broken": broken, "costly": costly, "rough": rough},
                         indent=1, ensure_ascii=False))
        return 1 if broken or costly or rough else 0

    for label, items, blurb in (
            ("BROKEN", broken, "does not run, or text fell out of its box"),
            ("COSTLY", costly, "runs, and the reader pays for it"),
            ("ROUGH", rough, "reads fine, awkward to hit")):
        print(f"\n{label}  — {blurb}")
        for i in items[:8]:
            print(f"  {i}")
        if len(items) > 8:
            print(f"  … and {len(items) - 8} more")
        if not items:
            print("  none")

    n = len(broken) + len(costly) + len(rough)
    print(f"\n{n} findings" if n else "\nclean")
    print(f"{shot}")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
