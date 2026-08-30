#!/usr/bin/env python3
"""blind_audit.py — content-blind interaction + ergonomics audit.

Design principle (the anti-leak rule): the script may know CONVENTIONS
(dashed underline = tappable, a row of 2-6 sibling buttons = a control
cluster) but never CONTENT (no button labels, no term names, no expected
strings). Interactions are found by computed style and geometry at runtime;
correctness is judged afterwards by a human/model LOOKING at the numbered
screenshots — the script only asserts mechanics (opened? closed? no JS
error? no overflow?).

Checks, in order:
  A. render + zero JS errors + zero horizontal overflow
  B. touch ergonomics: every visible non-decorative <button> >= min_px tall;
     every [data-term] hit-span >= min_px (convention-specific, skipped if absent)
  C. tap the first dashed-decorated element in view -> did a fixed bottom
     layer appear? tap outside it -> did it close?
  D. find the first cluster of 3-6 sibling buttons (a stepper/pager), tap the
     3rd repeatedly -> screenshots for visual judgment
  E. find the first row of exactly 2 non-term buttons (a toggle), tap the 2nd
  F. read-through: screenshot at N evenly spaced scroll positions

Usage: blind_audit.py <url> <out_dir> [n_read_stops=8] [min_px=38]
Prints one JSON line; screenshots land in <out_dir> as A_*.png ... F_*.png.
"""
import asyncio
import json
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/harness.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
N_STOPS = int(sys.argv[3]) if len(sys.argv) > 3 else 8
MIN_PX = int(sys.argv[4]) if len(sys.argv) > 4 else 38

R = {"js_errors": [], "checks": {}}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(
            args=["--ignore-certificate-errors", "--no-sandbox", "--disable-dev-shm-usage"])
        c = await b.new_context(viewport={"width": 390, "height": 844},
                                has_touch=True, is_mobile=True, device_scale_factor=2)
        pg = await c.new_page()
        pg.on("pageerror", lambda e: R["js_errors"].append(str(e)[:160]))
        pg.on("console", lambda x: R["js_errors"].append("console: " + x.text[:120])
              if x.type == "error" else None)
        await pg.goto(URL, timeout=20000)
        try:
            await pg.wait_for_function(
                "document.getElementById('root').children.length > 0", timeout=15000)
        except Exception:
            R["checks"]["mounted"] = False
            print(json.dumps(R, ensure_ascii=False))
            await b.close()
            return 1
        R["checks"]["mounted"] = True
        await pg.wait_for_timeout(800)
        await pg.screenshot(path=f"{OUT}/A_00_landing.png")

        async def scroll_to(frac=None, delta=None):
            await pg.evaluate("""(a)=>{
              const sc=[...document.querySelectorAll('*')]
                .filter(e=>e.scrollHeight>e.clientHeight+1000)
                .sort((x,y)=>y.scrollHeight-x.scrollHeight)[0] || document.scrollingElement;
              if(a.frac!=null) sc.scrollTop=(sc.scrollHeight-sc.clientHeight)*a.frac;
              if(a.delta!=null) sc.scrollTop+=a.delta;
            }""", {"frac": frac, "delta": delta})
            await pg.wait_for_timeout(420)

        # B. ergonomics
        R["checks"]["ergonomics"] = await pg.evaluate("""(MIN)=>{
          const vis=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0};
          const btns=[...document.querySelectorAll('button')]
            .filter(b=>!b.hasAttribute('data-term')).filter(vis);
          const small=btns.map(b=>Math.round(b.getBoundingClientRect().height))
                          .filter(h=>h<MIN);
          const hits=[...document.querySelectorAll('[data-term] > span[aria-hidden]')]
            .map(s=>Math.round(s.getBoundingClientRect().height)).filter(h=>h>0);
          return {buttons: btns.length, buttons_under_min: small.length,
                  term_hits: hits.length,
                  term_hit_min_px: hits.length?Math.min(...hits):null,
                  term_hit_status: hits.length?'checked'
                    :'SKIPPED: no [data-term] convention in this artifact'};
        }""", MIN_PX)

        # C. dashed-element tap -> sheet open -> outside tap -> closed
        await scroll_to(delta=700)
        pt = await pg.evaluate("""()=>{
          for(const el of document.querySelectorAll('span,button,a')){
            const cs=getComputedStyle(el), r=el.getBoundingClientRect();
            if(r.top>110&&r.bottom<790&&r.width>4&&
               (cs.textDecorationStyle==='dashed'||cs.borderBottomStyle==='dashed'))
              return {x:r.x+r.width/2,y:r.y+r.height/2};
          } return null;}""")
        if pt:
            await pg.touchscreen.tap(pt["x"], pt["y"])
            await pg.wait_for_timeout(500)
            opened = await pg.evaluate("""()=>[...document.querySelectorAll('div')].some(d=>{
              const cs=getComputedStyle(d),r=d.getBoundingClientRect();
              return cs.position==='fixed'&&r.bottom>800&&r.height>110;})""")
            await pg.screenshot(path=f"{OUT}/C_01_after_dashed_tap.png")
            await pg.touchscreen.tap(195, 140)
            await pg.wait_for_timeout(420)
            closed = await pg.evaluate("""()=>![...document.querySelectorAll('div')].some(d=>{
              const cs=getComputedStyle(d),r=d.getBoundingClientRect();
              return cs.position==='fixed'&&r.bottom>800&&r.height>110;})""")
            await pg.screenshot(path=f"{OUT}/C_02_after_outside_tap.png")
            R["checks"]["overlay"] = {"opened": opened, "closed": closed}
        else:
            R["checks"]["overlay"] = "no dashed element found"

        # D. control cluster (3-6 sibling buttons): tap 3rd x6
        got = await pg.evaluate("""()=>{
          for(const d of document.querySelectorAll('div')){
            const bs=[...d.children].filter(c=>c.tagName==='BUTTON'&&!c.hasAttribute('data-term'));
            if(bs.length>=3&&bs.length<=6){
              d.scrollIntoView({block:'center'});
              const r=bs[2].getBoundingClientRect();
              return {x:r.x+r.width/2,y:r.y+r.height/2,n:bs.length};
            }} return null;}""")
        await pg.wait_for_timeout(400)
        if got:
            for _ in range(6):
                await pg.touchscreen.tap(got["x"], got["y"])
                await pg.wait_for_timeout(170)
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=f"{OUT}/D_01_cluster_after_6taps.png")
            R["checks"]["cluster"] = {"buttons": got["n"], "tapped_3rd_x6": True}
        else:
            R["checks"]["cluster"] = "none found"

        # E. 2-button toggle (excluding term buttons and rows that contain terms)
        got2 = await pg.evaluate("""()=>{
          for(const d of document.querySelectorAll('div')){
            const kids=[...d.children];
            const bs=kids.filter(c=>c.tagName==='BUTTON'&&!c.hasAttribute('data-term'));
            const terms=kids.filter(c=>c.hasAttribute&&c.hasAttribute('data-term'));
            if(bs.length===2&&terms.length===0){
              d.scrollIntoView({block:'center'});
              const r=bs[1].getBoundingClientRect();
              return {x:r.x+r.width/2,y:r.y+r.height/2};
            }} return null;}""")
        await pg.wait_for_timeout(400)
        if got2:
            await pg.touchscreen.tap(got2["x"], got2["y"])
            await pg.wait_for_timeout(1000)
            await pg.screenshot(path=f"{OUT}/E_01_toggle_second.png")
            R["checks"]["toggle"] = True
        else:
            R["checks"]["toggle"] = "none found"

        # F. read-through
        for i in range(N_STOPS):
            f = (i + 1) / N_STOPS
            await scroll_to(frac=f)
            await pg.screenshot(path=f"{OUT}/F_read_{i:02d}_{int(f*100)}.png")

        R["checks"]["h_overflow_px"] = await pg.evaluate(
            "document.documentElement.scrollWidth - window.innerWidth")
        await b.close()
    print(json.dumps(R, ensure_ascii=False))
    ok = (not R["js_errors"]
          and R["checks"].get("h_overflow_px") == 0
          and R["checks"].get("ergonomics", {}).get("buttons_under_min") == 0)
    return 0 if ok else 1

sys.exit(asyncio.run(main()))
