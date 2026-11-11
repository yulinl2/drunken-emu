"""verdict: the engine prints its own verdict (checks/verdict.py). No browser: the engine's process (`bin/emu smoke`)
is replaced by a stub; the chain layer runs the real `bin/emu chain check` on the two real fixtures.

    python3 -m pytest -q checks/test_verdict.py
"""
import json
import os
import runpy
import shutil
import subprocess
import sys
import threading
import time

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from checks import verdict as V  # noqa: E402

BAD = os.path.join(ROOT, "checks/fixtures/chains/hw1_correction_pass.json")        # recorded: 'expensive' trips the verifiers
GOOD = os.path.join(ROOT, "checks/fixtures/chains/hw1_correction_pass_fixed.json")  # designed: no findings
SCRIPT = os.path.join(ROOT, "checks", "verdict.py")
GO = (0, '{"mounted": true, "js_errors": []}\n', "", 0.1)                            # what `bin/emu smoke` answers
FAILS = (1, '{"mounted": true, "js_errors": ["ReferenceError: x is not defined"]}\n', "", 0.1)
NO_PLAYWRIGHT = (1, "synced: root=<A/>\n", "Traceback\nModuleNotFoundError: No module named 'playwright'", 0.1)


@pytest.fixture(autouse=True)
def lock_in_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(V, "LOCK", str(tmp_path / "out" / "verdict.lock"))   # no test writes into the kit's own out/


@pytest.fixture
def art(tmp_path):
    p = tmp_path / "demo.jsx"
    p.write_text("export default function A() { return null }\n")
    return str(p)


def engine(monkeypatch, smoke=None):
    """The engine's process is replaced by a stub: `bin/emu smoke` answers with `smoke`, and the test fails if the
    smoke layer runs without one. `bin/emu chain check` runs for real: it needs no browser."""
    real = V.run

    def fake(cmd, timeout):
        if cmd[2] != "smoke":
            return real(cmd, timeout)
        assert smoke is not None, "the smoke layer ran"
        return smoke
    monkeypatch.setattr(V, "run", fake)


def cli(capsys, *argv):
    rc = V.main(list(argv))
    lines = [x for x in capsys.readouterr().out.splitlines() if x.strip()]
    return rc, lines, json.loads(lines[-1])


def test_chain_layer_separates_the_known_bad_chain_from_the_known_good_one():
    bad, good = V.plug_chain(BAD), V.plug_chain(GOOD)
    assert (bad["status"], good["status"]) == ("fail", "pass")
    assert good["findings"] < bad["findings"] and good["load"] < bad["load"]
    assert bad["classes"], "no verifier class was parsed from the finding lines"


def test_smoke_layer_tells_a_broken_harness_from_a_broken_page(monkeypatch):
    def canned(result):
        return lambda cmd, timeout: result
    monkeypatch.setattr(V, "run", canned((1, "synced: root=<A/>\n", "Traceback\nModuleNotFoundError: No module named 'playwright'", 0.1)))
    r = V.plug_smoke("x.jsx")
    assert r["status"] == "not_evaluated" and "playwright" in r["why"]
    monkeypatch.setattr(V, "run", canned((1, 'synced: root=<A/>\n{"ok": false}\n', "", 0.1)))
    assert V.plug_smoke("x.jsx")["status"] == "fail"
    monkeypatch.setattr(V, "run", canned((0, '{"ok": true}\n', "", 0.1)))
    assert V.plug_smoke("x.jsx")["status"] == "go"


def test_the_why_names_what_broke_not_the_banner_around_it(monkeypatch):
    err = ("Traceback (most recent call last):\n  File \"smoke.py\", line 9, in <module>\n"
           "playwright._impl._errors.Error: BrowserType.launch: Executable doesn't exist at /x/chrome\n"
           "╔════════╗\n║ Looks like Playwright was just installed or updated. ║\n║ <3 Playwright Team ║\n╚════════╝\n")
    monkeypatch.setattr(V, "run", lambda cmd, timeout: (1, "synced: root=<A/>\n", err, 0.1))
    r = V.plug_smoke("x.jsx")
    assert r["status"] == "not_evaluated" and "Executable doesn't exist" in r["why"]


def test_a_pass_exits_0_and_the_last_line_is_the_verdict(art, monkeypatch, capsys):
    engine(monkeypatch, smoke=GO)
    rc, lines, v = cli(capsys, art, "--chain", GOOD)
    assert rc == 0 and (lines[0], lines[1]) == ("smoke: go", "chain: pass")
    assert v["gate"] == "pass" and v["layers"] == {"smoke": "go", "chain": "pass"}
    assert v["vector"]["smoke_fail"] == 0 and v["vector"]["chain_findings"] == 0 and v["vector"]["chain_load"] > 0
    assert any(V.NOT_YET in x for x in lines), "the output must say what the verdict does not judge"


def test_a_chain_fail_exits_1_and_its_line_names_the_first_finding(art, monkeypatch, capsys):
    engine(monkeypatch, smoke=GO)
    rc, lines, v = cli(capsys, art, "--chain", BAD)
    assert rc == 1 and v["gate"] == "fail" and v["layers"] == {"smoke": "go", "chain": "fail"}
    assert any(x.startswith("chain: fail  step ") for x in lines)
    assert v["vector"]["chain_findings"] > 0


def test_a_smoke_fail_exits_1_and_its_line_names_the_js_error(art, monkeypatch, capsys):
    engine(monkeypatch, smoke=FAILS)
    rc, lines, v = cli(capsys, art, "--chain", GOOD)
    assert rc == 1 and v["gate"] == "fail" and v["vector"]["smoke_fail"] == 1
    assert "smoke: fail  js error: ReferenceError: x is not defined" in lines


def test_a_layer_that_could_not_run_exits_3(art, monkeypatch, capsys):
    engine(monkeypatch, smoke=NO_PLAYWRIGHT)
    rc, lines, v = cli(capsys, art, "--chain", GOOD)
    assert rc == 3 and v["gate"] == "not_evaluated"
    assert v["layers"] == {"smoke": "not_evaluated", "chain": "pass"}
    assert any(x.startswith("smoke: not_evaluated  ") and "playwright" in x for x in lines)


def test_a_chain_file_that_is_not_there_is_not_a_pass(art, monkeypatch, capsys, tmp_path):
    engine(monkeypatch, smoke=GO)
    rc, lines, v = cli(capsys, art, "--chain", str(tmp_path / "none.json"))
    assert rc == 3 and v["gate"] == "not_evaluated" and v["layers"] == {"smoke": "go", "chain": "not_evaluated"}
    assert any(x.startswith("chain: not_evaluated  no trial chain at ") for x in lines)


def test_a_fail_outranks_a_layer_that_could_not_run(art, monkeypatch, capsys):
    engine(monkeypatch, smoke=NO_PLAYWRIGHT)
    rc, lines, v = cli(capsys, art, "--chain", BAD)
    assert rc == 1 and v["gate"] == "fail"                      # any layer failed: fail, whatever else did not run


def test_no_smoke_runs_the_chain_alone(art, monkeypatch, capsys):
    engine(monkeypatch, smoke=None)                             # the smoke layer must not run at all
    rc, lines, v = cli(capsys, art, "--no-smoke", "--chain", GOOD)
    assert rc == 0 and v["layers"] == {"chain": "pass"} and "smoke_fail" not in v["vector"]


def test_no_layer_at_all_is_not_evaluated(art, monkeypatch, capsys):
    engine(monkeypatch, smoke=None)
    rc, lines, v = cli(capsys, art, "--no-smoke")
    assert rc == 3 and v == {"gate": "not_evaluated", "vector": {}, "layers": {}}
    assert "no layer ran" in " ".join(lines)


def test_a_missing_artifact_is_not_evaluated_even_without_smoke(tmp_path, monkeypatch, capsys):
    engine(monkeypatch, smoke=None)                             # nothing is run against a file that is not there
    rc, lines, v = cli(capsys, str(tmp_path / "gone.jsx"), "--chain", GOOD)
    assert rc == 3 and v["gate"] == "not_evaluated" and v["layers"] == {}


def test_the_real_process_exits_with_the_gate(art):
    """No stub: the process itself, chain only, so no browser is needed."""
    for extra, rc, gate in ((["--chain", GOOD], 0, "pass"), (["--chain", BAD], 1, "fail"), ([], 3, "not_evaluated")):
        p = subprocess.run([sys.executable, SCRIPT, art, "--no-smoke", *extra], capture_output=True, text=True)
        assert p.returncode == rc, p.stdout + p.stderr
        assert json.loads(p.stdout.splitlines()[-1])["gate"] == gate


def test_bin_emu_verdict_gives_the_same_verdict(art):
    p = subprocess.run(["bash", os.path.join(ROOT, "bin", "emu"), "verdict", art, "--no-smoke", "--chain", GOOD],
                       capture_output=True, text=True)
    assert p.returncode == 0 and json.loads(p.stdout.splitlines()[-1])["gate"] == "pass"


def test_relative_paths_mean_the_same_from_any_directory(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "demo.jsx").write_text("export default function A() { return null }\n")
    shutil.copy(GOOD, tmp_path / "trial.json")
    rc, lines, v = cli(capsys, "demo.jsx", "--no-smoke", "--chain", "trial.json")
    assert rc == 0 and v["gate"] == "pass"                      # the chain layer runs from the project root


def test_a_layer_is_one_line_even_when_its_error_runs_over_several(art, monkeypatch, capsys):
    err = "console: ReferenceError: x is not defined\n    at App (<anonymous>:8:110)\n    at of (http://127.0.0.1:8123/vendor"
    engine(monkeypatch, smoke=(1, json.dumps({"mounted": False, "js_errors": [err]}) + "\n", "", 0.1))
    rc, lines, v = cli(capsys, art)
    assert rc == 1 and len(lines) == 3, lines                   # the layer, what is not in the verdict yet, the verdict
    assert lines[0].startswith("smoke: fail  js error: console: ReferenceError: x is not defined at App")


def test_two_smoke_runs_never_overlap(monkeypatch):
    """bin/emu smoke shares harness/app.jsx, out/srv.pid and a port with every other run of it: two verdicts at once gave each
    other's pages (observed: a page with a ReferenceError read `smoke: go`, a good page read its neighbour's error)."""
    live, peak, mutex = [0], [0], threading.Lock()

    def fake(cmd, timeout):
        with mutex:
            live[0] += 1
            peak[0] = max(peak[0], live[0])
        time.sleep(0.15)
        with mutex:
            live[0] -= 1
        return GO
    monkeypatch.setattr(V, "run", fake)
    runs = [threading.Thread(target=V.plug_smoke, args=("x.jsx",)) for _ in range(3)]
    for r in runs:
        r.start()
    for r in runs:
        r.join()
    assert peak[0] == 1, f"{peak[0]} smoke runs at once"


def test_bin_emu_without_a_mode_names_verdict_among_the_modes():
    p = subprocess.run(["bash", os.path.join(ROOT, "bin", "emu")], capture_output=True, text=True)
    assert p.returncode != 0 and "verdict" in p.stderr, p.stderr


def test_a_crash_of_the_check_itself_is_not_evaluated_not_a_fail(art, monkeypatch, capsys):
    """An uncaught exception exits 1, which the harness reads as a fail of the page. The check broke; the page was not judged."""
    def boom(*args, **kwargs):
        raise RuntimeError("boom")
    monkeypatch.setattr(subprocess, "run", boom)
    monkeypatch.setattr(sys, "argv", [SCRIPT, art, "--no-smoke", "--chain", GOOD])
    with pytest.raises(SystemExit) as e:
        runpy.run_path(SCRIPT, run_name="__main__")
    lines = [x for x in capsys.readouterr().out.splitlines() if x.strip()]
    assert e.value.code == 3 and "verdict.py broke: RuntimeError: boom" in lines[0]
    assert json.loads(lines[-1]) == {"gate": "not_evaluated", "vector": {}, "layers": {}}
