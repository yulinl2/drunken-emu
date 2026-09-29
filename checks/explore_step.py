#!/usr/bin/env python3
"""explore_step — one stateless step of impaired exploration (P1, session-as-decider).

The decider is the CALLING SESSION, not an API model: each invocation replays the
recorded action trace from scratch (deterministic; chromium warm-launch ~0.4s),
optionally applies one new action, then reports what an impaired reader would
see. Decider-side impairments (working-memory, distractibility, patience) are
the session's contract; observation-side impairments are flags here.

  python3 checks/explore_step.py URL OUT TRACE [--act JSON] [--impulsivity] [--salience]
                                 [--viewport WxH] [--mouse] [--max-aff N]

TRACE is a JSON file: {"goal": str, "viewport": [w,h], "touch": bool, "actions": [ {kind,x,y,label}... ]}
--act JSON: {"kind":"tap","x":..,"y":..,"label":"why"}      touch tap (mouse click when the trace is mouse)
            {"kind":"click",...}                              alias of tap
            {"kind":"scroll","dy":..[,"x":..,"y":..]}         wheel, optionally over a point (scrolls that pane)
            {"kind":"key","key":"j"}                          one key press, e.g. "Control+Enter"
            {"kind":"type","text":"2.5"}                      types into whatever holds focus
            {"kind":"wait","ms":800}                          patience: let a slow response land before judging
--viewport / --mouse: only read when the trace is created (first call); after that the TRACE owns them,
            so replay is deterministic. Default stays 390x844 touch, as before.
--max-aff N: a reader who stops after N candidates (applied after --salience ordering).
Output: one JSON line {step, screenshot, affordances:[{text,x,y,w,h,salience,via,tag}], url, focus, errors}
  via = "semantic" (button/a/input/...) | "pointer-only" (cursor:pointer with no role: a reader can find it,
  a keyboard or screen-reader user cannot). Page errors seen during the replay are returned in `errors`.
"""
import asyncio, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from affordances import AFF_JS, settle
from playwright.async_api import async_playwright

URL, OUT, TRACE = sys.argv[1], sys.argv[2], sys.argv[3]
ACT = None; IMPULSIVE = "--impulsivity" in sys.argv; SALIENT = "--salience" in sys.argv
if "--act" in sys.argv: ACT = json.loads(sys.argv[sys.argv.index("--act")+1])
def _opt(name, default=None):
    return sys.argv[sys.argv.index(name)+1] if name in sys.argv else default
MAXAFF = int(_opt("--max-aff", 0))

async def main():
    try: tr = json.load(open(TRACE))
    except FileNotFoundError: tr = {"goal": "", "actions": []}
    if "viewport" not in tr:                                      # the trace owns device settings once created
        w, h = (int(v) for v in _opt("--viewport", "390x844").split("x"))
        tr["viewport"] = [w, h]; tr["touch"] = "--mouse" not in sys.argv
    if ACT: tr["actions"].append(ACT)
    async with async_playwright() as p:
        try: b = await p.chromium.launch()
        except Exception:                                         # pip's pinned revision != the container's (SANDBOX-FACTS)
            import glob; exe = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"), reverse=True)
            b = await p.chromium.launch(executable_path=exe[0])
        touch = tr.get("touch", True)
        pg = await b.new_page(viewport={"width":tr["viewport"][0],"height":tr["viewport"][1]}, device_scale_factor=2 if touch else 1, has_touch=touch)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)[:200]))
        pg.on("console", lambda m: m.type == "error" and errors.append(m.text[:200]))
        await pg.goto(URL, wait_until="domcontentloaded"); await settle(pg)   # data-fetching pages are not ready at DOMContentLoaded; polling pages never idle
        # React artifacts mount into #root; plain pages have no #root, so wait for any body content instead.
        await pg.wait_for_function("(document.getElementById('root')||document.body).children.length>0", timeout=15000)
        await pg.wait_for_timeout(250)                            # let the first render settle; the trace replays from a settled page
        for a in tr["actions"]:                                   # deterministic replay
            k = a["kind"]
            if k in ("tap", "click"):
                if touch: await pg.touchscreen.tap(a["x"], a["y"])
                else: await pg.mouse.click(a["x"], a["y"])
            elif k == "scroll":
                if "x" in a: await pg.mouse.move(a["x"], a["y"])
                await pg.mouse.wheel(0, a["dy"])
            elif k == "key": await pg.keyboard.press(a["key"])
            elif k == "type": await pg.keyboard.type(a["text"], delay=15)
            elif k == "wait": await pg.wait_for_timeout(a["ms"])                # e.g. let a slow fetch land
            await pg.wait_for_timeout(180)
        n = len(tr["actions"]); shot = f"{OUT}/explore_{n:02d}.png"
        await pg.screenshot(path=shot)
        aff = await pg.evaluate(AFF_JS)
        if SALIENT: aff.sort(key=lambda a:-a["salience"])          # big loud things first
        if IMPULSIVE: aff = aff[:max(1,int(len(aff)*0.6))]          # stop reading early
        if MAXAFF: aff = aff[:MAXAFF]
        json.dump(tr, open(TRACE,"w"))
        focus = await pg.evaluate("(()=>{const e=document.activeElement;return e&&e!==document.body?(e.tagName.toLowerCase()+(e.id?'#'+e.id:'')):null})()")
        print(json.dumps({"step":n,"screenshot":shot,"goal":tr["goal"],"url":pg.url,"viewport":tr["viewport"],"touch":touch,"focus":focus,
                          "errors":errors,"affordances":aff,"h":await pg.evaluate("document.body.scrollHeight")}))
        await b.close()
asyncio.run(main())
