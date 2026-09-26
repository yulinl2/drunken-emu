#!/usr/bin/env python3
"""svg_legibility.py — render an SVG in headless Chromium and audit it the way a phone
reader meets it: is every glyph big enough to read, does any label sit on top of another,
does anything fall outside the viewBox.

Extends the drunken-emu contract from React artifacts to static SVG figures. The existing
checks in a caller's own suite typically assert that an SVG is well-formed XML, is
self-contained, and has no empty <text> elements. None of those is a legibility claim:
a figure can pass all three and still be unreadable on a 380 px phone screen, which is
the reader this kit models.

Usage:
    python3 checks/svg_legibility.py FIG.svg [FIG2.svg ...] [--width 380] [--min-px 7.0]
                                    [--json OUT.json] [--quiet]

Exit 0 if every figure passes, 1 otherwise. Thresholds are arguments, not constants,
because the right floor depends on the delivery surface.
"""
import argparse, json, os, sys
from playwright.sync_api import sync_playwright

JS = """() => {
  const svg = document.querySelector('svg');
  const vb = svg.viewBox.baseVal;
  const box = svg.getBoundingClientRect();
  const scale = box.width / (vb && vb.width ? vb.width : box.width);
  const out = [];
  for (const t of svg.querySelectorAll('text')) {
    const r = t.getBoundingClientRect();
    const cs = getComputedStyle(t);
    out.push({text: (t.textContent||'').trim(),
              x: r.x - box.x, y: r.y - box.y, w: r.width, h: r.height,
              fontPx: parseFloat(cs.fontSize) * scale,
              fill: cs.fill, opacity: parseFloat(cs.fillOpacity || '1')});
  }
  let minX=1e9,minY=1e9,maxX=-1e9,maxY=-1e9;
  for (const e of svg.querySelectorAll('rect,circle,path,line,text,polygon,ellipse')) {
    const r = e.getBoundingClientRect();
    if (r.width===0 && r.height===0) continue;
    minX=Math.min(minX,r.x-box.x); minY=Math.min(minY,r.y-box.y);
    maxX=Math.max(maxX,r.x-box.x+r.width); maxY=Math.max(maxY,r.y-box.y+r.height);
  }
  return {texts: out, rendered: {w: box.width, h: box.height},
          ink: {minX, minY, maxX, maxY}, scale};
}"""

def overlap(a, b):
    ix = min(a['x']+a['w'], b['x']+b['w']) - max(a['x'], b['x'])
    iy = min(a['y']+a['h'], b['y']+b['h']) - max(a['y'], b['y'])
    if ix <= 0 or iy <= 0: return 0.0
    inter = ix*iy
    small = min(a['w']*a['h'], b['w']*b['h'])
    return inter/small if small > 0 else 0.0

def audit(page, path, width, min_px, overlap_tol):
    src = open(path, encoding='utf-8').read()
    page.set_viewport_size({'width': width, 'height': 900})
    page.set_content(f'<!doctype html><html><body style="margin:0">'
                     f'<div style="width:{width}px">{src}</div></body></html>')
    page.wait_for_timeout(60)
    d = page.evaluate(JS)
    faults = []
    for t in d['texts']:
        if t['fontPx'] < min_px:
            faults.append(dict(kind='too_small', px=round(t['fontPx'], 2), text=t['text'][:44]))
    ts = [t for t in d['texts'] if t['w'] > 0 and t['h'] > 0]
    for i in range(len(ts)):
        for j in range(i+1, len(ts)):
            o = overlap(ts[i], ts[j])
            if o > overlap_tol:
                faults.append(dict(kind='text_overlap', frac=round(o, 3),
                                   a=ts[i]['text'][:28], b=ts[j]['text'][:28]))
    ink, R = d['ink'], d['rendered']
    for side, val, lim in (('left', ink['minX'], 0), ('top', ink['minY'], 0)):
        if val < lim - 0.5:
            faults.append(dict(kind='ink_outside_viewbox', side=side, px=round(val, 1)))
    if ink['maxX'] > R['w'] + 0.5:
        faults.append(dict(kind='ink_outside_viewbox', side='right', px=round(ink['maxX']-R['w'], 1)))
    return dict(file=os.path.basename(path), n_text=len(d['texts']),
                rendered_width=round(R['w'], 1), scale=round(d['scale'], 4),
                min_font_px=round(min(([t['fontPx'] for t in d['texts']] or [0])), 2),
                faults=faults)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('svgs', nargs='+')
    ap.add_argument('--width', type=int, default=380, help='delivery viewport, default a phone')
    ap.add_argument('--min-px', type=float, default=7.0, help='smallest legible rendered font size')
    ap.add_argument('--overlap-tol', type=float, default=0.12,
                    help='fraction of the smaller label that may be covered before it is a fault')
    ap.add_argument('--json'); ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        for s in a.svgs:
            rows.append(audit(pg, s, a.width, a.min_px, a.overlap_tol))
        b.close()
    bad = 0
    for r in rows:
        ok = not r['faults']
        bad += 0 if ok else 1
        if not a.quiet:
            print(f"{'PASS' if ok else 'FAIL'}  {r['file']:46s} texts={r['n_text']:3d} "
                  f"min_font={r['min_font_px']:5.2f}px  faults={len(r['faults'])}")
            for f in r['faults'][:6]:
                print(f"        {f}")
    if a.json: json.dump(rows, open(a.json, 'w'), indent=1)
    if not a.quiet:
        print(f"\n{len(rows)-bad}/{len(rows)} figures legible at {a.width}px, floor {a.min_px}px")
    elif bad:
        # --quiet suppresses the per-figure log, never the reason for a non-zero exit:
        # a checker that fails without saying why costs the caller a second run.
        for r in rows:
            for f in r['faults']:
                print(f"{r['file']}: {f}")
        print(f"{bad}/{len(rows)} figures failed at {a.width}px, floor {a.min_px}px")
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
