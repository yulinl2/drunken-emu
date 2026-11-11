"""The exit codes of the hook commands that install registers and of the entry point, seen the way a session sees them.

Among the commands that hook install registers, exit 2 means one thing: this session is told no. It comes out of a Stop's refusal, and out of a
guard that did not run: a guard call whose kit call exits 64 (its verb unknown to the kit, or its arguments refused) exits 2 with one line of the
wrapper's own, and a guard call whose kit call exits with another code, other than 0, 2 and 64, exits 2 when the guard's failure rule
(cli.GUARD_FAILURE_RULE) denies it, judged by a stdlib-only check the command carries, and keeps the kit's own exit otherwise. bin/loop exits 64,
not 2, for an unknown verb; the verb hook, and guard pre and guard permissions, exit 64, not 2, for a usage error; record, gate, tick, keep, watch,
revisit and guard verdict keep the exit codes they had. The shell command that hook.command_for writes puts one line of its own on standard error
(a line that starts with "[loop] ") whenever it changes an exit: a prompt, post or compact whose kit call fails exits 0; a stop whose kit call exits 2
exits 2, and any other failure of it exits 0; every other exit of a guard call, and all its output, are the kit's own.
The tests named s1_ to s9_ pin these numbered sentences, for guard pre:
  s1  when the kit call exits with a code other than 0, 2 and 64, a call the failure rule names is blocked: exit 2, empty standard output, and one
      line of the wrapper's own that starts with "[loop] guard pre exited N", N being the kit's exit.
  s2  a call the rule does not name keeps the kit's exit and output, with no line of the wrapper's own.
  s3  only tool_name and tool_input.command are read.
  s4  the check imports nothing of the kit: it gives the same answers with the kit's loop/ folder absent.
  s5  when the check cannot run (no python3 on PATH), the kit's exit stays and one line of the wrapper's own says that the call was not checked.
  s6  when the kit call exits 0 or 2, the command's exit and output are the kit's own, byte for byte; an exit 64 still becomes exit 2 with one line.
  s7  the check gives the answer that guard.pre's failure branch gives, over one table of payloads.
  s8  the payload reaches the kit unchanged (a 2 MB payload, and one with text outside ASCII) and is judged as without the wrapper.
  s9  install runs the kit's own call of guard pre on its sample payload: any exit but 0 and 3 refuses the install, and exit 3 leaves the verb out.
The stop test pins the Stop's clause: any other failure of its kit call exits 0 with one line of the wrapper's own, and exit 2 stays exit 2.
Each test runs the shell command that hook.command_for writes (or the entry point itself) on a payload, as a session does. A kit that a test
renames or breaks is a copy in a temporary folder, a stub kit is a one-file program in a temporary folder, and no test changes the kit. Every test
runs with a temporary HOME."""
import ast, hashlib, io, json, os, pathlib, shutil, signal, subprocess, sys

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import guard, hook  # noqa: E402

BIN_LOOP = KIT / "bin" / "loop"
HOOKS = [["hook", "prompt"], ["hook", "post"], ["hook", "compact"]]


@pytest.fixture
def project(tmp_path):
    """A temporary project (its loop.json names it) and a temporary HOME."""
    root, home = (tmp_path / "project").resolve(), (tmp_path / "home").resolve()
    root.mkdir()
    home.mkdir()
    (root / "loop.json").write_text("{}", encoding="utf-8")
    return root, home


def _env(root, home):
    env = {k: v for k, v in os.environ.items() if not k.startswith("LOOP_")}
    return {**env, "HOME": str(home), "LOOP_PROJECT": str(root)}


def _kit_copy(tmp_path, rename=(), replace=None, skip=()):
    """A copy of the kit in a temporary folder, returned as its bin/loop. `rename` pairs a verb of the copy's VERBS table with a new
    name, so that the verb is unknown there; `replace` maps a path under the package to its new text; `skip` names modules left out."""
    dst = tmp_path / "kit"
    shutil.copytree(KIT / "loop", dst / "loop", ignore=shutil.ignore_patterns("__pycache__", "tests"))
    (dst / "bin").mkdir()
    shutil.copy2(BIN_LOOP, dst / "bin" / "loop")
    cli = dst / "loop" / "cli.py"
    text = cli.read_text(encoding="utf-8")
    for verb, new in rename:
        needle = f'    "{verb}": '
        assert text.count(needle) == 1, needle
        text = text.replace(needle, f'    "{new}": ')
    cli.write_text(text, encoding="utf-8")
    for path, body in (replace or {}).items():
        (dst / path).write_text(body, encoding="utf-8")
    for name in skip:
        os.remove(dst / "loop" / name)
    return dst / "bin" / "loop"


def _stub_kit(tmp_path, code):
    """A stand-in for bin/loop, returned as a path: whatever it is asked, it writes one line of its own on standard error and exits with `code`."""
    stub = tmp_path / "stub-kit" / "bin" / "loop"
    stub.parent.mkdir(parents=True)
    stub.write_text("import sys\nsys.stderr.write('stub kit line\\n')\nsys.exit(%d)\n" % code, encoding="utf-8")
    return stub


def _hook_run(cmd, payload, root, home):
    """One hook command, run by the shell with the payload on standard input, as a session runs it."""
    return subprocess.run(cmd, shell=True, input=json.dumps(payload), capture_output=True, text=True,
                          env=_env(root, home), cwd=str(root), timeout=120)


def _kit_run(bin_loop, args, root, home):
    """The entry point itself, run with the arguments and an empty standard input."""
    return subprocess.run([sys.executable, "-I", str(bin_loop), *args], capture_output=True, text=True, input="",
                          env=_env(root, home), cwd=str(root), timeout=120)


def _wrapper_lines(stderr):
    """The lines the hook wrapper writes on standard error: they start with "[loop] ". A line of the kit's own does not."""
    return [line for line in stderr.splitlines() if line.startswith("[loop] ")]


def _force_push(root):
    """The payload of a call that the guard denies: a forced push."""
    return {"tool_name": "Bash", "tool_input": {"command": "git push -f origin x"}, "cwd": str(root)}


def _bash(command):
    """A Bash call of one command."""
    return {"tool_name": "Bash", "tool_input": {"command": command, "description": "d"}}


DENIED = {  # the calls the failure rule names: each of the four tools, and a command with each of push, merge, api and repo edit
    "mcp-merge_pull_request": {"tool_name": "mcp__github__merge_pull_request", "tool_input": {"owner": "o", "repo": "r", "pullNumber": 1}},
    "mcp-push_files": {"tool_name": "mcp__github__push_files", "tool_input": {"owner": "o", "repo": "r", "branch": "topic"}},
    "mcp-create_or_update_file": {"tool_name": "mcp__github__create_or_update_file", "tool_input": {"owner": "o", "repo": "r", "path": "p"}},
    "mcp-delete_file": {"tool_name": "mcp__github__delete_file", "tool_input": {"owner": "o", "repo": "r", "path": "p"}},
    "command-push": _bash("git push -f origin x"),
    "command-merge": _bash("git merge topic"),
    "command-api": _bash("gh api repos/o/r"),
    "command-repo-edit": _bash("gh repo edit --visibility public"),
}
PASSED = {  # none of them
    "read": {"tool_name": "Read", "tool_input": {"file_path": "/x/README.md"}},
    "edit": {"tool_name": "Edit", "tool_input": {"file_path": "/x/a.py", "old_string": "a", "new_string": "b"}},
    "bash-ls": _bash("ls -la"),
}
SAYS_THE_WORDS = {  # the words are in these calls, and the rule does not read them: only tool_name and tool_input.command are read
    "edit-text": {"tool_name": "Edit", "tool_input": {"file_path": "/x/notes.md", "old_string": "a",
                  "new_string": "git push -f origin x; merge_pull_request; gh api; gh repo edit"}},
    "write-text": {"tool_name": "Write", "tool_input": {"file_path": "/x/merge_pull_request.txt", "content": "push merge api"}},
    "mcp-description": {"tool_name": "mcp__github__get_file_contents", "tool_input": {"owner": "o", "repo": "r", "path": "p", "description": "git push merge api"}},
    "bash-cwd-and-transcript": {"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": "/x/push-merge-api",
                                "transcript_path": "/y/mcp__github__merge_pull_request.jsonl"},
}


def _guard_pre(kit, payload, root, home):
    """The registered guard command of this kit, run on the payload as a session runs it."""
    return _hook_run(hook.command_for(root, kit, ["guard", "pre"]), payload, root, home)


def _direct(kit, argv, payload, root, home):
    """The kit's own call of one verb on the payload, without the wrapper: what the kit says by itself."""
    return _hook_run(hook._kit_call(root, kit, argv), payload, root, home)


def _hook_run_bytes(cmd, data, root, home):
    """One hook command run by the shell with `data` (bytes) on standard input; its standard output and error are bytes."""
    return subprocess.run(cmd, shell=True, input=data, capture_output=True, env=_env(root, home), cwd=str(root), timeout=120)


def _digest_kit(tmp_path, code):
    """A stand-in for bin/loop that writes the sha256 and the length of its standard input on standard error, and exits with `code`."""
    stub = tmp_path / "digest-kit" / "bin" / "loop"
    stub.parent.mkdir(parents=True)
    stub.write_text("import hashlib, sys\n"
                    "data = sys.stdin.buffer.read()\n"
                    "sys.stderr.write('stub digest ' + hashlib.sha256(data).hexdigest() + ' ' + str(len(data)) + '\\n')\n"
                    f"sys.exit({code})\n", encoding="utf-8")
    return stub


def _broken_kit(tmp_path, variant):
    """A copy of the kit whose guard.py is absent or broken, or whose config.py or cli.py is broken (a syntax error at its end)."""
    if variant == "guard-absent":
        return _kit_copy(tmp_path, skip=["guard.py"])
    if variant == "guard-broken":
        return _kit_copy(tmp_path, replace={"loop/guard.py": "def broken(:\n"})
    module = {"config-broken": "config.py", "cli-broken": "cli.py"}[variant]
    text = (KIT / "loop" / module).read_text(encoding="utf-8")
    return _kit_copy(tmp_path, replace={f"loop/{module}": text + "\ndef broken(:\n"})


def test_a_guard_whose_verb_is_unknown_blocks_with_exit_2(project, tmp_path):
    root, home = project
    kit = _kit_copy(tmp_path, rename=[("guard", "guard-renamed")])
    r = _hook_run(hook.command_for(root, kit, ["guard", "pre"]), _force_push(root), root, home)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert r.stdout == "", r.stdout
    lines = _wrapper_lines(r.stderr)
    assert len(lines) == 1 and lines[0].startswith("[loop] guard pre exited 64"), r.stderr


def test_a_guard_that_refuses_its_own_arguments_blocks_with_exit_2(project, tmp_path):
    root, home = project
    text = (KIT / "loop" / "guard.py").read_text(encoding="utf-8")
    needle = 'sub.add_parser("pre", '
    assert text.count(needle) == 1
    kit = _kit_copy(tmp_path, replace={"loop/guard.py": text.replace(needle, 'sub.add_parser("pre-moved", ', 1)})
    r = _hook_run(hook.command_for(root, kit, ["guard", "pre"]), _force_push(root), root, home)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert r.stdout == "", r.stdout
    lines = _wrapper_lines(r.stderr)
    assert len(lines) == 1 and lines[0].startswith("[loop] guard pre exited 64"), r.stderr


@pytest.mark.parametrize("code, wrapper_lines", [(64, 1), (2, 0)], ids=["64-the-guard-did-not-run", "2-the-kits-own-block"])
def test_a_guard_call_that_exits_64_or_2_blocks_with_exit_2(project, tmp_path, code, wrapper_lines):
    root, home = project
    r = _hook_run(hook.command_for(root, _stub_kit(tmp_path, code), ["guard", "pre"]), _force_push(root), root, home)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "stub kit line" in r.stderr and len(_wrapper_lines(r.stderr)) == wrapper_lines, r.stderr


@pytest.mark.parametrize("argv", HOOKS, ids=["prompt", "post", "compact"])
def test_a_prompt_post_or_compact_whose_verb_is_unknown_exits_0_with_one_wrapper_line(project, tmp_path, argv):
    root, home = project
    kit = _kit_copy(tmp_path, rename=[("hook", "hook-renamed")])
    r = _hook_run(hook.command_for(root, kit, argv), {"cwd": str(root)}, root, home)
    assert r.returncode == 0, (r.returncode, r.stderr)
    lines = _wrapper_lines(r.stderr)
    assert len(lines) == 1 and lines[0].startswith(f"[loop] {' '.join(argv)} exited 64"), r.stderr


@pytest.mark.parametrize("argv", HOOKS, ids=["prompt", "post", "compact"])
@pytest.mark.parametrize("code", [1, 2, 3, 64, 127])
def test_a_prompt_post_or_compact_exits_0_whatever_exit_its_kit_call_has(project, tmp_path, argv, code):
    """Exit 2 of the kit call is no exception here: a prompt, post or compact is never refused."""
    root, home = project
    r = _hook_run(hook.command_for(root, _stub_kit(tmp_path, code), argv), {"cwd": str(root)}, root, home)
    assert r.returncode == 0, (r.returncode, r.stderr)
    lines = r.stderr.splitlines()
    assert len(lines) == 2 and lines[0] == "stub kit line", r.stderr
    assert lines[1].startswith(f"[loop] {' '.join(argv)} exited {code}"), r.stderr


def test_a_stop_whose_verb_is_unknown_exits_0_not_2(project, tmp_path):
    root, home = project
    kit = _kit_copy(tmp_path, rename=[("hook", "hook-renamed")])
    r = _hook_run(hook.command_for(root, kit, ["hook", "stop"]), {"cwd": str(root)}, root, home)
    assert r.returncode == 0, (r.returncode, r.stderr)
    lines = _wrapper_lines(r.stderr)
    assert len(lines) == 1 and lines[0].startswith("[loop] hook stop exited 64"), r.stderr


def test_a_stop_refused_by_its_blocker_still_exits_2_through_the_wrapper(project):
    root, home = project
    (root / "loop.json").write_text(json.dumps({"stop_runs": [], "stop_blocks_on": [["false"]]}), encoding="utf-8")
    r = _hook_run(hook.command_for(root, BIN_LOOP, ["hook", "stop"]), {"cwd": str(root)}, root, home)
    assert r.returncode == 2 and "refusal 1 of 3" in r.stderr, (r.returncode, r.stderr)


def test_an_unknown_verb_and_the_usage_errors_of_hook_and_guard_exit_64(project):
    root, home = project
    assert hook.main([]) == 64
    assert hook.main(["install", "--user", "--project"]) == 64
    assert guard.main(["permissions", "apply"]) == 64
    for args in (["nosuch"], ["guard", "permissions", "apply"]):
        r = _kit_run(BIN_LOOP, args, root, home)
        assert r.returncode == 64, (args, r.stderr)


@pytest.mark.parametrize("args", [["help"], ["hook", "--help"], ["guard", "pre", "--help"]],
                         ids=["help", "hook-help", "guard-pre-help"])
def test_a_request_for_help_exits_0(project, args):
    root, home = project
    r = _kit_run(BIN_LOOP, args, root, home)
    assert r.returncode == 0, (args, r.stderr)


def test_guard_verdict_keeps_the_exit_2_of_its_own_usage(project):
    root, home = project
    r = _kit_run(BIN_LOOP, ["guard", "verdict"], root, home)
    assert r.returncode == 2, (r.returncode, r.stderr)


def test_a_guard_deny_is_a_json_answer_with_exit_0_through_the_wrapper(project):
    root, home = project
    r = _hook_run(hook.command_for(root, BIN_LOOP, ["guard", "pre"]), _force_push(root), root, home)
    assert r.returncode == 0, (r.returncode, r.stderr)
    assert json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny", r.stdout


def test_install_refuses_when_a_registered_hook_fails_on_its_sample_payload(project, tmp_path):
    """install runs each registered call once on a sample payload and refuses the install when one fails. The call it runs is the
    kit's own, not the wrapper that turns a failure of a hook into exit 0."""
    root, home = project
    text = (KIT / "loop" / "hook.py").read_text(encoding="utf-8")
    needle = "def cmd_post(args):\n"
    assert text.count(needle) == 1
    kit = _kit_copy(tmp_path, replace={"loop/hook.py": text.replace(needle, needle + '    raise RuntimeError("a broken post")\n', 1)})
    r = _kit_run(kit, ["hook", "install", "--user", "--dry-run"], root, home)
    assert r.returncode == 1 and "`hook post` exited 1 on a sample payload" in r.stderr, (r.returncode, r.stderr)
    assert r.stdout == ""


def test_install_leaves_out_a_verb_the_kit_does_not_have_yet(project, tmp_path):
    root, home = project
    kit = _kit_copy(tmp_path, skip=["guard.py"])
    r = _kit_run(kit, ["hook", "install", "--user", "--dry-run"], root, home)
    assert r.returncode == 0, (r.returncode, r.stderr)
    assert "`guard pre` left out" in r.stderr
    assert "PreToolUse" not in json.loads(r.stdout)["hooks"]


# The tests named s1_ to s9_ pin the numbered sentences of the module docstring; the stop test pins the Stop's clause.

@pytest.mark.parametrize("code", [1, 3, 127], ids=lambda c: f"exit-{c}")
@pytest.mark.parametrize("name", list(DENIED))
def test_s1_guard_pre_blocks_a_call_its_failure_rule_names_when_its_kit_call_exits_1_3_or_127(project, tmp_path, code, name):
    root, home = project
    r = _guard_pre(_stub_kit(tmp_path, code), DENIED[name], root, home)
    assert r.returncode == 2 and r.stdout == "", (r.returncode, r.stdout, r.stderr)
    lines = _wrapper_lines(r.stderr)
    assert "stub kit line" in r.stderr and len(lines) == 1 and lines[0].startswith(f"[loop] guard pre exited {code}"), r.stderr


@pytest.mark.parametrize("variant", ["guard-absent", "guard-broken", "config-broken", "cli-broken"])
def test_s1_guard_pre_blocks_a_forced_push_when_the_kit_copy_does_not_load(project, tmp_path, variant):
    root, home = project
    kit = _broken_kit(tmp_path, variant)
    direct = _direct(kit, ["guard", "pre"], _force_push(root), root, home)
    assert direct.returncode not in (0, 2, 64), (direct.returncode, direct.stderr)
    r = _guard_pre(kit, _force_push(root), root, home)
    assert r.returncode == 2 and r.stdout == "", (r.returncode, r.stdout, r.stderr)
    lines = _wrapper_lines(r.stderr)
    assert len(lines) == 1 and lines[0].startswith(f"[loop] guard pre exited {direct.returncode}"), r.stderr


@pytest.mark.parametrize("code", [1, 3, 127], ids=lambda c: f"exit-{c}")
@pytest.mark.parametrize("name", list(PASSED))
def test_s2_guard_pre_keeps_the_kit_exit_and_output_for_a_call_its_failure_rule_does_not_name(project, tmp_path, code, name):
    root, home = project
    r = _guard_pre(_stub_kit(tmp_path, code), PASSED[name], root, home)
    assert (r.returncode, r.stdout, r.stderr) == (code, "", "stub kit line\n"), r.stderr


@pytest.mark.parametrize("loop_json", ['{"nosuchkey": 1}', "{"], ids=["unknown-key", "not-json"])
def test_s2_a_guard_that_cannot_check_keeps_its_exit_1_for_a_read_an_edit_and_a_bash_ls_and_its_deny_for_a_forced_push(project, loop_json):
    root, home = project
    (root / "loop.json").write_text(loop_json, encoding="utf-8")
    for name, payload in PASSED.items():
        direct = _direct(BIN_LOOP, ["guard", "pre"], payload, root, home)
        r = _guard_pre(BIN_LOOP, payload, root, home)
        assert direct.returncode == 1, (name, direct.returncode, direct.stderr)
        assert (r.returncode, r.stdout, r.stderr) == (direct.returncode, direct.stdout, direct.stderr), (name, r.stderr)
    direct = _direct(BIN_LOOP, ["guard", "pre"], _force_push(root), root, home)
    r = _guard_pre(BIN_LOOP, _force_push(root), root, home)
    assert (r.returncode, r.stdout, r.stderr) == (direct.returncode, direct.stdout, direct.stderr), r.stderr
    assert json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny", r.stdout


def test_s2_a_kit_that_exits_before_reading_a_large_payload_adds_no_line_of_its_own_to_the_output(project, tmp_path):
    root, home = project
    payload = {"tool_name": "Write", "tool_input": {"file_path": "/x/big.txt", "content": "x" * 2_000_000}}
    r = subprocess.run(hook.command_for(root, _stub_kit(tmp_path, 1), ["guard", "pre"]), shell=True, input=json.dumps(payload).encode("utf-8"),
                       capture_output=True, env=_env(root, home), cwd=str(root), timeout=120,
                       preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_IGN))   # a write to a closed pipe is then an error the shell may print
    assert (r.returncode, r.stdout, r.stderr) == (1, b"", b"stub kit line\n"), r.stderr


@pytest.mark.parametrize("code", [1, 3, 127], ids=lambda c: f"exit-{c}")
@pytest.mark.parametrize("name", list(SAYS_THE_WORDS))
def test_s3_only_tool_name_and_tool_input_command_are_read_so_a_call_that_only_says_the_words_is_not_blocked(project, tmp_path, code, name):
    root, home = project
    r = _guard_pre(_stub_kit(tmp_path, code), SAYS_THE_WORDS[name], root, home)
    assert (r.returncode, r.stdout, r.stderr) == (code, "", "stub kit line\n"), r.stderr


@pytest.mark.parametrize("name", list(DENIED) + list(PASSED))
def test_s4_the_check_gives_the_same_answers_with_no_loop_folder_beside_the_kit(project, tmp_path, name):
    root, home = project
    stub = _stub_kit(tmp_path, 1)
    assert not (stub.parents[1] / "loop").exists()
    r = _guard_pre(stub, {**DENIED, **PASSED}[name], root, home)
    if name in DENIED:
        assert r.returncode == 2 and len(_wrapper_lines(r.stderr)) == 1, (r.returncode, r.stderr)
    else:
        assert (r.returncode, _wrapper_lines(r.stderr)) == (1, []), (r.returncode, r.stderr)


def test_s4_the_check_gives_the_same_answers_when_the_loop_folder_of_the_kit_is_gone(project, tmp_path):
    root, home = project
    kit = tmp_path / "kit" / "bin" / "loop"
    kit.parent.mkdir(parents=True)
    shutil.copy2(BIN_LOOP, kit)
    direct = _direct(kit, ["guard", "pre"], PASSED["read"], root, home)
    assert direct.returncode not in (0, 2, 64), (direct.returncode, direct.stderr)
    r = _guard_pre(kit, _force_push(root), root, home)
    assert r.returncode == 2 and len(_wrapper_lines(r.stderr)) == 1, (r.returncode, r.stderr)
    r = _guard_pre(kit, PASSED["read"], root, home)
    assert (r.returncode, r.stdout, r.stderr) == (direct.returncode, direct.stdout, direct.stderr), r.stderr


def test_s4_the_check_imports_only_json_re_and_sys():
    imported = set()
    for node in ast.walk(ast.parse(hook._guard_check())):
        if isinstance(node, ast.Import):
            imported |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert imported == {"json", "re", "sys"}, imported


@pytest.mark.parametrize("name", ["read", "command-push"])
def test_s5_without_python3_on_path_the_kit_exit_stays_and_one_line_says_the_call_was_not_checked(project, tmp_path, name):
    root, home = project
    nopy = tmp_path / "nopy"
    nopy.mkdir()
    os.symlink(shutil.which("cat"), nopy / "cat")
    env = {**_env(root, home), "PATH": str(nopy)}
    r = subprocess.run(hook.command_for(root, BIN_LOOP, ["guard", "pre"]), shell=True, input=json.dumps({**DENIED, **PASSED}[name]),
                       capture_output=True, text=True, env=env, cwd=str(root), timeout=120)
    assert r.returncode == 127, (r.returncode, r.stderr)
    lines = _wrapper_lines(r.stderr)
    assert len(lines) == 1 and lines[0].startswith("[loop] guard pre exited 127") and "not checked" in lines[0], r.stderr


@pytest.mark.parametrize("code, wrapper_lines", [(2, 0), (64, 1)], ids=["exit-2-the-kits-own", "exit-64-the-guard-did-not-run"])
def test_s6_a_kit_exit_2_is_its_own_and_an_exit_64_still_becomes_exit_2_with_one_line(project, tmp_path, code, wrapper_lines):
    root, home = project
    r = _guard_pre(_stub_kit(tmp_path, code), _force_push(root), root, home)
    assert r.returncode == 2 and r.stdout == "", (r.returncode, r.stdout, r.stderr)
    assert "stub kit line\n" in r.stderr and len(_wrapper_lines(r.stderr)) == wrapper_lines, r.stderr


def test_s6_a_deny_is_the_kits_own_json_with_exit_0_byte_for_byte(project):
    root, home = project
    direct = _direct(BIN_LOOP, ["guard", "pre"], _force_push(root), root, home)
    r = _guard_pre(BIN_LOOP, _force_push(root), root, home)
    assert direct.returncode == 0 and json.loads(direct.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny", direct.stdout
    assert (r.returncode, r.stdout, r.stderr) == (direct.returncode, direct.stdout, direct.stderr), r.stderr


def test_s6_an_artifact_delete_is_the_kits_own_ask_with_exit_0_byte_for_byte(project):
    root, home = project
    payload = {"tool_name": "Artifact", "tool_input": {"action": "delete", "url": "u"}}
    direct = _direct(BIN_LOOP, ["guard", "pre"], payload, root, home)
    r = _guard_pre(BIN_LOOP, payload, root, home)
    assert direct.returncode == 0 and json.loads(direct.stdout)["hookSpecificOutput"]["permissionDecision"] == "ask", direct.stdout
    assert (r.returncode, r.stdout, r.stderr) == (direct.returncode, direct.stdout, direct.stderr), r.stderr


def test_s6_a_call_that_passes_prints_nothing_and_exits_0(project):
    root, home = project
    r = _guard_pre(BIN_LOOP, PASSED["read"], root, home)
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), (r.returncode, r.stdout, r.stderr)


@pytest.mark.parametrize("name", list(DENIED) + list(PASSED))
def test_s7_the_check_answers_as_the_failure_branch_of_guard_pre_answers_over_one_table(project, tmp_path, monkeypatch, capsys, name):
    root, home = project
    payload = {**DENIED, **PASSED}[name]

    def failing_judge(*args, **kwargs):
        raise RuntimeError("a failure of the judge")

    monkeypatch.setattr(guard, "judge", failing_judge)
    guard.pre(io.StringIO(json.dumps(payload)))
    guard_denies = '"deny"' in capsys.readouterr().out
    r = _guard_pre(_stub_kit(tmp_path, 1), payload, root, home)
    assert guard_denies == (r.returncode == 2) == (name in DENIED), (name, guard_denies, r.returncode, r.stderr)


def test_s8_a_2_mb_payload_is_judged_as_without_the_wrapper(project):
    root, home = project
    data = json.dumps({"tool_name": "Write", "tool_input": {"file_path": "/x/big.txt", "content": "x" * 2_000_000 + " git push -f origin y"}}).encode("utf-8")
    direct = _hook_run_bytes(hook._kit_call(root, BIN_LOOP, ["guard", "pre"]), data, root, home)
    r = _hook_run_bytes(hook.command_for(root, BIN_LOOP, ["guard", "pre"]), data, root, home)
    assert direct.returncode == 0 and direct.stdout == b"", direct.stderr[:200]
    assert (r.returncode, r.stdout, r.stderr) == (direct.returncode, direct.stdout, direct.stderr), r.stderr[:200]


def test_s8_a_2_mb_payload_is_read_whole_by_the_check(project, tmp_path):
    root, home = project
    data = json.dumps({"tool_name": "Bash", "tool_input": {"command": "x" * 2_000_000 + "; git push -f origin y"}}).encode("utf-8")
    r = _hook_run_bytes(hook.command_for(root, _stub_kit(tmp_path, 1), ["guard", "pre"]), data, root, home)
    err = r.stderr.decode("utf-8")
    assert r.returncode == 2 and r.stdout == b"" and len(_wrapper_lines(err)) == 1 and "stub kit line\n" in err, err[:200]


def test_s8_a_2_mb_payload_reaches_the_kit_unchanged(project, tmp_path):
    root, home = project
    data = json.dumps({"tool_name": "Write", "tool_input": {"file_path": "/x/big.txt", "content": "x" * 2_000_000}}).encode("utf-8")
    r = _hook_run_bytes(hook.command_for(root, _digest_kit(tmp_path, 1), ["guard", "pre"]), data, root, home)
    err = r.stderr.decode("utf-8")
    assert r.returncode == 1 and f"stub digest {hashlib.sha256(data).hexdigest()} {len(data)}\n" in err and _wrapper_lines(err) == [], err[:200]


def test_s8_a_payload_with_text_outside_ascii_reaches_the_kit_unchanged_and_is_judged_as_without_the_wrapper(project, tmp_path):
    root, home = project
    payload = {"tool_name": "Bash", "tool_input": {"command": "git push -f origin x", "description": "".join([chr(252), "nic", chr(248), "de ", chr(0x6f22), chr(0x5b57)])}}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    assert not data.isascii()
    seen = _hook_run_bytes(hook.command_for(root, _digest_kit(tmp_path, 1), ["guard", "pre"]), data, root, home)
    assert f"stub digest {hashlib.sha256(data).hexdigest()} {len(data)}\n" in seen.stderr.decode("utf-8"), seen.stderr[:200]
    direct = _hook_run_bytes(hook._kit_call(root, BIN_LOOP, ["guard", "pre"]), data, root, home)
    r = _hook_run_bytes(hook.command_for(root, BIN_LOOP, ["guard", "pre"]), data, root, home)
    assert direct.returncode == 0 and b'"deny"' in direct.stdout, direct.stderr[:200]
    assert (r.returncode, r.stdout, r.stderr) == (direct.returncode, direct.stdout, direct.stderr), r.stderr[:200]


@pytest.mark.parametrize("variant, code", [("guard-broken", 1), ("guard-returns-2", 2), ("verb-renamed", 64)],
                         ids=["guard-broken", "guard-returns-2", "verb-renamed"])
def test_s9_install_refuses_when_the_trial_of_guard_pre_exits_1_2_or_64(project, tmp_path, variant, code):
    root, home = project
    text = (KIT / "loop" / "guard.py").read_text(encoding="utf-8")
    if variant == "guard-broken":
        kit = _kit_copy(tmp_path, replace={"loop/guard.py": "def broken(:\n"})
    elif variant == "guard-returns-2":
        needle = '    if args.cmd == "pre":\n'
        assert text.count(needle) == 1
        kit = _kit_copy(tmp_path, replace={"loop/guard.py": text.replace(needle, needle + "        return 2\n", 1)})
    else:
        kit = _kit_copy(tmp_path, rename=[("guard", "guard-renamed")])
    r = _kit_run(kit, ["hook", "install", "--user", "--dry-run"], root, home)
    assert r.returncode == 1 and f"`guard pre` exited {code} on a sample payload" in r.stderr, (r.returncode, r.stderr)
    assert r.stdout == ""


def test_s9_install_leaves_out_the_guard_pre_whose_trial_exits_3(project, tmp_path):
    root, home = project
    kit = _kit_copy(tmp_path, skip=["guard.py"])
    r = _kit_run(kit, ["hook", "install", "--user", "--dry-run"], root, home)
    assert r.returncode == 0 and "`guard pre` left out" in r.stderr, (r.returncode, r.stderr)


@pytest.mark.parametrize("code, wrapper_lines", [(1, 1), (3, 1), (64, 1), (127, 1), (2, 0)],
                         ids=["exit-1", "exit-3", "exit-64", "exit-127", "exit-2-the-refusal"])
def test_a_stop_whose_kit_call_fails_exits_0_with_one_line_of_the_wrapper_except_its_refusal_2(project, tmp_path, code, wrapper_lines):
    root, home = project
    r = _hook_run(hook.command_for(root, _stub_kit(tmp_path, code), ["hook", "stop"]), {"cwd": str(root)}, root, home)
    assert r.returncode == (2 if code == 2 else 0), (r.returncode, r.stderr)
    assert r.stderr.splitlines()[0] == "stub kit line", r.stderr
    lines = _wrapper_lines(r.stderr)
    assert len(lines) == wrapper_lines and all(line.startswith(f"[loop] hook stop exited {code}") for line in lines), r.stderr
