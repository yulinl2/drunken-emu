#!/usr/bin/env python3
"""region_shots.py — screenshot the viewport around given text anchors.

This is the ONE content-aware tool in the kit, and it is fenced accordingly:
anchors decide only WHERE to point the camera, never WHAT counts as correct.
Use it after an edit to re-photograph exactly the regions you changed; judge
the photographs by eye. (For content-blind auditing use blind_audit.py.)

Anchor matching picks the TIGHTEST element containing the text (shortest
textContent), not the first — outer wrappers contain everything and would
always win a document-order search. That bug cost one debugging round; the
sort is the fix.

Usage: region_shots.py <url> <out_dir> "anchor1" "anchor2" ...
Each anchor i produces <out_dir>/R_<i>_<slug>.png; prints found/not per anchor.
"""
import asyncio
import json
import re
import sys

from playwright.async_api import async_playwright

URL, OUT = sys.argv[1], sys.argv[2]
ANCHORS = sys.argv[3:]

async def main():
    res = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(
            args=["--ignore-certificate-errors", "--no-sandbox", "--disable-dev-shm-usage"])
        c = await b.new_context(viewport={"width": 390, "height": 844},
                                has_touch=True, is_mobile=True, device_scale_factor=2)
        pg = await c.new_page()
        await pg.goto(URL, timeout=20000)
        await pg.wait_for_function(
            "document.getElementById('root').children.length > 0", timeout=15000)
        await pg.wait_for_timeout(600)
        for i, a in enumerate(ANCHORS):
            ok = await pg.evaluate("""(t)=>{
              const cands=[...document.querySelectorAll('p,li,td,th,b,h1,h2,h3,span,pre,div')]
                .filter(e=>e.textContent.includes(t));
              cands.sort((x,y)=>x.textContent.length-y.textContent.length);
              if(!cands.length) return false;
              cands[0].scrollIntoView({block:'center'});
              return true;}""", a)
            await pg.wait_for_timeout(430)
            slug = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", a)[:24]
            await pg.screenshot(path=f"{OUT}/R_{i}_{slug}.png")
            res[a] = bool(ok)
        await b.close()
    print(json.dumps(res, ensure_ascii=False))
    return 0 if all(res.values()) else 1

sys.exit(asyncio.run(main()))
