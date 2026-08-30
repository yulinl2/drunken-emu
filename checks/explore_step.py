#!/usr/bin/env python3
"""explore_step — one stateless step of impaired exploration (P1, session-as-decider).

The decider is the CALLING SESSION, not an API model: each invocation replays the
recorded action trace from scratch (deterministic; chromium warm-launch ~0.4s),
optionally applies one new action, then reports what an impaired reader would
see. Decider-side impairments (working-memory, distractibility, patience) are
the session's contract; observation-side impairments are flags here.

  python3 checks/explore_step.py URL OUT TRACE [--act JSON] [--impulsivity] [--salience]

TRACE is a JSON file: {"goal": str, "actions": [ {kind,x,y,label}... ]}
--act JSON: {"kind":"tap","x":..,"y":..,"label":"why"} | {"kind":"scroll","dy":..}
Output: one JSON line {step, screenshot, affordances:[{text,x,y,w,h,salience}], url}
"""
import asyncio, json, sys, time
from playwright.async_api import async_playwright

URL, OUT, TRACE = sys.argv[1], sys.argv[2], sys.argv[3]
ACT = None; IMPULSIVE = "--impulsivity" in sys.argv; SALIENT = "--salience" in sys.argv
if "--act" in sys.argv: ACT = json.loads(sys.argv[sys.argv.index("--act")+1])

async def main():
    try: tr = json.load(open(TRACE))
    except FileNotFoundError: tr = {"goal": "", "actions": []}
    if ACT: tr["actions"].append(ACT)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, has_touch=True)
        await pg.goto(URL); await pg.wait_for_function("document.getElementById('root').children.length>0", timeout=15000)
        for a in tr["actions"]:                                   # deterministic replay
            if a["kind"]=="tap": await pg.touchscreen.tap(a["x"], a["y"])
            elif a["kind"]=="scroll": await pg.mouse.wheel(0, a["dy"])
            await pg.wait_for_timeout(120)
        n = len(tr["actions"]); shot = f"{OUT}/explore_{n:02d}.png"
        await pg.screenshot(path=shot)
        aff = await pg.evaluate("""()=>{
          const cand=[...document.querySelectorAll('button,a,[role=button],input,select,[data-term]')];
          const vp={w:innerWidth,h:innerHeight};
          return cand.map(e=>{const r=e.getBoundingClientRect();
            const cs=getComputedStyle(e);
            const vis=r.width>0&&r.height>0&&r.bottom>0&&r.top<vp.h&&cs.visibility!=='hidden';
            if(!vis) return null;
            const area=r.width*r.height;
            const motion=(cs.animationName!=='none'||cs.transitionDuration!=='0s')?1.5:1;
            return {text:(e.textContent||e.value||'').trim().slice(0,40),
                    x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2),
                    w:Math.round(r.width), h:Math.round(r.height),
                    salience:Math.round(area*motion)};
          }).filter(Boolean);
        }""")
        if SALIENT: aff.sort(key=lambda a:-a["salience"])          # big loud things first
        if IMPULSIVE: aff = aff[:max(1,int(len(aff)*0.6))]          # stop reading early
        json.dump(tr, open(TRACE,"w"))
        print(json.dumps({"step":n,"screenshot":shot,"goal":tr["goal"],
                          "affordances":aff,"h":await pg.evaluate("document.body.scrollHeight")}))
        await b.close()
asyncio.run(main())
