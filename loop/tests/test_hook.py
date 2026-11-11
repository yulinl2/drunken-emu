"""loop/hook.py: the hooks a session fires, the install that registers them, and the stop that is refused a capped number of times.

Every test runs in temporary folders with a temporary HOME; none reads or writes the settings of the machine it runs on."""
import json, os, pathlib, subprocess, sys, threading, time

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


def _run(args, root, home, stdin="", budget=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("LOOP_")}
    env.update({"LOOP_PROJECT": str(root), "HOME": str(home)})
    if budget is not None:   # every event's time budget, in seconds (loop/hook.py): a test makes a check outlast it
        env["LOOP_HOOK_BUDGET_S"] = str(budget)
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
    assert {c.split(f"python3 -I {BIN_LOOP} ", 1)[1].split(" || ", 1)[0] for c in cmds} == {"hook prompt", "hook post", "hook stop", "hook compact"}   # the verb and its arguments end where the wrapper starts: at " || "


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


def test_install_refuses_user_and_project_together(project, trials, capsys):
    root, home = project
    assert hook.main(["install", "--user", "--project"]) == 64        # argparse's usage error: nothing is written anywhere
    assert not (home / ".claude").exists() and not (root / ".claude").exists()


def test_a_user_install_writes_nothing_under_the_project_root(project, trials):
    root, home = project
    (root / ".git" / "info").mkdir(parents=True)
    (root / ".git" / "info" / "exclude").write_text("# exclude\n", encoding="utf-8")   # a clone's exclude file: left as it was
    before = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert hook.main(["install"]) == 0                              # the default: the user settings
    after = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert after == before and (home / ".claude" / "settings.json").is_file()


def test_install_keeps_a_command_that_shares_a_group_with_ours_and_the_group_matcher(project, trials):
    root, home = project
    shared = {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo mine"},
                                           {"type": "command", "command": f"LOOP_PROJECT={root} python3 -I {BIN_LOOP} hook stop", "timeout": 30}]}
    f = home / ".claude" / "settings.json"
    f.parent.mkdir()
    f.write_text(json.dumps({"hooks": {"Stop": [shared]}}), encoding="utf-8")
    assert hook.main(["install"]) == 0
    groups = _settings(home)["hooks"]["Stop"]
    kept = [g for g in groups if any(h["command"] == "echo mine" for h in g["hooks"])]
    assert len(kept) == 1 and kept[0]["matcher"] == "Bash" and [h["command"] for h in kept[0]["hooks"]] == ["echo mine"]
    assert sum(str(BIN_LOOP) in h["command"] for g in groups for h in g["hooks"]) == 1


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
    assert hook.main([]) == 64


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


# the stop's count under stop.lock, the post counter, what a failed blocker says, and the entries an install recognises

def test_two_stops_at_once_both_count_their_refusal(project, monkeypatch):
    """The read, the verdict and the write of a stop are one step under stop.lock: two stops that overlap count two refusals."""
    root, _home = project
    cfg = config.load()
    res = {"failed": ["false"], "did_not_run": [], "passed": [], "said": [("false", "exit 1: ")]}
    read = hook._stop_state

    def slow(path):
        st = read(path)
        time.sleep(0.2)
        return st

    monkeypatch.setattr(hook, "_stop_state", slow)
    stops = [threading.Thread(target=hook._decide, args=(cfg, res)) for _ in range(2)]
    for t in stops:
        t.start()
    for t in stops:
        t.join()
    assert json.loads((root / ".loop" / "stop-refusals.json").read_text(encoding="utf-8")) == {"refused": 2, "open": False}


def test_a_stop_that_finds_stop_lock_held_says_so_and_does_not_hang(project, monkeypatch, capsys):
    import fcntl
    root, _home = project
    cfg = config.load()
    monkeypatch.setattr(hook, "STOP_LOCK_WAIT_S", 0.3, raising=False)
    res = {"failed": ["false"], "did_not_run": [], "passed": [], "said": [("false", "exit 1: ")]}
    with open(cfg.state("stop.lock"), "w") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        t0 = time.monotonic()
        assert hook._decide(cfg, res) == 2
        assert time.monotonic() - t0 < 2
    assert "stop.lock is still held after 0.3 s" in capsys.readouterr().err


def test_the_post_counter_counts_eight_calls_that_arrive_at_once(project, monkeypatch):
    root, _home = project
    _cfg(root, reread_every=1000)
    monkeypatch.setattr(hook, "_payload", lambda: {"cwd": str(root)})
    read = hook._count

    def slow(path):
        n = read(path)
        time.sleep(0.05)
        return n

    monkeypatch.setattr(hook, "_count", slow)
    together = threading.Barrier(8)

    def call():
        together.wait()
        hook.cmd_post(None)

    calls = [threading.Thread(target=call) for _ in range(8)]
    for t in calls:
        t.start()
    for t in calls:
        t.join()
    assert json.loads((root / ".loop" / "post-count.json").read_text(encoding="utf-8")) == {"count": 8}


def test_a_state_file_is_replaced_in_one_step_not_written_in_place(tmp_path):
    f = tmp_path / "state.json"
    hook._write_json(f, {"count": 1})
    before = f.stat().st_ino
    hook._write_json(f, {"count": 2})
    assert json.loads(f.read_text(encoding="utf-8")) == {"count": 2} and f.stat().st_ino != before


def test_a_failed_blocker_says_the_marker_it_printed(project):
    root, home = project
    _cfg(root, stop_runs=[], stop_blocks_on=[["sh", "-c", "echo KETTLE-$((4000 + 1583)); exit 1"]])   # the marker is made by the shell
    r = _run(["hook", "stop"], root, home, stdin="{}")
    assert r.returncode == 2 and "KETTLE-5583" in r.stderr


def test_a_failed_blocker_says_the_last_20_lines_it_printed(project):
    root, home = project
    script = "i=1; while [ $i -le 30 ]; do echo row-$i; i=$((i+1)); done; exit 1"
    _cfg(root, stop_runs=[], stop_blocks_on=[["sh", "-c", script]])
    r = _run(["hook", "stop"], root, home, stdin="{}")
    assert r.returncode == 2 and "    row-30\n" in r.stderr and "    row-11\n" in r.stderr and "    row-10\n" not in r.stderr


def test_a_failed_blocker_says_at_most_2000_characters_of_its_output(project):
    root, home = project
    _cfg(root, stop_runs=[], stop_blocks_on=[["sh", "-c", "printf '%5000s' '' | tr ' ' A; exit 1"]])
    r = _run(["hook", "stop"], root, home, stdin="{}")
    assert r.returncode == 2 and "A" * 2000 in r.stderr and "A" * 2001 not in r.stderr


def test_a_blocker_that_cannot_run_says_why(project):
    root, home = project
    _cfg(root, stop_runs=[], stop_blocks_on=[["no-such-program-for-this-test"]])
    r = _run(["hook", "stop"], root, home, stdin="{}")
    assert r.returncode == 2 and "did not run" in r.stderr and "could not start" in r.stderr


# item 3: one time budget per hook event, ending before the timeout install writes; what runs past it is reported as out of time

SLEEPER = 'import json, time\ntime.sleep(5)\nprint(json.dumps({"vector": {"errors": 0}, "layers": {"stub": "go"}}))\n'


def _watched_sleeper(root):
    """A project whose one check sleeps five seconds on every file, and then passes."""
    (root / "sleeper.py").write_text(SLEEPER, encoding="utf-8")
    _cfg(root, reread_every=1000, stop_runs=[], stop_cap=2,
         watch=[{"name": "slow", "files": ["*.txt"], "run": ["python3", "-I", "sleeper.py", "{path}"]}])


def test_every_hook_event_has_a_budget_that_ends_before_its_installed_timeout():
    registered = {event for event, _argv, _matcher in hook.REGISTERED}
    assert registered <= set(hook.HOOK_TIME), registered - set(hook.HOOK_TIME)
    for event, (budget_s, timeout_s) in hook.HOOK_TIME.items():
        assert 0 < budget_s < timeout_s, (event, budget_s, timeout_s)


def test_install_writes_each_registered_command_the_timeout_of_its_event(project, trials):
    _root, home = project
    assert hook.main(["install", "--user"]) == 0
    got = _settings(home)
    assert set(got["hooks"]) == {"UserPromptSubmit", "PostToolUse", "Stop", "PreCompact"}
    for event, groups in got["hooks"].items():
        timeouts = [h.get("timeout") for g in groups for h in g["hooks"]]
        assert timeouts == [hook.HOOK_TIME[event][1]] * len(timeouts), (event, timeouts)


def test_a_check_that_outlasts_the_budget_is_out_of_time_for_each_file_and_the_post_returns_inside_it(project):
    root, home = project
    _watched_sleeper(root)
    (root / "app.txt").write_text("x\n", encoding="utf-8")
    (root / "other.txt").write_text("y\n", encoding="utf-8")
    t0 = time.monotonic()
    r = _run(["hook", "post"], root, home, stdin='{"tool_name": "Edit"}', budget=1)
    elapsed = time.monotonic() - t0
    assert r.returncode == 0 and elapsed < 4, (elapsed, r.stderr)
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    assert ctx.count("not evaluated (out of time)") == 2, ctx        # the file whose check was running, and the one not yet judged
    assert "refusal" not in r.stderr                                  # at a post it is a plain report, not a refusal


def test_a_stop_whose_check_outlasts_the_budget_is_refused_as_out_of_time(project):
    root, home = project
    _watched_sleeper(root)
    (root / "app.txt").write_text("x\n", encoding="utf-8")
    t0 = time.monotonic()
    r = _run(["hook", "stop"], root, home, stdin="{}", budget=1)
    elapsed = time.monotonic() - t0
    assert r.returncode == 2 and elapsed < 4, (elapsed, r.stderr)
    assert "refusal 1 of 2" in r.stderr and "did not run: watch slow app.txt" in r.stderr and "out of time" in r.stderr, r.stderr


def test_a_stop_step_that_outlasts_the_budget_is_refused_as_out_of_time(project):
    root, home = project
    _cfg(root, stop_runs=[], stop_blocks_on=[["sh", "-c", "sleep 8"]], stop_cap=2)
    t0 = time.monotonic()
    r = _run(["hook", "stop"], root, home, stdin="{}", budget=1)
    elapsed = time.monotonic() - t0
    assert r.returncode == 2 and elapsed < 6, (elapsed, r.stderr)
    assert "refusal 1 of 2" in r.stderr and "out of time" in r.stderr, r.stderr


def test_the_budget_override_can_not_outlast_the_timeout_it_is_under(monkeypatch):
    monkeypatch.setenv("LOOP_HOOK_BUDGET_S", "100000")
    for event, (_budget_s, timeout_s) in hook.HOOK_TIME.items():
        assert hook.budget(event) < timeout_s, event


def test_a_second_clone_replaces_the_entries_of_a_first_whose_path_has_a_space(project, trials, monkeypatch, tmp_path):
    root, home = project
    first, second = tmp_path / "first clone", tmp_path / "second-clone"
    monkeypatch.setattr(config, "KIT", first)
    assert hook.main(["install", "--user"]) == 0
    monkeypatch.setattr(config, "KIT", second)
    assert hook.main(["install", "--user"]) == 0
    got = _settings(home)
    assert str(first) not in json.dumps(got)
    for event, groups in got["hooks"].items():
        cmds = [h["command"] for g in groups for h in g["hooks"]]
        assert len(cmds) == 1 and str(second / "bin" / "loop") in cmds[0], (event, cmds)


# the queued words: every tool call shows the principal's messages still waiting in its transcript, once per session

T = "2026-01-01T00:01:00Z"


def _transcript(root, name, rows):
    """A transcript beside the project. Its first eight characters name the session, as the file names of transcripts do."""
    path = root.parent / "transcripts" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def _queue(content, ts=T):
    return {"type": "queue-operation", "operation": "enqueue", "timestamp": ts, "content": content}


def _post(root, home, transcript=None):
    payload = {"tool_name": "Bash"}
    if transcript is not None:
        payload["transcript_path"] = str(transcript)
    return _run(["hook", "post"], root, home, stdin=json.dumps(payload))


def _block(text, line=1, at=T):
    return (f"[loop] typed by the principal at {at}, not delivered yet (queue row {line}); the engine will deliver it again "
            f"when the turn ends, and it is one message:\n{text}")


def _context(r):
    return json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"] if r.stdout.strip() else ""


def test_a_waiting_queued_message_is_shown_once_over_two_tool_calls(project):
    root, home = project
    t = _transcript(root, "aaaaaaaa-1.jsonl", [_queue("please also check the margins")])
    first, second = _post(root, home, t), _post(root, home, t)
    assert (first.returncode, second.returncode) == (0, 0)
    assert _context(first) == _block("please also check the margins")
    assert second.stdout == ""


def test_after_the_delivery_row_the_next_tool_call_shows_nothing(project):
    root, home = project
    t = _transcript(root, "aaaaaaaa-1.jsonl", [_queue("please also check the margins")])
    assert _context(_post(root, home, t)) == _block("please also check the margins")
    delivered = {"type": "user", "uuid": "u9", "timestamp": "2026-01-01T00:02:00Z",
                 "message": {"role": "user", "content": "please also check the margins"}}
    with t.open("a", encoding="utf-8") as f:
        f.write(json.dumps(delivered) + "\n")
    r = _post(root, home, t)
    assert r.returncode == 0 and r.stdout == ""


def test_an_unparsable_line_is_skipped_and_the_hook_exits_as_on_success(project):
    root, home = project
    t = _transcript(root, "aaaaaaaa-1.jsonl", [])
    t.write_text('{"type": "queue-operation", "operation":\n' + json.dumps(_queue("still reached")) + "\n", encoding="utf-8")
    r = _post(root, home, t)
    assert r.returncode == 0 and _context(r) == _block("still reached", line=2) and "not read" not in r.stderr


def test_a_payload_without_a_transcript_path_says_in_one_line_that_the_queue_was_not_read(project):
    root, home = project
    r = _post(root, home)
    assert r.returncode == 0 and r.stdout == ""
    assert r.stderr.count("\n") == 1 and "the queue was not read" in r.stderr and "transcript_path" in r.stderr


def test_a_transcript_path_that_cannot_be_read_is_said_in_one_line(project):
    root, home = project
    unreadable = root.parent / "transcripts" / "aaaaaaaa-1.jsonl"
    unreadable.mkdir(parents=True)                       # a directory where the transcript should be
    r = _post(root, home, unreadable)
    assert r.returncode == 0 and r.stdout == "" and r.stderr.count("\n") == 1 and "the queue was not read" in r.stderr


def test_a_state_file_that_is_not_valid_is_said_in_one_line_shows_nothing_and_is_kept(project):
    root, home = project
    t = _transcript(root, "aaaaaaaa-1.jsonl", [_queue("a waiting message")])
    (root / ".loop").mkdir(exist_ok=True)
    bad = root / ".loop" / "queued-aaaaaaaa.json"
    bad.write_text("{broken", encoding="utf-8")
    r = _post(root, home, t)
    assert r.returncode == 0 and r.stdout == "" and r.stderr.count("\n") == 1 and "the queue was not read" in r.stderr
    assert bad.read_text(encoding="utf-8") == "{broken"


def test_each_session_is_shown_its_own_waiting_message(project):
    root, home = project
    a = _transcript(root, "aaaaaaaa-1.jsonl", [_queue("the same words")])
    b = _transcript(root, "bbbbbbbb-1.jsonl", [_queue("the same words")])
    assert _context(_post(root, home, a)) == _block("the same words")
    assert _context(_post(root, home, b)) == _block("the same words")
    assert _post(root, home, a).stdout == "" and _post(root, home, b).stdout == ""


def test_the_message_is_shown_whole_under_its_header(project):
    root, home = project
    text = 'Line one, with "quotes" and ' + chr(252) + 'nic' + chr(248) + 'de.\n' + "a long clause, " * 250 + "\nEND"
    t = _transcript(root, "aaaaaaaa-1.jsonl", [_queue(text)])
    assert _context(_post(root, home, t)) == _block(text)


def test_a_queued_row_without_a_timestamp_is_shown_as_at_an_unknown_time(project):
    root, home = project
    row = {"type": "queue-operation", "operation": "enqueue", "content": "no time on this one"}
    t = _transcript(root, "aaaaaaaa-1.jsonl", [row])
    assert _context(_post(root, home, t)) == _block("no time on this one", at="an unknown time")


def test_the_queued_words_join_the_reprint_in_the_same_context(project):
    root, home = project
    _cfg(root, reread_every=1)
    (root / "PRINCIPAL-METHOD.md").write_text("METHOD TEXT", encoding="utf-8")
    t = _transcript(root, "aaaaaaaa-1.jsonl", [_queue("a queued message")])
    reprint = "(tool call 1; every 1) Check yourself against the principal's method once more:\n\nMETHOD TEXT"
    assert _context(_post(root, home, t)) == reprint + "\n\n" + _block("a queued message")
