"""emu_loop: the loop's mechanics. No browser: the smoke layer is switched off or faked, and the chain layer
runs the real `bin/emu chain check` on the two real chain fixtures.

    python3 -m pytest -q checks/test_emu_loop.py

What this does NOT show: that the loop improves an artifact. That needs a chain captured from a driven run
(P-9d8b); here the chain is a fixture and the "edit" is a file copy. It pins the plumbing: who calls the
evaluator, what the verdict says, when the gate holds and when it lets go.
"""
import io
import json
import os
import shutil
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from checks import emu_loop as L  # noqa: E402

BAD = os.path.join(ROOT, "checks/fixtures/chains/hw1_correction_pass.json")        # recorded: 'expensive' trips the verifiers
GOOD = os.path.join(ROOT, "checks/fixtures/chains/hw1_correction_pass_fixed.json")  # designed: no findings


@pytest.fixture
def loop(tmp_path, monkeypatch):
    monkeypatch.setenv("EMU_LOOP_DIR", str(tmp_path / "state"))
    art = tmp_path / "demo.jsx"
    art.write_text("export default function A() { return null }\n")
    chain = tmp_path / "demo.chain.json"
    shutil.copy(BAD, chain)
    L.write_armed({"armed_at": L.now(), "watch": [str(art)], "chain": str(tmp_path / "{stem}.chain.json"),
                   "smoke": False, "max_rounds": 2})
    return art, chain


def context(result):
    return json.loads(result[1])["hookSpecificOutput"]["additionalContext"]


def fake_chain(load):
    return lambda path, timeout=20: {"status": "pass", "findings": 0, "load": load, "classes": {}, "top": [], "wall_s": 0}


def test_dominates():
    assert L.dominates({"a": 1, "b": 1}, {"a": 2, "b": 1})
    assert not L.dominates({"a": 1, "b": 2}, {"a": 2, "b": 1})   # a trade-off is not a regression
    assert not L.dominates({"a": 1}, {"a": 1})                   # equal is not better
    assert not L.dominates({"a": 1}, {"b": 0})                   # nothing in common, nothing to compare


def test_chain_layer_separates_the_known_bad_chain_from_the_known_good_one():
    bad, good = L.plug_chain(BAD), L.plug_chain(GOOD)
    assert (bad["status"], good["status"]) == ("fail", "pass")
    assert good["findings"] < bad["findings"] and good["load"] < bad["load"]
    assert bad["classes"], "no verifier class was parsed from the finding lines"


def test_smoke_layer_tells_a_broken_harness_from_a_broken_page(monkeypatch):
    def canned(result):
        return lambda cmd, timeout: result
    monkeypatch.setattr(L, "run", canned((1, "synced: root=<A/>\n", "Traceback\nModuleNotFoundError: No module named 'playwright'", 0.1)))
    r = L.plug_smoke("x.jsx")
    assert r["status"] == "not_evaluated" and "playwright" in r["why"]
    monkeypatch.setattr(L, "run", canned((1, 'synced: root=<A/>\n{"ok": false}\n', "", 0.1)))
    assert L.plug_smoke("x.jsx")["status"] == "fail"
    monkeypatch.setattr(L, "run", canned((0, '{"ok": true}\n', "", 0.1)))
    assert L.plug_smoke("x.jsx")["status"] == "go"


def test_disarmed_hooks_are_inert(tmp_path, monkeypatch):
    monkeypatch.setenv("EMU_LOOP_DIR", str(tmp_path / "state"))
    assert L.hook_post_edit({}) == (0, "", "")
    assert L.hook_stop({}) == (0, "", "")
    assert not os.path.exists(tmp_path / "state" / "ledger.jsonl")


def test_post_edit_feeds_back_goes_quiet_and_then_sees_an_improvement(loop):
    art, chain = loop
    first = context(L.hook_post_edit({"session_id": "s"}))
    assert "FAIL" in first and "chain_findings" in first and "NOT run" not in first
    assert "P1" in first and "P-9d8b" in first, "the feedback must say which layers were not run"
    assert L.hook_post_edit({}) == (0, "", "")                  # nothing changed: nothing said
    shutil.copy(GOOD, chain)                                    # the trial chain is re-recorded, better
    second = context(L.hook_post_edit({}))
    assert "PASS" in second and "improved" in second


def test_stop_is_refused_until_the_round_cap_then_released(loop):
    rc, out, err = L.hook_stop({})
    assert rc == 2 and "stop blocked 1/2" in err and "FAIL" in err
    assert L.hook_stop({})[0] == 2
    rc, out, err = L.hook_stop({})
    assert rc == 0 and "round cap" in out
    kinds = [r["kind"] for r in L.read_ledger()]
    assert kinds.count("stop_block") == 2 and kinds[-1] == "stop_allowed"


def test_stop_allows_a_passing_candidate(loop):
    art, chain = loop
    shutil.copy(GOOD, chain)
    assert L.hook_stop({})[0] == 0
    assert L.read_ledger()[-1]["reason"] == "gate pass"


def test_a_dominated_candidate_is_a_regression_and_blocks_the_stop(loop, monkeypatch):
    art, chain = loop
    monkeypatch.setattr(L, "plug_chain", fake_chain(2.5))
    L.hook_post_edit({})
    chain.write_text(chain.read_text() + " ")                   # the trial changed: a new candidate
    monkeypatch.setattr(L, "plug_chain", fake_chain(15.0))      # still passes, but at a higher load
    assert "REGRESSION" in context(L.hook_post_edit({}))
    rc, out, err = L.hook_stop({})
    assert rc == 2 and "REGRESSION" in err


def test_a_missing_trial_is_not_a_pass(loop):
    art, chain = loop
    chain.unlink()
    ctx = context(L.hook_post_edit({}))
    assert "NOT EVALUATED" in ctx and "no trial chain" in ctx
    assert L.hook_stop({})[0] == 2                              # fail-closed


def test_ledger_is_append_only_and_each_record_supersedes_the_last(loop):
    art, chain = loop
    L.hook_post_edit({})
    first = open(L._p("ledger.jsonl"), "rb").read()
    shutil.copy(GOOD, chain)
    L.hook_post_edit({})
    second = open(L._p("ledger.jsonl"), "rb").read()
    assert second.startswith(first) and len(second) > len(first)
    evals = [r for r in L.read_ledger() if r["kind"] == "eval"]
    assert evals[1]["supersedes"] == evals[0]["id"] and evals[1]["parent"] == evals[0]["sha"]
    assert os.path.exists(evals[0]["snapshot"])                 # the evaluated artifact is kept by hash


def test_the_cli_hook_prints_one_json_object(loop, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"session_id": "s", "tool_name": "Edit"})))
    with pytest.raises(SystemExit) as e:
        L.main(["hook", "post-edit"])
    assert e.value.code == 0
    assert json.loads(capsys.readouterr().out)["hookSpecificOutput"]["hookEventName"] == "PostToolUse"


def test_a_broken_hook_fails_open_and_says_so(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("EMU_LOOP_DIR", str(tmp_path / "state"))
    monkeypatch.setattr(L, "hook_stop", lambda payload: 1 / 0)
    monkeypatch.setattr(sys, "stdin", io.StringIO("{}"))
    with pytest.raises(SystemExit) as e:
        L.main(["hook", "stop"])
    assert e.value.code == 0 and "hook error" in capsys.readouterr().out


def test_arm_and_disarm_leave_a_trail(tmp_path, monkeypatch):
    monkeypatch.setenv("EMU_LOOP_DIR", str(tmp_path / "state"))
    L.main(["arm", "--watch", "x/*.jsx", "--chain", "c/{stem}.json"])
    assert L.load_armed()["max_rounds"] == 3
    L.main(["disarm"])
    assert L.load_armed() is None
    assert [r["kind"] for r in L.read_ledger()] == ["arm", "disarm"]
    with pytest.raises(SystemExit):
        L.main(["arm", "--watch", "x", "--no-smoke"])           # nothing to run is refused, not silently inert


def test_install_is_idempotent_and_keeps_other_hooks(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo hi"}]}]}}))
    L.install(str(p))
    L.install(str(p))
    cfg = json.loads(p.read_text())
    assert len(cfg["hooks"]["Stop"]) == 1 and len(cfg["hooks"]["PostToolUse"]) == 1
    assert cfg["hooks"]["SessionStart"][0]["hooks"][0]["command"] == "echo hi"
    assert "emu_loop.py" in cfg["hooks"]["Stop"][0]["hooks"][0]["command"]


def test_the_why_names_what_broke_not_the_banner_around_it(monkeypatch):
    err = ("Traceback (most recent call last):\n  File \"smoke.py\", line 9, in <module>\n"
           "playwright._impl._errors.Error: BrowserType.launch: Executable doesn't exist at /x/chrome\n"
           "╔════════╗\n║ Looks like Playwright was just installed or updated. ║\n║ <3 Playwright Team ║\n╚════════╝\n")
    monkeypatch.setattr(L, "run", lambda cmd, timeout: (1, "synced: root=<A/>\n", err, 0.1))
    r = L.plug_smoke("x.jsx")
    assert r["status"] == "not_evaluated" and "Executable doesn't exist" in r["why"]


def test_install_keeps_the_local_file_out_of_what_the_harness_stop_hook_flags(tmp_path, monkeypatch):
    import subprocess

    def untracked():   # the predicate of ~/.claude/stop-hook-git-check.sh
        return subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=tmp_path,
                              capture_output=True, text=True).stdout

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    monkeypatch.setattr(L, "ROOT", str(tmp_path))
    target = tmp_path / ".claude" / "settings.local.json"
    L.install(str(target))
    assert "settings.local.json" in untracked()                 # control: left alone, the hook would flag it
    L.keep_local(str(target))
    L.keep_local(str(target))                                   # idempotent
    assert untracked() == ""
    assert (tmp_path / ".git" / "info" / "exclude").read_text().count("settings.local.json") == 1


def test_a_watched_artifact_that_disappears_is_not_a_pass(loop, tmp_path):
    art, chain = loop
    shutil.copy(GOOD, chain)
    assert L.hook_stop({})[0] == 0                              # control: present and passing
    art.unlink()                                                # deleted, or renamed away
    rc, out, err = L.hook_stop({})
    assert rc == 2 and "gone" in err and "NOT EVALUATED" in err and "cp " in err
    art.write_text("export default function A() { return null }\n")
    L.main(["arm", "--watch", str(tmp_path / "*.jsx"), "--chain", str(tmp_path / "{stem}.chain.json"), "--no-smoke"])
    art.unlink()                                                # a pattern that found it when armed now finds nothing
    rc, out, err = L.hook_stop({})
    assert rc == 2 and "gone" in err


def test_a_verdict_is_reused_only_under_the_same_layers(loop, monkeypatch):
    art, chain = loop
    shutil.copy(GOOD, chain)
    assert L.hook_stop({})[0] == 0                              # armed chain-only: PASS
    L.write_armed({**L.load_armed(), "smoke": True})            # re-armed with smoke; the bytes are unchanged
    monkeypatch.setattr(L, "plug_smoke", lambda art, timeout=60: {"status": "fail", "json": {"ok": False}, "wall_s": 0})
    rc, out, err = L.hook_stop({})
    assert rc == 2 and "smoke" in err                           # the new layer ran; the chain-only PASS was not reused


def test_install_keeps_a_command_that_shares_a_group_with_the_hook(tmp_path):
    p = tmp_path / "settings.json"
    L.install(str(p))
    cfg = json.loads(p.read_text())
    cfg["hooks"]["Stop"][0]["hooks"].append({"type": "command", "command": "echo mine"})   # a user's own command
    p.write_text(json.dumps(cfg))
    L.install(str(p))
    cmds = [h["command"] for g in json.loads(p.read_text())["hooks"]["Stop"] for h in g["hooks"]]
    assert "echo mine" in cmds and sum("emu_loop.py" in c for c in cmds) == 1


def test_a_new_arming_gets_its_own_rounds_even_within_the_same_second(loop, tmp_path, monkeypatch):
    art, chain = loop                                           # the fixture's chain fails: every stop is refused
    monkeypatch.setattr(L, "now", lambda: "2026-10-18T19:00:00+00:00")   # every record in one second
    arm = ["arm", "--watch", str(art), "--chain", str(tmp_path / "{stem}.chain.json"), "--no-smoke", "--max-rounds", "2"]
    L.main(arm)
    assert [L.hook_stop({})[0] for _ in range(3)] == [2, 2, 0]  # two refusals, then the cap lets go
    L.main(arm)                                                 # re-armed within the same second
    rc, out, err = L.hook_stop({})
    assert rc == 2 and "stop blocked 1/2" in err                # a fresh budget, not the old arming's spent one


def test_a_pass_under_other_layers_is_no_baseline_for_a_regression(loop, monkeypatch, capsys):
    art, chain = loop
    monkeypatch.setattr(L, "plug_chain", fake_chain(1.0))
    L.hook_post_edit({})                                        # a chain-only pass at load 1
    L.write_armed({**L.load_armed(), "smoke": True})            # re-armed with smoke as well
    monkeypatch.setattr(L, "plug_smoke", lambda art, timeout=60: {"status": "go", "json": {"ok": True}, "wall_s": 0})
    art.write_text(art.read_text() + "// edited\n")             # a new candidate
    monkeypatch.setattr(L, "plug_chain", fake_chain(2.0))       # passes both layers, at a higher load
    ctx = context(L.hook_post_edit({}))
    assert "REGRESSION" not in ctx and "vs previous" not in ctx  # never smoke-checked: no baseline, and no "worse" either
    assert L.hook_stop({})[0] == 0
    L.main(["status"])
    fronts = [x for x in capsys.readouterr().out.splitlines() if x.startswith("frontier for")]
    assert len(fronts) == 2 and not any("none yet" in x for x in fronts)   # one frontier per config, each keeps its pass
