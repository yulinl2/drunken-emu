"""Tests for bin/figpipe --svg (external-SVG mode) and checks/svg_text_gates.py. No browser, no model.
    python3 -m unittest checks.test_external_svg
"""
import json, os, subprocess, sys, tempfile, unittest

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KIT)
from checks import svg_text_gates as tg  # noqa: E402

# a pure-analytic figure (no research data; this is a public toolkit repo). It is rendered by the bank itself,
# so it stands in for "an SVG some other tool made": the mode never looks at how the SVG was produced.
EX = os.path.join(KIT, "figbank", "examples")
SVG = os.path.join(EX, "majority-vote-curve.svg")
SPEC = os.path.join(EX, "majority-vote-curve.json")


def write(d, name, s):
    p = os.path.join(d, name)
    open(p, "w", encoding="utf-8").write(s)
    return p


class TextGates(unittest.TestCase):
    def test_an_svg_counts_text(self):
        g = tg.gates(SVG, budget=400, forbid=["lorem"])
        self.assertEqual(g["errors"], [])
        self.assertGreater(g["n_text"], 10)
        self.assertLess(g["words_non_numeric"], g["words"])

    def test_budget_forbidden_ellipsis_are_gates(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "a.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                                  '<text>one two three…</text><text><tspan>lorem</tspan> ipsum</text></svg>')
            errs = " | ".join(tg.gates(p, budget=3, forbid=["lorem"])["errors"])
            self.assertIn("word budget", errs)
            self.assertIn("forbidden", errs)
            self.assertIn("ellipsis", errs)

    def test_outlined_text_fails_loudly(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "o.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><path d="M0 0"/></svg>')
            self.assertTrue(any("no <text>" in e for e in tg.gates(p)["errors"]))


class FigpipeExternal(unittest.TestCase):
    def run_pipe(self, spec, svg, out):
        return subprocess.run([sys.executable, os.path.join(KIT, "bin", "figpipe"), spec, "--svg", svg,
                               "--out", out, "--reader", "none"], capture_output=True, text=True)

    def test_canvas_mismatch_is_an_error_not_a_rescale(self):
        with tempfile.TemporaryDirectory() as d:
            spec = json.load(open(SPEC))
            spec["canvas"] = {"width": 500, "height": 300}
            sp = write(d, "s.json", json.dumps(spec))
            r = self.run_pipe(sp, SVG, d)
            self.assertEqual(r.returncode, 2)
            self.assertIn("spec.canvas", r.stdout)

    def test_gate_failure_stops_before_raster_and_names_inapplicable_gates(self):
        with tempfile.TemporaryDirectory() as d:
            spec = json.load(open(SPEC))
            spec["word_budget"] = 10
            sp = write(d, "s.json", json.dumps(spec))
            r = self.run_pipe(sp, SVG, d)
            self.assertEqual(r.returncode, 2)
            self.assertIn("GATES THAT DO NOT APPLY", r.stdout)
            self.assertIn("word budget", r.stdout)
            rec = json.loads(open(os.path.join(d, "verdicts.jsonl")).read().splitlines()[-1])
            self.assertEqual(rec["mode"], "external-svg")
            self.assertTrue(rec["gates_not_applied"])
            self.assertFalse(rec["accepted"])

    def test_missing_svg_is_exit_2(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_pipe(SPEC, os.path.join(d, "nope.svg"), d)
            self.assertEqual(r.returncode, 2)

    def test_malformed_svg_is_exit_2_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as d:
            bad = write(d, "bad.svg", "<svg><text>oops")
            r = self.run_pipe(SPEC, bad, d)
            self.assertEqual(r.returncode, 2)
            self.assertNotIn("Traceback", r.stderr)


class Review(unittest.TestCase):
    def test_hidden_text_is_refused_not_counted(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "h.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                                  '<text>shown</text><text display="none">secret words</text></svg>')
            errs = " | ".join(tg.gates(p)["errors"])
            self.assertIn("hidden", errs)

    def test_transform_scale_shrinks_the_measured_font(self):
        # <g transform="scale(0.1)"><text font-size="12"> is 1.2 px on screen; the audit must say so
        sys.path.insert(0, KIT)
        from checks import svg_legibility as sl
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "t.svg", '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100" viewBox="0 0 200 100">'
                                  '<g transform="scale(0.1)"><text x="10" y="200" font-size="12">tiny on screen</text></g></svg>')
            from playwright.sync_api import sync_playwright
            from checks.browser import launch
            with sync_playwright() as pw:
                br = launch(pw)
                r = sl.audit(br.new_page(), p, 200, 8, 0.12)
                br.close()
            self.assertTrue(any(f["kind"] == "too_small" for f in r["faults"]), r)
            self.assertLess(r["min_font_px"], 2)


if __name__ == "__main__":
    unittest.main()
