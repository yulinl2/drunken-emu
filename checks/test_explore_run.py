#!/usr/bin/env python3
"""Positive control for explore_run.py: the impairment must actually bite, and must not when it is off.

A page with one big decoy button and one small target button. The policy always intends to press the target.
  p = 0  -> every trial succeeds (the policy and the runner work)
  p = 1  -> every step is hijacked onto the loudest element, the decoy: no trial succeeds, hijacks == steps
A sweep whose curve cannot move proves nothing; this is the known-bad input that makes it move.
Needs Chromium (see SANDBOX-FACTS); not wired into the text-only CI job.   python3 checks/test_explore_run.py
"""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
PAGE = """<!doctype html><meta charset=utf-8><body style="margin:0">
<button id=decoy style="width:600px;height:300px;font-size:30px" onclick="document.title='decoy'">BIG LOUD DECOY</button>
<button id=goal style="width:90px;height:30px" onclick="document.title='goal';document.getElementById('o').textContent='reached'">Go</button>
<p id=o></p></body>"""
POLICY = '''
GOAL = "press the small Go button"
_won = {"v": False}
def reset(): _won["v"] = False
def success(): return _won["v"]
async def progress(page):
    _won["v"] = (await page.title()) == "goal"
    return 1 if _won["v"] else 0
async def done(page): return await page.title() == "goal"
async def decide(view, page, rng):
    b = next((a for a in view if a["text"] == "Go"), None)
    return {"kind": "click", "x": b["x"], "y": b["y"], "intention": "press Go", "rationale": "the small button is the goal"} if b else None
'''


class T(unittest.TestCase):
    def run_sweep(self, levels, trials=4, policy=POLICY, mouse=True, expect_ok=True):
        d = Path(tempfile.mkdtemp()); (d / "page.html").write_text(PAGE); (d / "pol.py").write_text(policy)
        r = subprocess.run([sys.executable, str(KIT / "checks/explore_run.py"), str(d / "pol.py"), (d / "page.html").as_uri(), str(d / "out"),
                            "--levels", levels, "--trials", str(trials), *(["--mouse"] if mouse else []), "--budget", "6", "--patience", "6", "--label", "t"],
                           capture_output=True, text=True, timeout=120)
        if not expect_ok: return r
        self.assertEqual(r.returncode, 0, r.stderr[-400:])
        return json.load(open(d / "out/sweep_t.json"))["trials"]

    def test_every_step_keeps_intention_action_target_rationale(self):
        t = self.run_sweep("0,1", trials=2)
        for trial in t:
            for st in trial["log"]:
                self.assertTrue(st["intention"] and st["rationale"] and st["action"]["kind"] and st["target"] is not None, st)
        clean = [s for x in t if x["p"] == 0 for s in x["log"]]; drunk = [s for x in t if x["p"] == 1 for s in x["log"]]
        self.assertTrue(all("Go" in s["target"] for s in clean), clean)                     # aimed at the goal button
        self.assertTrue(all(s["hijacked"] and "DECOY" in s["target"] for s in drunk), drunk)  # the hijack landed on the loud decoy

    def test_a_policy_that_breaks_the_contract_stops_the_run(self):
        no_rationale = POLICY.replace(', "rationale": "the small button is the goal"', "")
        r = self.run_sweep("0", trials=1, policy=no_rationale, expect_ok=False)
        self.assertNotEqual(r.returncode, 0); self.assertIn("rationale", r.stderr)
        triple = POLICY.replace('"kind": "click"', '"kind": "triple"')
        r = self.run_sweep("0", trials=1, policy=triple, mouse=False, expect_ok=False)      # touch device: triple must be refused, not downgraded to a tap
        self.assertNotEqual(r.returncode, 0); self.assertIn("touch", r.stderr)
        bogus = POLICY.replace('"kind": "click"', '"kind": "teleport"')
        r = self.run_sweep("0", trials=1, policy=bogus, expect_ok=False); self.assertNotEqual(r.returncode, 0); self.assertIn("unknown action kind", r.stderr)

    def test_impairment_bites_only_when_on(self):
        t = self.run_sweep("0,1")
        clean = [x for x in t if x["p"] == 0]; drunk = [x for x in t if x["p"] == 1]
        self.assertTrue(all(x["success"] for x in clean), clean)
        self.assertFalse(any(x["success"] for x in drunk), drunk)
        self.assertTrue(all(x["hijacks"] == x["steps"] for x in drunk))


if __name__ == "__main__":
    unittest.main()
