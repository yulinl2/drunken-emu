#!/usr/bin/env python3
"""explore_run — scripted-decider impaired exploration and the dose-response sweep (P1, browser half).

`explore_step.py` lets the calling session decide each step. That is faithful but cannot be repeated 100 times.
This runner keeps the loop (observe -> decide -> act -> record) but the decider is a small policy script that holds a
*goal* and forms each intention from what the page shows, so a sweep over impairment levels is a command, not a chore.

  python3 checks/explore_run.py POLICY.py URL OUT --levels 0,0.1,0.2,0.3,0.4 --trials 10
          [--viewport 1366x768] [--mouse] [--budget 40] [--patience 6] [--seed 1] [--impulsivity] [--label NAME]

POLICY.py (plain module) defines:
    GOAL: str
    def reset(): optional, called before every trial (restore server-side state)
    async def progress(page) -> int          count of subgoals the READER can see are achieved (visible predicates only)
    async def done(page) -> bool             the reader believes the goal is met (visible predicate)
    def success() -> bool                    ground truth, may look anywhere (files, API); reported next to `done`
    async def decide(view, page, rng) -> dict | None
        view = affordances ordered loudest-first (checks/affordances.py); return one action:
        {"kind": "click"|"triple"|"key"|"type"|"scroll"|"wait", x,y | key | text | dy, "intention": str}

The runner owns the impairment (the policy cannot opt out of it):
    distractibility p   per step, with probability p the intended action is replaced by a click on the MOST SALIENT affordance
    patience k          abandon after k consecutive steps without the progress count reaching a new best
    impulsivity         (flag) the reader stops after the first 60% of the affordances
    budget              hard step limit (a censored run: neither success nor abandonment)
NOT implemented here: working-memory limits. They need decider-side memory, and these policies read the page instead of
remembering; claiming otherwise would be the kind of wrong justification README `## Falsified` row 3 is about.

Output: one table per run (rate of TRUE success per level, Wilson 95% interval, mean steps, hijacks, false completions)
and OUT/sweep_<label>.json with every trial. `false completion` = the reader believed it was done but ground truth says no.
"""
import argparse, asyncio, glob, importlib.util, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from affordances import AFF_JS
from playwright.async_api import async_playwright


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


def load_policy(path):
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))     # policies may share a helper module next to them
    spec = importlib.util.spec_from_file_location("policy", path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


async def observe(page, impulsive):
    aff = await page.evaluate(AFF_JS)
    aff.sort(key=lambda a: -a["salience"])                        # loud things first
    return aff[:max(1, int(len(aff) * 0.6))] if impulsive else aff


async def perform(page, a, touch):
    k = a["kind"]
    if k == "click":
        await (page.touchscreen.tap(a["x"], a["y"]) if touch else page.mouse.click(a["x"], a["y"]))
    elif k == "triple":
        await (page.touchscreen.tap(a["x"], a["y"]) if touch else page.mouse.click(a["x"], a["y"], click_count=3))
    elif k == "key": await page.keyboard.press(a["key"])
    elif k == "type": await page.keyboard.type(a["text"], delay=10)
    elif k == "scroll":
        if "x" in a: await page.mouse.move(a["x"], a["y"])
        await page.mouse.wheel(0, a["dy"])
    elif k == "wait": await page.wait_for_timeout(a.get("ms", 400))
    await page.wait_for_timeout(160)


async def trial(browser, pol, url, vp, touch, p, seed, args, shot=None):
    rng = random.Random(seed)
    if hasattr(pol, "reset"): pol.reset()
    ctx = await browser.new_context(viewport={"width": vp[0], "height": vp[1]}, has_touch=touch, device_scale_factor=1)
    page = await ctx.new_page(); errors = []
    page.on("pageerror", lambda e: errors.append(str(e)[:120]))
    await page.goto(url, wait_until="networkidle"); await page.wait_for_timeout(250)
    best, stall, hijacks, steps, why, believed = await pol.progress(page), 0, 0, 0, "budget", False
    log = []
    while steps < args.budget:
        view = await observe(page, args.impulsivity)
        d = await pol.decide(view, page, rng)
        hij = rng.random() < p and bool(view)
        if hij: a, note = {"kind": "click", "x": view[0]["x"], "y": view[0]["y"]}, "HIJACK " + view[0]["text"][:24]; hijacks += 1
        elif d is None: a, note = {"kind": "wait", "ms": 300}, "no idea what to do next"
        else: a, note = d, d.get("intention", "")
        try: await perform(page, a, touch)
        except Exception as e: note += f" [act failed: {type(e).__name__}]"
        steps += 1; log.append(note)
        prog = await pol.progress(page)
        if prog > best: best, stall = prog, 0
        else: stall += 1
        if await pol.done(page): believed = True; why = "believed-done"; break
        if stall >= args.patience: why = "abandoned"; break
    ok = bool(pol.success());
    if not ok and shot: await page.screenshot(path=shot)
    await ctx.close()
    return {"seed": seed, "p": p, "steps": steps, "hijacks": hijacks, "end": why, "believed_done": believed, "success": ok, "errors": errors[:2], "log": log[-8:]}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("policy"); ap.add_argument("url"); ap.add_argument("out")
    ap.add_argument("--levels", default="0,0.1,0.2,0.3,0.4"); ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--viewport", default="1366x768"); ap.add_argument("--mouse", action="store_true")
    ap.add_argument("--budget", type=int, default=40); ap.add_argument("--patience", type=int, default=6)
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--impulsivity", action="store_true"); ap.add_argument("--label", default="run")
    args = ap.parse_args()
    pol = load_policy(args.policy); vp = tuple(int(v) for v in args.viewport.split("x")); touch = not args.mouse
    os.makedirs(args.out, exist_ok=True); results = []
    async with async_playwright() as pw:
        try: browser = await pw.chromium.launch()
        except Exception:                                          # pip's pinned revision != the container's (SANDBOX-FACTS)
            exe = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"), reverse=True); browser = await pw.chromium.launch(executable_path=exe[0])
        print(f"goal: {pol.GOAL}\nviewport {vp} {'touch' if touch else 'mouse'} · budget {args.budget} · patience {args.patience} · trials/level {args.trials} · seed {args.seed}")
        print(f"{'p':>5} {'success':>9} {'95% CI':>13} {'mean steps':>11} {'hijacks':>8} {'false-done':>11} {'abandoned':>10} {'censored':>9}")
        for li, p in enumerate(float(x) for x in args.levels.split(",")):
            rs = []
            for t in range(args.trials):
                shot = f"{args.out}/{args.label}_p{p}_fail{t}.png" if t < 2 else None
                rs.append(await trial(browser, pol, args.url, vp, touch, p, args.seed * 1000 + li * 100 + t, args, shot))
            k = sum(r["success"] for r in rs); lo, hi = wilson(k, len(rs)); results += rs
            print(f"{p:5.2f} {k:>4}/{len(rs):<4} {lo:5.2f}-{hi:4.2f} {sum(r['steps'] for r in rs)/len(rs):11.1f} {sum(r['hijacks'] for r in rs)/len(rs):8.1f} "
                  f"{sum(1 for r in rs if r['believed_done'] and not r['success']):>11} {sum(r['end']=='abandoned' for r in rs):>10} {sum(r['end']=='budget' for r in rs):>9}", flush=True)
        await browser.close()
    json.dump({"goal": pol.GOAL, "args": vars(args), "trials": results}, open(f"{args.out}/sweep_{args.label}.json", "w"), indent=1)


asyncio.run(main())
