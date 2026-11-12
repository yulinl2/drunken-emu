"""Use a relocated export, without the source tree on Python's import path."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "tools/export_loop.py"


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(("LOOP_", "GIT_", "PYTHON"))}
        self.env.update(HOME=str(self.base / "home"), GIT_CONFIG_GLOBAL=os.devnull,
                        PYTHONDONTWRITEBYTECODE="1")
        (self.base / "home").mkdir()
        self.package = self.base / "export"
        self.run_cmd(EXPORT, self.package)
        self.package.rename(self.base / "relocated")
        self.package = self.base / "relocated"
        self.project = self.package / "examples/loop-minimal"

    def run_cmd(self, script, *args, cwd=None, expected=0):
        result = subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)],
                                cwd=cwd or self.base, env=self.env, text=True,
                                capture_output=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def loop(self, *args, expected=0):
        return self.run_cmd(self.package / "bin/loop", *args, cwd=self.project, expected=expected)

    def records(self):
        return [json.loads(line) for line in (self.project / ".loop/watch.jsonl").read_text().splitlines()]

    def test_relocated_instance_pass_failure_input_and_checker_changes(self):
        doctor = json.loads(self.loop("doctor").stdout)
        self.assertTrue(doctor["loop_json"])
        self.assertFalse((self.project / ".loop").exists())
        evaluation = self.loop("watch", "eval")
        self.assertEqual(self.records()[-1]["gate"], "pass")
        self.assertIn("meaning", evaluation.stdout)
        self.assertIn("layers not run: meaning", evaluation.stdout)
        self.assertIn("PASS", self.loop("watch", "status").stdout)
        first = self.records()[-1]
        (self.project / "policy.json").write_text('{"required":"other"}')
        self.loop("watch", "eval", expected=1)
        second = self.records()[-1]
        self.assertEqual(first["sha"], second["sha"])
        self.assertNotEqual(first["cand"], second["cand"])
        self.assertEqual(second["gate"], "fail")
        checker = self.project / "check.py"
        checker.write_text(checker.read_text() + "\n# checker revision\n")
        self.loop("watch", "eval", expected=1)
        self.assertNotEqual(second["cand"], self.records()[-1]["cand"])
        (self.project / "policy.json").write_text("invalid json")
        self.loop("watch", "eval", expected=3)
        self.assertEqual(self.records()[-1]["gate"], "not_evaluated")
        self.assertFalse((self.base / "home/.claude").exists())
        self.assertFalse((self.project / "loop-state").exists())

    def test_byte_identity_modes_and_self_contained_verification(self):
        manifest = json.loads((self.package / "MANIFEST.json").read_text())
        self.assertEqual(len(manifest["source_head"]), 40)
        for name, rec in manifest["files"].items():
            if name != "README.md":
                self.assertEqual((self.package / name).read_bytes(), (ROOT / name).read_bytes())
            self.assertEqual(hashlib.sha256((self.package / name).read_bytes()).hexdigest(), rec["sha256"])
        self.assertFalse((self.package / ".git").exists())
        self.assertFalse((self.package / "checks").exists())
        self.assertFalse((self.package / "loop/mod/hooks/register.test.ts").exists())
        self.assertTrue((self.package / "loop/mod/hooks/register.ts").is_file())
        self.run_cmd(self.package / "tools/export_loop.py", "--verify", self.package)
        with (self.package / "loop/config.py").open("a") as stream:
            stream.write("\n# corruption\n")
        result = self.run_cmd(self.package / "tools/export_loop.py", "--verify", self.package, expected=1)
        self.assertIn("bytes changed: loop/config.py", result.stdout)

    def test_deterministic_manifest_and_existing_destination_preserved(self):
        second = self.base / "second"
        self.run_cmd(EXPORT, second)
        self.assertEqual((self.package / "MANIFEST.json").read_bytes(), (second / "MANIFEST.json").read_bytes())
        marker = second / "keep.txt"
        marker.write_text("preserve")
        self.run_cmd(EXPORT, second, expected=2)
        self.assertEqual(marker.read_text(), "preserve")

    def test_verifier_refuses_missing_and_symlinked_files(self):
        target = self.package / "examples/loop-minimal/artifact.json"
        target.unlink()
        target.symlink_to(ROOT / "examples/loop-minimal/artifact.json")
        result = self.run_cmd(self.package / "tools/export_loop.py", "--verify", self.package, expected=1)
        self.assertIn("missing or nonregular", result.stdout)


if __name__ == "__main__":
    unittest.main()
