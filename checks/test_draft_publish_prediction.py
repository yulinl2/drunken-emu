"""The prediction registered before the owner's first run of the draft publisher (docs/predictions/draft-publish-first-run.*).

Pins what the registration says it was made from, so that a later edit cannot pass as the original: the fixture, the measured file and the chain
check it carries. A change of the fixture is a NEW dated registration (regenerate with checks/draft_publish_prediction.py and a new id or date),
never an edit of this one. Stdlib only; no browser."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRED = ROOT / "docs/predictions/draft-publish-first-run.prediction.json"
sys.path.insert(0, str(ROOT / "checks"))
import prediction_score  # noqa: E402


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Registration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pred = json.loads(PRED.read_text(encoding="utf-8"))

    def test_the_fixture_and_the_measurement_are_the_ones_registered(self):
        for key in ("fixture", "measured", "scorer"):
            self.assertEqual(sha(ROOT / self.pred[key]["path"]), self.pred[key]["sha256"], f"{key} changed after registration: write a NEW dated registration, do not edit this one")

    def test_the_chain_check_it_carries_is_what_the_checker_says_now(self):
        r = subprocess.run([str(ROOT / "bin/emu"), "chain", "check", self.pred["fixture"]["path"], "--json"], cwd=ROOT, capture_output=True, text=True)
        self.assertIn(r.returncode, (0, 1), r.stderr)
        self.assertEqual(json.loads(r.stdout), self.pred["chain_check_json"])

    def test_every_event_names_a_real_step_with_its_op_and_a_probability_with_a_known_basis(self):
        fix = json.loads((ROOT / self.pred["fixture"]["path"]).read_text(encoding="utf-8"))
        steps = {c["id"]: c["steps"] for c in fix["chains"]}
        seen = set()
        for e in self.pred["events"]:
            self.assertNotIn(e["id"], seen); seen.add(e["id"])
            self.assertIn(e["basis"], self.pred["parameters"]["p_basis"]); self.assertTrue(0 < e["p"] < 1)
            self.assertIn(e["kind"], ("friction", "smooth"))
            for st in e["steps"]:
                self.assertEqual(steps[st["chain"]][st["step"] - 1]["op"], st["op"], e["id"])

    def test_the_scorer_reads_it_and_a_wrong_outcome_file_is_refused(self):
        out = {"schema": "emu-outcomes/1", "prediction": self.pred["id"], "events": {e["id"]: 0 for e in self.pred["events"]}, "durations_min": {}, "losses": [], "unregistered_frictions": [], "false_findings": []}
        r = prediction_score.score(self.pred, out)
        self.assertEqual(r["brier"]["n"], len(self.pred["events"])); self.assertFalse(r["kendall"]["scored"])
        out["events"]["NOPE"] = 1
        with self.assertRaises(prediction_score.OutcomesError): prediction_score.score(self.pred, out)

    def test_it_was_made_for_the_build_it_names_and_says_what_it_replaces(self):
        a = self.pred["artifact"]
        self.assertEqual(len(a["commit"]), 40); self.assertEqual(len(a["script_sha256"]), 64); self.assertEqual(len(a["delivered_file_sha256"]), 64)
        self.assertEqual(a["version"], "0.3.1")
        measured = json.loads((ROOT / self.pred["measured"]["path"]).read_text(encoding="utf-8"))
        self.assertEqual(measured["file"]["sha256"], a["delivered_file_sha256"])        # the geometry was measured on the file the owner holds, not on another build
        self.assertEqual(self.pred["supersedes"]["commit"], "3e87f6f5085a5c8533f5fe73e4396f2e8e98d80b")
        text = (ROOT / "docs/predictions/draft-publish-first-run.md").read_text(encoding="utf-8")
        self.assertIn("second registration", text); self.assertIn("It is void", text); self.assertIn("void for that run", text)

    def test_the_owner_is_asked_for_nothing(self):
        """CLAUDE.md of speeds-kit, rule 2: the owner's share is the sign-in and one tap; never narration or screenshots to collect"""
        leaves = self.pred["scoring"]["owner_leaves"]
        self.assertTrue(leaves.lower().startswith("nothing"), leaves)
        for word in ("narrat", "screenshot", "write down", "if you can"):
            self.assertNotIn(word, leaves.lower())
        text = (ROOT / "docs/predictions/draft-publish-first-run.md").read_text(encoding="utf-8")
        self.assertIn("Nothing. No narration, no screenshots, no clock.", text)
        for e in self.pred["events"]:
            self.assertNotIn("narration says", e["observable"], e["id"])                  # an observable the owner would have to produce on request

    def test_the_budget_is_two_and_no_chain_needs_more_and_the_hypothesis_is_stated(self):
        p = self.pred
        self.assertEqual(p["parameters"]["budget"], 2)
        self.assertEqual(max(s["peak_slots"] for s in p["segments"]), 2)
        findings = [f for c in p["chain_check_json"]["files"][0]["chains"] for f in c["findings"]]
        self.assertEqual([f for f in findings if f["verifier"] == "memory_budget"], [])        # the claim H-externalized makes: a memory finding would falsify it on paper
        self.assertIn("H-externalized", p["falsifiers"]); self.assertEqual(p["hypothesis"]["id"], "H-externalized")

if __name__ == "__main__":
    unittest.main()
