#!/usr/bin/env python3
"""
reading.py — what the reader pays.

The rest of this kit checks that a layout is *correct*: nothing clipped, nothing
too small, nothing overflowing. All of that can be true of something nobody can
read. The emu is not emulating a renderer — Chromium already does that, and
better. It is emulating a reader whose eye does not politely start at the top
left and proceed: it lands somewhere, skips, jumps back, and gives up on a wall.

So these five metrics ask a different question. Not "is it drawn right" but
"how much does it cost to get the answer out". Every one is mechanical, every
one has a threshold you can argue with, and none of them is a proxy for taste.

  echo    The same phrase, said twice in different places. The single most
          expensive thing a UI can do to a reader who already knows it: it has
          to be read, recognised as already-known, and discarded — three
          operations for zero information. Restating what the reader told you
          is the worst case, because they pay that cost on their own words.

  travel  Content that can only be decoded somewhere else. A key is load-
          bearing when the thing it explains does *not* say so itself: a block
          painted legend-blue whose text never mentions the room is a decoder
          ring, and the distance to the legend is a lookup the eye performs
          every single time. A block that spells the room out is self-
          sufficient and costs nothing, however far the legend is — so a token
          merely appearing twice is not a finding, and treating it as one was
          the first thing this metric got wrong.

  wall    The longest run of prose with no structural break. An eye that skips
          does not skip a bullet; it skips a paragraph. Measured in characters
          and reported in the seconds it costs at 200 wpm.

  fold    How far down the first thing you can act on sits. Everything above it
          is throat-clearing that has to be scrolled past on every visit.

  aim     The smallest interactive target. Not an ergonomic nicety — for a
          reader whose hand is already impatient, a 38px button is a second
          attempt, and a second attempt is where the thread gets dropped.

  python3 checks/reading.py <url>
  python3 checks/reading.py <url> --content ".rg-root" --json
  python3 checks/reading.py <url> --wall 320 --travel 400 --fold 1.0

Exit status is 1 on any finding, so it drops into a gate beside the geometry.
"""

import argparse
import json
import sys

from playwright.sync_api import sync_playwright

PROBE = r"""(cfg) => {
  const root = document.querySelector(cfg.content) || document.body;
  const norm = (s) => (s || "").replace(/\s+/g, " ").trim();
  const box = (e) => { const r = e.getBoundingClientRect();
                       return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; };

  // Leaf elements carrying their own words. Anything with element children is a
  // container and would double-count its descendants' text.
  const leaves = [...root.querySelectorAll("*")].filter(
    (e) => !e.children.length && norm(e.textContent).length > 1 &&
           e.getBoundingClientRect().height > 0);

  // ---- echo: the same phrase in two different places -----------------------
  const seen = new Map();
  for (const e of leaves) {
    const words = norm(e.textContent).toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fff ]+/g, " ").split(/\s+/).filter(Boolean);
    for (let n = cfg.echoWords; n <= Math.min(words.length, cfg.echoWords + 4); n++)
      for (let i = 0; i + n <= words.length; i++) {
        const k = words.slice(i, i + n).join(" ");
        if (!seen.has(k)) seen.set(k, []);
        seen.get(k).push({ txt: norm(e.textContent).slice(0, 60), y: box(e).y });
      }
  }
  const echo = [];
  for (const [phrase, where] of seen) {
    const spots = where.filter((w, i, a) => a.findIndex(z => Math.abs(z.y - w.y) < 4) === i);
    if (spots.length >= 2)
      echo.push({ phrase, times: spots.length,
                  spread: Math.round(Math.max(...spots.map(s => s.y)) -
                                     Math.min(...spots.map(s => s.y))),
                  where: spots.slice(0, 3).map(s => s.txt) });
  }
  // keep the longest phrase of each overlapping family
  echo.sort((a, b) => b.phrase.length - a.phrase.length);
  const kept = [];
  for (const e of echo)
    if (!kept.some(k => k.phrase.includes(e.phrase))) kept.push(e);

  // ---- travel: content that can only be decoded elsewhere -----------------
  // A key entry is a label plus a colour. Anything painted that colour whose
  // own text does not carry the label has to be looked up; anything that spells
  // the label out is self-sufficient no matter how far the key is.
  // Only paint that encodes something counts. Text colour does not: every
  // element inherits the same grey, so including it matched every key against
  // every paragraph on the page — which is how this metric first went wrong.
  // Alpha is dropped, because a 14%-opacity fill of a colour is that colour.
  const rgb = (c) => {
    const m = /rgba?\((\d+),\s*(\d+),\s*(\d+)/.exec(c || "");
    if (!m) return null;
    const v = [+m[1], +m[2], +m[3]];
    return Math.max(...v) - Math.min(...v) < 26 ? null : v.join(",");  // grey is chrome
  };
  const paint = (e) => {
    const cs = getComputedStyle(e);
    return [rgb(cs.backgroundColor), rgb(cs.borderLeftColor)].filter(Boolean);
  };
  const keys = [];
  for (const k of root.querySelectorAll(cfg.key)) {
    // The label is the key's name, not everything the row happens to contain.
    // A legend row reading "HLL 552" beside "17h 20m" concatenates to
    // "HLL 55217h 20m", which then matches nothing and makes every block look
    // like it needs decoding. Take the first labelled child, or the first text
    // node, before falling back to the whole row.
    const named = k.querySelector("[class*=name],[class*=label],[class*=title]");
    const firstText = [...k.childNodes].find(
      (n) => n.nodeType === 3 && norm(n.textContent).length > 1);
    const label = norm((named && named.textContent) ||
                       (firstText && firstText.textContent) || k.textContent);
    if (label.length < 2 || label.length > 24) continue;
    const sw = k.querySelector("[class*=swatch],[class*=dot],i,span") || k;
    const colours = paint(sw).concat(paint(k));
    if (!colours.length) continue;          // a key with no colour explains nothing
    keys.push({ label, k, colours });
  }
  const painted = [...root.querySelectorAll("*")]
    .filter((e) => e.getBoundingClientRect().height > 4);
  const travel = [];
  for (const key of keys) {
    let far = null;
    for (const e of painted) {
      if (e === key.k || key.k.contains(e) || e.contains(key.k)) continue;
      const txt = norm(e.textContent);
      if (txt.includes(key.label)) continue;              // says so itself
      if (!paint(e).some((c) => key.colours.includes(c))) continue;
      if (!txt || txt.length > 90) continue;              // a container, not a chip
      const d = Math.round(Math.hypot(box(e).x - box(key.k).x, box(e).y - box(key.k).y));
      if (!far || d > far.d) far = { d, txt: txt.slice(0, 40) };
    }
    if (far) travel.push({ token: key.label, px: far.d, farthest: far.txt });
  }
  travel.sort((a, b) => b.px - a.px);

  // ---- wall: longest unbroken prose ---------------------------------------
  const wall = leaves
    .map((e) => ({ chars: norm(e.textContent).length,
                   y: Math.round(box(e).y),
                   txt: norm(e.textContent).slice(0, 70) }))
    .sort((a, b) => b.chars - a.chars).slice(0, 6);

  // ---- fold: first thing you can act on -----------------------------------
  const acts = [...root.querySelectorAll("button, a[href], input, select, [role=button]")]
    .map((e) => ({ y: e.getBoundingClientRect().top + window.scrollY,
                   txt: norm(e.textContent).slice(0, 30) || e.tagName }))
    .filter((a) => a.y >= 0).sort((a, b) => a.y - b.y);

  // ---- aim: smallest target ------------------------------------------------
  const aim = [...root.querySelectorAll("button, a[href], input, select, [role=button]")]
    .map((e) => { const r = e.getBoundingClientRect();
                  return { w: +r.width.toFixed(1), h: +r.height.toFixed(1),
                           txt: norm(e.textContent).slice(0, 22) || e.tagName }; })
    .filter((t) => t.w > 0 && t.h > 0)
    .sort((a, b) => Math.min(a.w, a.h) - Math.min(b.w, b.h));

  return { echo: kept, travel: travel.slice(0, 8), wall,
           first: acts[0] || null, aim: aim.slice(0, 5),
           viewport: window.innerHeight, leaves: leaves.length };
}"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--content", default="body", help="the region a reader reads")
    ap.add_argument("--key", default=".legend,.key,[data-key],.rg-roomchip,.rg-swatch",
                    help="elements that define a token used elsewhere")
    ap.add_argument("--width", type=int, default=390)
    ap.add_argument("--height", type=int, default=1400)
    ap.add_argument("--settle", type=int, default=2200)
    ap.add_argument("--echo-words", type=int, default=3,
                    help="shortest phrase that counts as a repeat")
    ap.add_argument("--echo-spread", type=int, default=120,
                    help="px apart before a repeat is a separate place, not a label pair")
    ap.add_argument("--wall", type=int, default=320, help="chars of unbroken prose")
    ap.add_argument("--travel", type=int, default=420, help="px between token and meaning")
    ap.add_argument("--fold", type=float, default=1.0,
                    help="viewports before the first actionable thing")
    ap.add_argument("--aim", type=int, default=44)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": a.width, "height": a.height}, device_scale_factor=2)
        pg.goto(a.url)
        pg.wait_for_timeout(a.settle)
        d = pg.evaluate(PROBE, {"content": a.content, "key": a.key, "echoWords": a.echo_words})
        b.close()

    if a.json:
        print(json.dumps(d, indent=1, ensure_ascii=False))
        return 0

    findings = 0
    print(f"{a.width}px wide, {d['leaves']} text-bearing elements\n")

    ech = [e for e in d["echo"] if e["spread"] >= a.echo_spread]
    print(f"echo    phrases of {a.echo_words}+ words said in two places, "
          f"{a.echo_spread}px or further apart")
    for e in ech[:6]:
        print(f"        \"{e['phrase']}\" — {e['times']}x, {e['spread']}px apart")
        for w in e["where"][:2]:
            print(f"            {w!r}")
    findings += len(ech)
    if not ech:
        print("        none")

    tr = [t for t in d["travel"] if t["px"] >= a.travel]
    print(f"\ntravel  painted by a key that is {a.travel}px away, and not self-labelled")
    for t in tr[:5]:
        print(f"        {t['token']!r} colours {t['farthest']!r} from {t['px']}px away, "
              f"and that element never says it")
    findings += len(tr)
    if not tr:
        print("        none")

    wl = [w for w in d["wall"] if w["chars"] >= a.wall]
    print(f"\nwall    unbroken prose over {a.wall} characters")
    for w in wl:
        print(f"        {w['chars']} chars (~{w['chars']/5/200*60:.0f}s) at y={w['y']}: {w['txt']!r}")
    findings += len(wl)
    if not wl:
        print(f"        none — longest is {d['wall'][0]['chars'] if d['wall'] else 0}")

    print("\nfold    where the first actionable thing is")
    if d["first"]:
        vp = d["first"]["y"] / d["viewport"]
        bad = vp > a.fold
        print(f"        {d['first']['txt']!r} at y={d['first']['y']:.0f} "
              f"({vp:.2f} viewports){'  OVER' if bad else ''}")
        findings += 1 if bad else 0
    else:
        print("        nothing actionable on the page")

    sm = [t for t in d["aim"] if min(t["w"], t["h"]) < a.aim]
    print(f"\naim     interactive targets under {a.aim}px")
    for t in sm[:5]:
        print(f"        {t['txt']!r} is {t['w']}x{t['h']}")
    findings += len(sm)
    if not sm:
        print(f"        none — smallest is "
              f"{min(t['w'] for t in d['aim']):.0f}x{min(t['h'] for t in d['aim']):.0f}"
              if d["aim"] else "        no targets")

    print(f"\n{findings} findings" if findings else "\nnothing the reader pays twice for")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
