#!/usr/bin/env python3
"""
clipping.py — did any text get cut off, and can a thumb hit anything.

Written because the same twenty lines were pasted inline eight times over one
project, each time slightly differently, and twice with a bug that made the
check pass when it should not have. Two measurements do most of the work in a
layout that positions things absolutely:

  scrollHeight > clientHeight   text taller than the box holding it. This is
                                what a wrapped name looks like when the height
                                budget assumed one line.
  scrollWidth  > clientWidth    text wider than its column.

Neither is visible in a screenshot when the container has `overflow: hidden`,
which is exactly when you need to be told.

Plus the ergonomic floor. 28px clears a thumb; 44px is what a thumb wants when
it is aiming rather than swiping. A 30-minute calendar block draws 19.6px tall
and looks completely fine.

  python3 checks/clipping.py <url> [--width 390] [--height 1400] [--min-tap 44]
                             [--shot out/clip.png] [--selector .rg-ev,.rg-card]

Exit status is 1 on any finding, so it drops straight into a gate.
"""

import argparse
import json
import sys
from playwright.sync_api import sync_playwright

PROBE = """(sel) => {
  // Text these hold is never laid out, so their scroll box means nothing.
  const UNRENDERED = new Set(["STYLE", "SCRIPT", "TITLE", "NOSCRIPT", "TEMPLATE", "HEAD",
    // A page taller than the window is a page. <html> and <body> report the
    // whole document as scroll overflow on every site ever built, and their
    // textContent starts with whatever the first <style> holds, so the finding
    // reads as "1,359px of tailwind fell out" and is never actionable.
    "HTML", "BODY"]);
  // An element told to scroll is *supposed* to have more content than box.
  // Reporting a horizontal scroller as "text fell out" is reporting the feature.
  const scrolls = (e) => {
    const cs = getComputedStyle(e);
    return /auto|scroll/.test(cs.overflowX) || /auto|scroll/.test(cs.overflowY);
  };
  const clipped = [];
  document.querySelectorAll(sel).forEach(e => {
    if (UNRENDERED.has(e.tagName) || scrolls(e)) return;
    const dw = e.scrollWidth - e.clientWidth, dh = e.scrollHeight - e.clientHeight;
    // Height needs a line's worth, not a pixel. A `line-height` tighter than the
    // font's natural line box makes scrollHeight exceed clientHeight by a few
    // pixels on text that renders perfectly — 3px on a 10.5px font is a glyph
    // box, 9px is a row that fell out of the bottom. Width has no such effect,
    // so a small absolute tolerance is enough there.
    const fs = parseFloat(getComputedStyle(e).fontSize) || 12;
    if (dw > 2 || dh >= fs * 0.7) clipped.push({
      cls: e.className && e.className.toString().split(' ')[0],
      txt: (e.textContent || '').trim().slice(0, 40).replace(/\\s+/g, ' '),
      overWide: Math.max(0, dw), overTall: Math.max(0, dh),
      box: `${e.clientWidth}x${e.clientHeight}`,
    });
  });
  const small = [];
  document.querySelectorAll('button, a[href], [role=button], input, select').forEach(e => {
    const r = e.getBoundingClientRect();
    if (r.width > 0 && r.height > 0 && (r.width < MIN || r.height < MIN))
      small.push({ txt: (e.textContent || '').trim().slice(0, 22) || e.tagName,
                   w: +r.width.toFixed(1), h: +r.height.toFixed(1) });
  });
  return {
    clipped, small,
    pageOverflow: Math.max(0, document.documentElement.scrollWidth - window.innerWidth),
    counted: document.querySelectorAll(sel).length,
  };
}"""


def run(url, width, height, min_tap, selector, shot, settle):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url)
        pg.wait_for_timeout(settle)
        d = pg.evaluate(PROBE.replace("MIN", str(min_tap)), selector)
        d["jsErrors"] = errs
        if shot:
            pg.screenshot(path=shot, full_page=True)
        b.close()
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--width", type=int, default=390)
    ap.add_argument("--height", type=int, default=1400,
                    help="tall viewport avoids stitched screenshots and lays the whole page out")
    ap.add_argument("--min-tap", type=int, default=44)
    ap.add_argument("--selector", default="*")
    ap.add_argument("--shot")
    ap.add_argument("--settle", type=int, default=2200)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    d = run(a.url, a.width, a.height, a.min_tap, a.selector, a.shot, a.settle)

    if a.json:
        print(json.dumps(d, indent=1))
    else:
        print(f"{a.width}x{a.height}, {d['counted']} elements matched {a.selector!r}")
        for c in d["clipped"]:
            over = ", ".join(filter(None, [
                f"{c['overWide']}px too wide" if c["overWide"] else "",
                f"{c['overTall']}px too tall" if c["overTall"] else ""]))
            print(f"  CLIPPED  .{c['cls']} {c['txt']!r} — {over} for its {c['box']} box")
        for s in d["small"]:
            print(f"  SMALL    {s['txt']!r} is {s['w']}x{s['h']}, under {a.min_tap}")
        if d["pageOverflow"]:
            print(f"  OVERFLOW page is {d['pageOverflow']}px wider than the viewport")
        for e in d["jsErrors"]:
            print(f"  JS       {e[:130]}")
        if not (d["clipped"] or d["small"] or d["pageOverflow"] or d["jsErrors"]):
            print("  clean")

    return 1 if (d["clipped"] or d["small"] or d["pageOverflow"] or d["jsErrors"]) else 0


if __name__ == "__main__":
    sys.exit(main())
