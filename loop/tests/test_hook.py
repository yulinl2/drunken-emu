"""loop/hook.py: the hooks a session fires, the install that registers them, and the stop that is refused a capped number of times.

Every test runs in temporary folders with a temporary HOME; none reads or writes the settings of the machine it runs on."""
import json, os, pathlib, subprocess, sys

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import config, hook  # noqa: E402

BIN_LOOP = config.KIT / "bin" / "loop"


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A temporary project root and a temporary HOME, named by the environment; no LOOP_ variable of this machine leaks in."""
    root, home = (tmp_path / "project").resolve(), (tmp_path / "home").resolve()
    root.mkdir()
    home.mkdir()
    (root / "loop.json").write_text("{}", encoding="utf-8")   # a project names itself
    for name in [k for k in os.environ if k.startswith("LOOP_")]:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LOOP_PROJECT", str(root))
    monkeypatch.setenv("HOME", str(home))
    return root, home


@pytest.fixture
def trials(monkeypatch):
    """Install's sample-payload trials: the verb guard has no module in the kit yet (exit 3), every other command exits 0."""
    def fake(cmd):
        return subprocess.CompletedProcess(cmd, 3 if " guard pre" in cmd else 0, "", "")
    monkeypatch.setattr(hook, "_trial", fake)


def _run(args, root, home, stdin=""):
    env = {k: v for k, v in os.environ.items() if not k.startswith("LOOP_")}
    env.update({"LOOP_PROJECT": str(root), "HOME": str(home)})
    try:   # a payload names the session's working directory, as the harness's does: the data hooks do not act without one
        d = json.loads(stdin or "{}")
        if isinstance(d, dict) and "cwd" not in d:
            stdin = json.dumps({**d, "cwd": str(root)})
    except ValueError:
        pass
    return subprocess.run([sys.executable, "-I", str(BIN_LOOP), *args], input=stdin, capture_output=True, text=True,
                          env=env, cwd=str(root), timeout=300)


def _cfg(root, **values):
    (root / "loop.json").write_text(json.dumps(values), encoding="utf-8")


def _settings(home):
    return json.loads((home / ".claude" / "settings.json").read_text(encoding="utf-8"))


def _commands(settings):
    return [h["command"] for groups in settings["hooks"].values() for g in groups for h in g["hooks"]]


# install: the ported properties of the source's installer, and the ones the new registration adds

def test_install_keeps_other_keys_and_a_second_run_changes_nothing(project, trials, capsys):
    root, home = project
    f = home / ".claude" / "settings.json"
    f.parent.mkdir()
    f.write_text(json.dumps({"permissions": {"allow": ["Agent"]}, "autoMode": {"allow": ["$defaults"]}}), encoding="utf-8")
    assert hook.main(["install"]) == 0                       # no flag: the user settings
    got = _settings(home)
    assert got["permissions"] == {"allow": ["Agent"]} and got["autoMode"] == {"allow": ["$defaults"]}
    cmds = _commands(got)
    assert cmds and all(str(root) in c and str(BIN_LOOP) in c for c in cmds)
    text = f.read_text(encoding="utf-8")
    assert "__ROOT__" not in text and "__GUARDS__" not in text   # no placeholder survives an install
    first = f.read_bytes()
    capsys.readouterr()
    assert hook.main(["install"]) == 0
    assert "already in" in capsys.readouterr().err and f.read_bytes() == first


def test_dry_run_writes_nothing_and_a_broken_file_is_left_alone(project, trials, capsys):
    _, home = project
    f = home / ".claude" / "settings.json"
    assert hook.main(["install", "--dry-run"]) == 0
    assert "Stop" in json.loads(capsys.readouterr().out)["hooks"] and not f.exists()
    f.parent.mkdir()
    f.write_text("{not json", encoding="utf-8")
    assert hook.main(["install"]) == 1
    assert f.read_text(encoding="utf-8") == "{not json"


def test_other_hooks_stay_and_an_earlier_copy_of_ours_is_replaced_not_doubled(project, trials, capsys):
    root, home = project
    earlier_clone = root.parent / "earlier-clone"
    mine = {"hooks": [{"type": "command", "command": "echo mine"}]}
    earlier = {"hooks": [{"type": "command",
                          "command": f"LOOP_PROJECT={root} python3 -I {earlier_clone}/bin/loop hook stop",   # this project's hooks, from an earlier clone of the kit
                          "timeout": 30}]}
    f = home / ".claude" / "settings.json"
    f.parent.mkdir()
    f.write_text(json.dumps({"hooks": {"Stop": [mine, earlier], "SessionStart": [mine]}}), encoding="utf-8")
    assert hook.main(["install"]) == 0
    got = _settings(home)
    stop = [h["command"] for g in got["hooks"]["Stop"] for h in g["hooks"]]
    ours = [c for c in stop if c != "echo mine"]
    assert "echo mine" in stop and len(ours) == 1 and str(BIN_LOOP) in ours[0]
    assert str(earlier_clone) not in " ".join(stop)
    assert got["hooks"]["SessionStart"] == [mine]
    assert "2 other hook(s) kept" in capsys.readouterr().err
    first = f.read_bytes()
    assert hook.main(["install"]) == 0
    assert f.read_bytes() == first


def test_registered_commands_carry_the_project_root_and_this_bin_loop(project, trials):
    root, home = project
    assert hook.main(["install", "--user"]) == 0
    got = _settings(home)
    assert set(got["hooks"]) == {"UserPromptSubmit", "PostToolUse", "Stop", "PreCompact"}   # PreToolUse waits for its verb
    assert got["hooks"]["PostToolUse"][0]["matcher"] == "*"
    cmds = _commands(got)
    assert all(f"LOOP_PROJECT={root}" in c and f"python3 -I {BIN_LOOP} " in c and "CLAUDE_PROJECT_DIR" not in c for c in cmds)
    assert {c.split(f"python3 -I {BIN_LOOP} ", 1)[1] for c in cmds} == {"hook prompt", "hook post", "hook stop", "hook compact"}


def test_install_leaves_out_a_verb_that_is_not_in_the_kit_with_a_note(project, trials, capsys):
    _, home = project
    assert hook.main(["install", "--user"]) == 0
    assert "`guard pre` left out" in capsys.readouterr().err
    assert "PreToolUse" not in _settings(home)["hooks"]


def test_install_project_writes_into_the_project_root(project, trials):
    root, home = project
    assert hook.main(["install", "--project"]) == 0
    assert (root / ".claude" / "settings.json").is_file() and not (home / ".claude").exists()


def test_install_refuses_a_command_that_fails_on_a_sample_payload(project, capsys, monkeypatch):
    root, home = project
    # a trial starts the command and runs none of its steps, so a failing blocker no longer fails it: the failure is the command's own
    monkeypatch.setattr(hook, "_trial", lambda cmd: subprocess.CompletedProcess(cmd, 1 if " hook stop" in cmd else 0, "", "boom"))
    assert hook.main(["install", "--user"]) == 1
    assert "refused" in capsys.readouterr().err
    assert not (home / ".claude" / "settings.json").exists()


# the hooks themselves, run as a session runs them: one process per event

def test_prompt_prints_the_principal_method_and_says_so_when_it_is_missing(project):
    root, home = project
    method = root / "PRINCIPAL-METHOD.md"
    method.write_text("METHOD TEXT\n", encoding="utf-8")
    r = _run(["hook", "prompt"], root, home)
    assert r.returncode == 0 and r.stdout.startswith("METHOD TEXT\n") and "no backup remote is named" in r.stdout   # this project names no remote, and the prompt says so
    method.unlink()
    r = _run(["hook", "prompt"], root, home)
    assert r.returncode == 0 and r.stdout.strip() == "[loop] no backup remote is named (loop.json: backup.remote): nothing of this session is kept outside this machine" and "no principal method" in r.stderr


def test_post_prints_only_on_the_nth_call_and_the_count_survives_a_new_process(project):
    root, home = project
    _cfg(root, reread_every=3)
    (root / "PRINCIPAL-METHOD.md").write_text("METHOD TEXT", encoding="utf-8")
    outs = [_run(["hook", "post"], root, home, stdin='{"tool_name": "x"}').stdout for _ in range(6)]
    assert [bool(o) for o in outs] == [False, False, True, False, False, True]
    ctx = json.loads(outs[2])["hookSpecificOutput"]["additionalContext"]
    assert ctx.startswith("(tool call 3; every 3)") and ctx.endswith("METHOD TEXT")
    assert json.loads(outs[5])["hookSpecificOutput"]["additionalContext"].startswith("(tool call 6; every 3)")
    assert json.loads((root / ".loop" / "post-count.json").read_text(encoding="utf-8")) == {"count": 6}
    r = _run(["hook", "post"], root, home, stdin="{broken")
    assert r.returncode == 0 and r.stdout == ""


def test_stop_runs_its_steps_and_is_not_blocked_by_their_failure(project):
    root, home = project
    _cfg(root, stop_runs=[["false"], ["touch", "ran.marker"]], stop_blocks_on=[])
    r = _run(["hook", "stop"], root, home, stdin="{}")
    assert r.returncode == 0
    assert (root / "ran.marker").exists()
    assert "false" in r.stderr


def test_stop_refuses_a_failing_blocker_exactly_stop_cap_times_then_lets_through_and_rearms(project):
    root, home = project
    state = root / ".loop" / "stop-refusals.json"
    _cfg(root, stop_runs=[], stop_blocks_on=[["false"]], stop_cap=3)
    rs = [_run(["hook", "stop"], root, home, stdin="{}") for _ in range(5)]
    assert [r.returncode for r in rs] == [2, 2, 2, 0, 0]
    assert "refusal 1 of 3" in rs[0].stderr and "refusal 3 of 3" in rs[2].stderr
    assert json.loads(state.read_text(encoding="utf-8")) == {"refused": 3, "open": True}
    _cfg(root, stop_runs=[], stop_blocks_on=[["true"]], stop_cap=3)          # one pass in which nothing fails
    r = _run(["hook", "stop"], root, home, stdin="{}")
    assert r.returncode == 0 and json.loads(state.read_text(encoding="utf-8")) == {"refused": 0, "open": False}
    _cfg(root, stop_runs=[], stop_blocks_on=[["false"]], stop_cap=3)         # armed again
    r = _run(["hook", "stop"], root, home, stdin="{}")
    assert r.returncode == 2 and "refusal 1 of 3" in r.stderr


def test_a_blocker_that_cannot_run_counts_as_failing(project):
    root, home = project
    _cfg(root, stop_runs=[], stop_blocks_on=[["no-such-program-for-this-test"]])
    r = _run(["hook", "stop"], root, home, stdin="{}")
    assert r.returncode == 2 and "did not run" in r.stderr and "refusal 1 of 3" in r.stderr


def test_a_hook_step_inside_stop_is_refused_rather_than_run_again(project):
    root, home = project
    _cfg(root, stop_runs=[["hook", "stop"]], stop_blocks_on=[])
    r = _run(["hook", "stop"], root, home, stdin="{}")
    assert r.returncode == 0 and "not a step" in r.stderr


@pytest.mark.parametrize("text", ["{not json", json.dumps({"bnak": 1})])
def test_a_broken_loop_json_does_not_make_stop_exit_other_than_zero(project, text):
    root, home = project
    (root / "loop.json").write_text(text, encoding="utf-8")
    r = _run(["hook", "stop"], root, home, stdin="{}")
    assert r.returncode == 0 and r.stderr.strip()


def test_compact_exits_zero_whatever_its_steps_do(project):
    root, home = project
    assert _run(["hook", "compact"], root, home, stdin="{}").returncode == 0


def test_no_subcommand_is_an_argument_error():
    assert hook.main([]) == 2


def test_a_second_projects_install_leaves_the_first_projects_hooks_in_place(project, trials, monkeypatch, tmp_path):
    """Each project's hooks serve its own sessions: installing the loop for a second project keeps the first one's entries,
    and a repeat of either install changes nothing."""
    root, home = project
    assert hook.main(["install"]) == 0
    first = _commands(_settings(home))
    other = tmp_path / "second-project"
    other.mkdir()
    (other / "loop.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("LOOP_PROJECT", str(other))
    assert hook.main(["install"]) == 0
    after = _commands(_settings(home))
    assert first and all(c in after for c in first) and len(after) == 2 * len(first)
    assert sum(str(other) in c for c in after) == len(first)
    assert hook.main(["install"]) == 0 and sorted(_commands(_settings(home))) == sorted(after)


def test_a_hook_whose_kit_is_gone_does_nothing_and_the_prompt_says_so(project):
    """A missing script would exit 2, which blocks a tool call or a stop. The installed command tests for the kit first: with
    the kit gone it exits 0 with nothing said, except at the prompt, where the session is told that the loop is off."""
    root, home = project
    gone = root.parent / "kit-that-was-moved" / "bin" / "loop"
    for argv in (["hook", "stop"], ["hook", "post"], ["hook", "compact"], ["guard", "pre"]):
        r = subprocess.run(hook.command_for(root, gone, argv), shell=True, input="{}", capture_output=True, text=True)
        assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), argv
    r = subprocess.run(hook.command_for(root, gone, ["hook", "prompt"]), shell=True, input="{}", capture_output=True, text=True)
    assert r.returncode == 0 and "the kit at" in r.stdout and "is gone" in r.stdout
    (root / "PRINCIPAL-METHOD.md").write_text("METHOD TEXT\n", encoding="utf-8")   # and with the kit in place the same command runs it
    r = subprocess.run(hook.command_for(root, BIN_LOOP, ["hook", "prompt"]), shell=True, input=json.dumps({"cwd": str(root)}),
                       capture_output=True, text=True, env={**os.environ, "HOME": str(home)})
    assert r.returncode == 0 and r.stdout.startswith("METHOD TEXT\n") and "is gone" not in r.stdout
