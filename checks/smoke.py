#!/usr/bin/env python3
"""smoke.py — fastest possible go/no-go: does the artifact render at all?
Also the kit's timing probe: reports per-phase wall clock so efficiency
claims are measured, not guessed.

Usage: smoke.py <url> [out_dir]
Prints one JSON line: phases (s), root child count, js errors, overflow px.
"""
import asyncio
import json
import sys
import time

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/harness.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "."

async def main():
    t = {}
    t0 = time.monotonic()
    async with async_playwright() as p:
        b = await p.chromium.launch(
            args=["--ignore-certificate-errors", "--no-sandbox", "--disable-dev-shm-usage"])
        t["launch_chromium"] = round(time.monotonic() - t0, 2)

        c = await b.new_context(viewport={"width": 390, "height": 844},
                                has_touch=True, is_mobile=True, device_scale_factor=2)
        pg = await c.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
        pg.on("console", lambda x: errs.append("console: " + x.text[:120])
              if x.type == "error" else None)

        t1 = time.monotonic()
        await pg.goto(URL, timeout=20000)
        t["goto_load"] = round(time.monotonic() - t1, 2)

        # wait until React has actually mounted something (Babel compile included)
        t2 = time.monotonic()
        try:
            await pg.wait_for_function(
                "document.getElementById('root') && document.getElementById('root').children.length > 0",
                timeout=15000)
            mounted = True
        except Exception:
            mounted = False
        t["babel_compile_and_mount"] = round(time.monotonic() - t2, 2)

        n = await pg.evaluate("document.getElementById('root').children.length")
        # rendered DOM node count: the variable that actually drives mount time
        # (measured: mount ≈ 0.15 s fixed + ~0.6 ms per rendered node; source
        #  BYTE count is nearly irrelevant — 80 KB of comments costs 0.19 s)
        dom = await pg.evaluate("document.getElementById('root').querySelectorAll('*').length")
        ov = await pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        t3 = time.monotonic()
        await pg.screenshot(path=f"{OUT}/smoke_hero.png")
        t["one_screenshot"] = round(time.monotonic() - t3, 2)

        await b.close()
        t["total"] = round(time.monotonic() - t0, 2)
    print(json.dumps({"phases_s": t, "mounted": mounted, "root_children": n,
                      "dom_nodes": dom,
                      "js_errors": errs, "h_overflow_px": ov}, ensure_ascii=False))
    return 0 if (mounted and not errs) else 1

sys.exit(asyncio.run(main()))
