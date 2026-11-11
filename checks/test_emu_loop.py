"""checks/emu_loop.py is a stub since 2026-11-10: loop/watch.py replaced the module. These tests pin what the stub may still do:
every invocation exits 0 and says the loop moved, a post-edit call is answered in additionalContext, a stop is never blocked, and
nothing is read, written or registered. docs/EMU-LOOP-RETIRED.md maps each of the 29 tests the module had to its replacement.

    python3 -m pytest -q checks/test_emu_loop.py
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
STUB = ROOT / "checks" / "emu_loop.py"
MSG = "emu_loop is retired: run python3 -I bin/loop hook install (loop/README.md)"
INVOCATIONS = [[], ["arm", "--watch", "x/*.jsx"], ["arm", "--watch", "x", "--no-smoke"], ["disarm"], ["status"],
               ["eval", "x.jsx", "--chain", "c.json"], ["install"], ["install", "--user"], ["install", "--shared", "--user"],
               ["hook", "stop"], ["hook", "bogus"], ["--help"], ["hook", "post-edit", "--anything"]]


def run(tmp_path, *args, stdin="{}"):
    env = {**os.environ, "HOME": str(tmp_path / "home"), "EMU_LOOP_DIR": str(tmp_path / "state")}
    return subprocess.run([sys.executable, str(STUB), *args], input=stdin, capture_output=True, text=True, env=env,
                          cwd=str(tmp_path), timeout=60)


@pytest.mark.parametrize("args", INVOCATIONS, ids=lambda a: " ".join(a) or "no-arguments")
def test_every_invocation_exits_0_and_says_the_loop_moved(tmp_path, args):
    r = run(tmp_path, *args)
    assert r.returncode == 0, (r.returncode, r.stderr)
    assert MSG in r.stdout, r.stdout


def test_a_post_edit_call_answers_in_additional_context(tmp_path):
    r = run(tmp_path, "hook", "post-edit", stdin=json.dumps({"session_id": "s", "tool_name": "Edit"}))
    assert r.returncode == 0 and r.stderr == ""
    assert json.loads(r.stdout) == {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": MSG}}


def test_a_stop_is_said_on_stdout_and_never_blocked(tmp_path):
    r = run(tmp_path, "hook", "stop")
    assert r.returncode == 0 and r.stdout == MSG + "\n" and r.stderr == ""


def test_nothing_is_read_written_or_registered(tmp_path):
    for args in (["install", "--user"], ["arm", "--watch", "x"], ["disarm"], ["hook", "post-edit"], ["hook", "stop"]):
        assert run(tmp_path, *args).returncode == 0
    assert sorted(os.listdir(tmp_path)) == []


def test_the_stub_is_at_most_30_lines_and_has_no_file_code():
    src = STUB.read_text(encoding="utf-8")
    assert len(src.splitlines()) <= 30, len(src.splitlines())
    assert "open(" not in src and ".write" not in src
