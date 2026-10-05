#!/usr/bin/env python3
"""
webfonts.py — test with the real typefaces even though the browser cannot fetch them.

Headless Chromium in a sandboxed environment usually cannot load a font from a
CDN: the egress proxy re-signs TLS and the request is rejected. So every
screenshot silently uses the fallback stack, and the typeface the artifact
actually declares goes unrendered and unmeasured — sometimes for months.

`curl` has no such objection. Fetch the CSS, keep the faces whose
`unicode-range` covers Latin, fetch each woff2, base64 it, and inject the
`@font-face` rules with `add_style_tag`. No CDN is involved at render time.

Two things then become possible, and the second matters more:

  see     a screenshot in the intended typeface
  measure the width of real strings in both, which says whether a layout tuned
          against the fallback is safe in the real font. Anything under 1.0 is
          narrower and therefore safe; over 1.0 is where text starts to wrap a
          line further than the estimator expected.

  python3 checks/webfonts.py fetch "Archivo:wght@400;600;700" "IBM+Plex+Mono:wght@400"
  python3 checks/webfonts.py shot  <url> --out out/realfont.png
  python3 checks/webfonts.py measure <url> --strings "Data Mining,HLL 552,Applied I"
"""

import argparse
import base64
import json
import pathlib
import re
import subprocess
import sys

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122 Safari/537.36")
CACHE = pathlib.Path(__file__).resolve().parent.parent / "out" / "fonts.css"


def curl(url, binary=False, timeout=30):
    r = subprocess.run(["curl", "-sL", "-m", str(timeout), "-A", UA, url],
                       capture_output=True)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def fetch(families, latin_only=True):
    """Build a self-contained @font-face block. Desktop UA or you get ttf."""
    q = "&".join(f"family={f}" for f in families)
    css = curl(f"https://fonts.googleapis.com/css2?{q}&display=swap")
    if "@font-face" not in css:
        sys.exit("no @font-face came back — check the family strings")
    out, got = [], []
    for face in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S):
        fam = re.search(r"font-family:\s*'([^']+)'", face)
        wt = re.search(r"font-weight:\s*(\d+)", face)
        url = re.search(r"src:\s*url\(([^)]+)\)", face)
        ur = re.search(r"unicode-range:\s*([^;]+)", face)
        if not (fam and wt and url):
            continue
        if latin_only and "U+0000-00FF" not in (ur.group(1) if ur else ""):
            continue
        data = curl(url.group(1), binary=True)
        if len(data) < 800:
            continue
        out.append(f"@font-face{{font-family:'{fam.group(1)}';font-style:normal;"
                   f"font-weight:{wt.group(1)};src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(data).decode()}) format('woff2');}}")
        got.append(f"{fam.group(1)} {wt.group(1)} ({len(data):,} B)")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text("".join(out), encoding="utf-8")
    for g in got:
        print("  " + g)
    print(f"{len(got)} faces -> {CACHE} ({CACHE.stat().st_size:,} B)")
    return CACHE.read_text(encoding="utf-8")


def _css():
    if not CACHE.exists():
        sys.exit(f"no font cache at {CACHE} — run `webfonts.py fetch ...` first")
    return CACHE.read_text(encoding="utf-8")


def shot(url, out, width, height, settle):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
        pg.goto(url)
        pg.wait_for_timeout(settle)
        pg.add_style_tag(content=_css())
        pg.wait_for_timeout(1200)
        loaded = pg.evaluate("""async () => { await document.fonts.ready;
            return [...document.fonts].filter(f => f.status === 'loaded')
                                      .map(f => `${f.family} ${f.weight}`); }""")
        pg.screenshot(path=out, full_page=True)
        b.close()
    print(f"{out} — faces live: {', '.join(loaded) or 'none'}")


def measure(url, strings, real_sans, fb_sans, real_mono, fb_mono, px):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(url)
        pg.wait_for_timeout(1200)
        pg.add_style_tag(content=_css())
        pg.wait_for_timeout(800)
        d = pg.evaluate("""([strs, rs, fs, rm, fm, px]) => {
            const w = (t, fam) => {
              const s = document.createElement('span');
              s.style.cssText = `position:absolute;visibility:hidden;white-space:nowrap;
                                 font-size:${px}px;font-family:${fam}`;
              s.textContent = t; document.body.appendChild(s);
              const x = s.getBoundingClientRect().width; s.remove(); return +x.toFixed(2);
            };
            return strs.map(t => ({ t, sans: w(t, rs) / w(t, fs), mono: w(t, rm) / w(t, fm) }));
        }""", [strings, real_sans, fb_sans, real_mono, fb_mono, px])
        b.close()

    print(f"{'string':26} {'sans':>7} {'mono':>7}   ratio = real / fallback")
    for r in d:
        print(f"{r['t'][:26]:26} {r['sans']:7.3f} {r['mono']:7.3f}")
    ws, wm = [r["sans"] for r in d], [r["mono"] for r in d]
    print(f"\nsans {min(ws):.3f}–{max(ws):.3f}   mono {min(wm):.3f}–{max(wm):.3f}")
    if max(ws + wm) > 1.02:
        print("\nThe real font is more than 2% wider somewhere. A layout tuned "
              "against the fallback can wrap a line further than it expects.")
        return 1
    print("\nReal faces are no wider than the fallback; a layout tuned against "
          "the fallback has margin in the real one.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch"); f.add_argument("families", nargs="+")
    s = sub.add_parser("shot")
    s.add_argument("url"); s.add_argument("--out", default="out/realfont.png")
    s.add_argument("--width", type=int, default=390); s.add_argument("--height", type=int, default=1500)
    s.add_argument("--settle", type=int, default=2200)
    m = sub.add_parser("measure")
    m.add_argument("url"); m.add_argument("--strings", required=True)
    m.add_argument("--real-sans", default="'Archivo'")
    m.add_argument("--fb-sans", default="'Helvetica Neue',Helvetica,Arial,sans-serif")
    m.add_argument("--real-mono", default="'IBM Plex Mono'")
    m.add_argument("--fb-mono", default="ui-monospace,'SF Mono',Menlo,Consolas,monospace")
    m.add_argument("--px", type=float, default=9.5)
    a = ap.parse_args()

    if a.cmd == "fetch":
        fetch(a.families); return 0
    if a.cmd == "shot":
        shot(a.url, a.out, a.width, a.height, a.settle); return 0
    return measure(a.url, [x.strip() for x in a.strings.split(",") if x.strip()],
                   a.real_sans, a.fb_sans, a.real_mono, a.fb_mono, a.px)


if __name__ == "__main__":
    sys.exit(main())
