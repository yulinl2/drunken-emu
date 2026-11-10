"""loop/watch.py: a changed watched file is judged by its check. The verdict reaches the session's context after the tool
call that changed the file, and a stop is refused while the newest verdict of a watched file fails, could not be made,
or is dominated.

Every test runs in a temporary project. Its check is a stub (STUB below) that reads the watched file: BROKEN makes it
fail, UNABLE makes it exit 3 (a layer could not run), LOAD=<n> sets its load, SLEEP makes it outlast the time limit.
The hooks are called in-process with the payload the harness sends; the entry bin/loop is run in test_closed_loop.py.
Every value here is invented, and no test reads or writes the settings of the machine it runs on."""
import io, json, os, pathlib, sys

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import config, hook, watch  # noqa: E402

STUB = '''import json, re, sys, time
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8")
if "UNABLE" in text:
    print("the stub cannot run here")
    sys.exit(3)
if "SLEEP" in text:
    time.sleep(5)
strict = Path("policy.txt").is_file() and "strict" in Path("policy.txt").read_text(encoding="utf-8")
errors = text.count("BROKEN") + (text.count("TODO") if strict else 0) + ("--fail" in sys.argv[2:])
found = re.search(r"LOAD=([0-9.]+)", text)
load = float(found.group(1)) if found else 1.0
print("checked " + sys.argv[1])
print(json.dumps({"vector": {"errors": errors, "load": load}, "layers": {"stub": "fail" if errors else "go"}}))
sys.exit(1 if errors else 0)
'''
RUN = ["python3", "-I", "check.py", "{path}"]
WATCH = [{"name": "stub", "files": ["app.txt"], "run": RUN}]
BASE = {"reread_every": 1000, "stop_runs": [], "stop_cap": 2}


def setcfg(root, **values):
    (root / "loop.json").write_text(json.dumps({**BASE, **values}), encoding="utf-8")


@pytest.fixture
def proj(tmp_path, monkeypatch):
    root = (tmp_path / "project").resolve()
    root.mkdir()
    for name in [k for k in os.environ if k.startswith("LOOP_")]:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LOOP_PROJECT", str(root))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (root / "check.py").write_text(STUB, encoding="utf-8")
    setcfg(root, watch=WATCH)
    return root


def put(root, text, name="app.txt"):
    (root / name).write_text(text, encoding="utf-8")


def hook_run(monkeypatch, capsys, root, which, **payload):
    """One hook, in-process, with the payload the harness sends for an event in this project: (exit code, stdout, stderr)."""
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(root), **payload})))
    rc = hook.main([which])
    out, err = capsys.readouterr()
    return rc, out, err


def context(out):
    return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out.strip() else ""


def ledger(root):
    path = root / ".loop" / "watch.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []


def test_dominates():
    assert watch.dominates({"a": 1, "b": 1}, {"a": 2, "b": 1})
    assert not watch.dominates({"a": 1, "b": 2}, {"a": 2, "b": 1})   # a trade-off is not a regression
    assert not watch.dominates({"a": 1}, {"a": 1})                   # equal is not better
    assert not watch.dominates({"a": 1}, {"b": 0})                   # nothing in common, nothing to compare


def test_inert_with_an_empty_list(proj, monkeypatch, capsys):
    setcfg(proj, watch=[])
    put(proj, "BROKEN\n")
    assert hook_run(monkeypatch, capsys, proj, "post", tool_name="Edit")[:2] == (0, "")
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0
    assert watch.main(["eval"]) == 0 and watch.main(["status"]) == 0
    assert not (proj / ".loop" / "watch.jsonl").exists() and not (proj / ".loop" / "cand").exists()


def test_a_trial_judges_nothing(proj, monkeypatch, capsys):
    put(proj, "BROKEN\n")
    assert hook_run(monkeypatch, capsys, proj, "post", loop_trial=True)[:2] == (0, "")
    assert hook_run(monkeypatch, capsys, proj, "stop", loop_trial=True)[0] == 0
    assert not (proj / ".loop" / "watch.jsonl").exists()


def test_post_feeds_back_goes_quiet_on_unchanged_bytes_and_sees_an_improvement(proj, monkeypatch, capsys):
    put(proj, "BROKEN\n")
    rc, out, _ = hook_run(monkeypatch, capsys, proj, "post", tool_name="Edit")
    ctx = context(out)
    assert rc == 0 and out.count("\n") == 1, out                     # one JSON object, one line
    assert "FAIL" in ctx and "app.txt" in ctx and "stub" in ctx and "errors=1" in ctx
    assert hook_run(monkeypatch, capsys, proj, "post")[1] == ""      # the same bytes: nothing said
    put(proj, "LOAD=0.5\n")                                          # better on every axis
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "PASS" in ctx and "improved" in ctx


def test_one_output_carries_the_reprint_and_the_verdict(proj, monkeypatch, capsys):
    setcfg(proj, reread_every=1, watch=WATCH)
    (proj / "PRINCIPAL-METHOD.md").write_text("Evidence before judgements.\n", encoding="utf-8")
    put(proj, "BROKEN\n")
    rc, out, _ = hook_run(monkeypatch, capsys, proj, "post")
    ctx = context(out)
    assert rc == 0 and out.count("\n") == 1
    assert "Evidence before judgements." in ctx and "FAIL" in ctx


def test_a_stop_is_refused_until_the_cap_then_released(proj, monkeypatch, capsys):
    put(proj, "BROKEN\n")                                            # stop_cap is 2
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 2 and "refusal 1 of 2" in err and "watch stub app.txt" in err and "FAIL" in err
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 2
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 0 and "the cap of 2 refusals is reached" in err
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0       # open until one pass


def test_a_stop_judges_a_file_changed_with_no_post_event(proj, monkeypatch, capsys):
    put(proj, "BROKEN\n")
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 2
    put(proj, "LOAD=1\n")                                            # fixed, and no tool call said so either
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0


def test_a_stop_allows_a_passing_candidate(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 0 and "refusal" not in err
    assert ledger(proj)[-1]["gate"] == "pass"


def test_a_dominated_candidate_blocks_the_stop(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    hook_run(monkeypatch, capsys, proj, "post")                      # candidate A: passes at load 1
    put(proj, "LOAD=2\n")                                            # candidate B: passes, at a higher load
    assert "REGRESSION" in context(hook_run(monkeypatch, capsys, proj, "post")[1])
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 2 and "REGRESSION" in err


def test_a_check_that_cannot_run_is_not_a_pass(proj, monkeypatch, capsys):
    put(proj, "UNABLE\n")                                            # the stub exits 3: a layer could not run
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "NOT EVALUATED" in ctx and "cannot run here" in ctx
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 2 and "did not run" in err


def test_a_check_past_the_time_limit_is_not_a_pass(proj, monkeypatch, capsys):
    monkeypatch.setattr(hook, "STEP_TIMEOUT_S", 1)
    put(proj, "SLEEP\n")
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "NOT EVALUATED" in ctx and "no result within 1 s" in ctx
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 2


def test_a_named_file_that_does_not_exist_is_not_evaluated(proj, monkeypatch, capsys):
    setcfg(proj, watch=[{"name": "stub", "files": ["gone.txt"], "run": RUN}])
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "NOT EVALUATED" in ctx and "gone.txt" in ctx
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 2 and "did not run" in err


EDITING = '''import json, sys
from pathlib import Path
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
if "EDIT-DURING" in text:                                            # the file changes under the check, as an editor's save would
    path.write_text(text.replace("EDIT-DURING", "EDITED"), encoding="utf-8")
print(json.dumps({"vector": {"errors": 0}, "layers": {"stub": "go"}}))
'''


def test_a_file_that_changes_while_its_check_runs_gets_no_verdict_for_the_old_bytes(proj, monkeypatch, capsys):
    (proj / "edit_check.py").write_text(EDITING, encoding="utf-8")
    setcfg(proj, watch=[{"name": "edit", "files": ["app.txt"], "run": ["python3", "-I", "edit_check.py", "{path}"]}])
    put(proj, "EDIT-DURING\n")
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "NOT EVALUATED" in ctx and "changed while its check ran" in ctx
    rec = ledger(proj)[-1]
    assert rec["gate"] == "not_evaluated" and rec["vector"] == {}   # the pass the check printed belongs to bytes that are gone
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")        # the stop judges the bytes that are there now, and they pass
    assert rc == 0 and ledger(proj)[-1]["gate"] == "pass" and ledger(proj)[-1]["sha"] != rec["sha"], err


def test_a_refused_stop_does_not_quote_a_refusal_count_that_is_one_behind(proj, monkeypatch, capsys):
    put(proj, "BROKEN\n")
    hook_run(monkeypatch, capsys, proj, "post")
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 2 and "refusal 1 of 2" in err and "stop refusals used" not in err   # the header counts it; a block made before it must not


def test_the_ledger_is_append_only_and_each_record_supersedes_the_last(proj, monkeypatch, capsys):
    put(proj, "BROKEN\n")
    hook_run(monkeypatch, capsys, proj, "post")
    first = (proj / ".loop" / "watch.jsonl").read_bytes()
    put(proj, "LOAD=0.5\n")
    hook_run(monkeypatch, capsys, proj, "post")
    second = (proj / ".loop" / "watch.jsonl").read_bytes()
    assert second.startswith(first) and len(second) > len(first)
    recs = ledger(proj)
    assert len(recs) == 2 and recs[1]["supersedes"] == recs[0]["id"]
    assert recs[1]["config"] == recs[0]["config"] and recs[0]["sha"] != recs[1]["sha"]
    assert (proj / recs[0]["snapshot"]).is_file()                    # the judged bytes are kept by hash
    fields = {"at", "id", "check", "path", "sha", "config", "gate", "vector", "layers", "tail", "trigger", "supersedes",
              "dominated_by", "snapshot"}
    assert fields <= set(recs[0]), sorted(fields - set(recs[0]))


def test_a_broken_hook_fails_open_and_says_so(proj, monkeypatch, capsys):
    (proj / ".loop").mkdir()
    (proj / ".loop" / "watch.jsonl").write_text("this is not a record\n", encoding="utf-8")
    put(proj, "BROKEN\n")
    rc, _, err = hook_run(monkeypatch, capsys, proj, "post")
    assert rc == 0 and "fails open" in err
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 0 and "fails open" in err


def test_a_watched_file_that_disappears_is_not_a_pass(proj, monkeypatch, capsys):
    setcfg(proj, watch=[{"name": "stub", "files": ["*.txt"], "run": RUN}])
    put(proj, "LOAD=1\n")
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0      # control: present and passing
    (proj / "app.txt").unlink()                                      # deleted, or renamed away
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 2 and "gone" in err and "NOT EVALUATED" in err and "cp .loop/cand/" in err


def test_a_verdict_is_reused_only_under_the_same_command(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0      # passes under the command as it stands
    setcfg(proj, watch=[{"name": "stub", "files": ["app.txt"], "run": RUN + ["--fail"]}])   # same bytes, other command
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 2 and "FAIL" in err
    assert len({r["config"] for r in ledger(proj)}) == 2


def test_a_pass_under_another_command_is_no_baseline(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    hook_run(monkeypatch, capsys, proj, "post")                      # passes under the first command, at load 1
    setcfg(proj, watch=[{"name": "stub", "files": ["app.txt"], "run": RUN + ["--other"]}])
    put(proj, "LOAD=2\n")                                            # a new candidate: passes at a higher load
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "PASS" in ctx and "REGRESSION" not in ctx
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0


def test_a_pass_that_a_later_verdict_replaced_is_no_baseline(proj, monkeypatch, capsys):
    put(proj, "LOAD=1 TODO\n")                                       # a TODO counts only under the strict policy
    hook_run(monkeypatch, capsys, proj, "post")                      # candidate A passes at load 1
    (proj / "policy.txt").write_text("strict\n", encoding="utf-8")   # the checker changes: the same bytes now fail
    assert watch.main(["eval", "app.txt"]) == 1                      # re-evaluated now: A's newest verdict is a fail
    capsys.readouterr()                                              # the eval's printout is not the hook's output
    put(proj, "LOAD=2\n")                                            # candidate B passes at load 2
    assert "REGRESSION" not in context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0


def test_the_feedback_counts_stop_refusals_not_evaluations(proj, monkeypatch, capsys):
    for i in range(3):                                               # three edits, no stop between them
        put(proj, f"BROKEN {i}\n")
        ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "evaluation 3 of this file" in ctx and "stop refusals used 0/2" in ctx and "3/2" not in ctx


def test_the_restore_hint_names_only_a_copy_that_exists_and_holds_the_candidate(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    hook_run(monkeypatch, capsys, proj, "post")                      # A passes at load 1; its copy is kept
    put(proj, "LOAD=2\n")                                            # B is dominated by A
    snap = [r for r in ledger(proj) if r["gate"] == "pass"][0]["snapshot"]
    assert f"cp {snap} app.txt" in watch_eval_out(proj, capsys)
    (proj / snap).write_text("LOAD=9\n", encoding="utf-8")           # the copy no longer holds A
    assert f"cp {snap}" not in watch_eval_out(proj, capsys)
    (proj / snap).unlink()                                           # and now it does not exist
    out = watch_eval_out(proj, capsys)
    assert "REGRESSION" in out and f"cp {snap}" not in out


def watch_eval_out(proj, capsys):
    """`watch eval` (forced) of the watched file, printed: the stdout it wrote."""
    watch.main(["eval", "app.txt"])
    return capsys.readouterr().out


def test_a_file_over_4_MiB_is_judged_and_not_copied(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n" + "x" * (4 << 20))
    hook_run(monkeypatch, capsys, proj, "post")
    rec = ledger(proj)[-1]
    assert rec["gate"] == "pass" and rec["snapshot"] is None
    assert not list((proj / ".loop").glob("cand/*"))


def test_eval_exit_codes_and_status_writes_nothing(proj, capsys):
    put(proj, "LOAD=1\n")
    assert watch.main(["eval"]) == 0
    put(proj, "BROKEN\n")
    assert watch.main(["eval"]) == 1
    put(proj, "UNABLE\n")
    assert watch.main(["eval"]) == 3
    capsys.readouterr()
    before = sorted(str(p) for p in proj.rglob("*"))
    assert watch.main(["status"]) == 0
    assert sorted(str(p) for p in proj.rglob("*")) == before        # status writes nothing
    out = capsys.readouterr().out
    assert "NOT EVALUATED" in out and "watch stub app.txt" in out
    assert watch.main(["eval", "nosuch.txt"]) == 2                   # a path that is not watched


def test_an_unknown_key_inside_a_watch_entry_is_refused(proj):
    setcfg(proj, watch=[{"name": "stub", "files": ["app.txt"], "run": RUN, "extra": 1}])
    with pytest.raises(SystemExit) as e:
        config.load()
    assert "'extra'" in str(e.value) and "'run'" in str(e.value)    # the message names it and the known keys


@pytest.mark.parametrize("entry", [
    {"name": "stub", "files": ["app.txt"]},                         # no run
    {"name": "", "files": ["app.txt"], "run": RUN},                  # an empty name
    {"name": "stub", "files": "app.txt", "run": RUN},                # files is not a list
    {"name": "stub", "files": ["app.txt"], "run": []},               # nothing to run
])
def test_a_malformed_watch_entry_is_refused(proj, entry):
    setcfg(proj, watch=[entry])
    with pytest.raises(SystemExit):
        config.load()


def test_a_name_used_by_two_entries_is_refused(proj):
    setcfg(proj, watch=WATCH + [{"name": "stub", "files": ["other.txt"], "run": RUN}])
    with pytest.raises(SystemExit):
        config.load()
