"""loop/watch.py: a changed watched file is judged by its check. The verdict reaches the session's context after the tool
call that changed the file, and a stop is refused while the newest verdict of a watched file fails, could not be made,
or is dominated.

Every test runs in a temporary project. Its check is a stub (STUB below) that reads the watched file: BROKEN makes it
fail, UNABLE makes it exit 3 (a layer could not run), LOAD=<n> sets its load, SLEEP makes it outlast the time limit.
The hooks are called in-process with the payload the harness sends; the entry bin/loop is run in test_closed_loop.py.
Every value here is invented, and no test reads or writes the settings of the machine it runs on."""
import hashlib, io, json, os, pathlib, re, sys, time

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import config, hook, watch  # noqa: E402
from loop.adapters import emu

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


INPUT_EDITING = '''import json
from pathlib import Path
rules = Path("policy") / "rules.txt"
rules.write_text(rules.read_text(encoding="utf-8") + "x\\n", encoding="utf-8")   # the input changes under the check
print(json.dumps({"vector": {"errors": 0}, "layers": {"stub": "go"}}))
'''
QUIET_CHECK = '''import json
print(json.dumps({"vector": {"errors": 0}, "layers": {"stub": "go"}}))
'''


def test_an_input_that_changes_while_its_check_runs_gets_no_verdict_for_the_old_inputs(proj, monkeypatch, capsys):
    setcfg(proj, watch=[{"name": "edit", "files": ["app.txt"], "inputs": ["policy/*.txt"],
                         "run": ["python3", "-I", "edit_check.py", "{path}"]}])
    (proj / "policy").mkdir()
    (proj / "policy" / "rules.txt").write_text("v1\n", encoding="utf-8")
    (proj / "edit_check.py").write_text(INPUT_EDITING, encoding="utf-8")   # the input changes under the check, on every run
    put(proj, "LOAD=1\n")                                                  # the watched file's bytes do not change
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "NOT EVALUATED" in ctx and "an input changed while its check ran" in ctx
    rec = ledger(proj)[-1]
    assert rec["gate"] == "not_evaluated" and rec["vector"] == {}          # the pass the check printed is for inputs that are gone
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")               # the check changes the input again: the stop is refused
    assert rc == 2 and "refusal 1 of 2" in err and "did not run" in err, err
    assert ledger(proj)[-1]["gate"] == "not_evaluated"
    (proj / "edit_check.py").write_text(QUIET_CHECK, encoding="utf-8")     # a check that exits 0 and changes nothing
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")               # the file is judged again, on the inputs on disk now
    on_disk = hashlib.sha256((proj / "policy" / "rules.txt").read_bytes()).hexdigest()
    assert rc == 0 and ledger(proj)[-1]["gate"] == "pass" and ledger(proj)[-1]["inputs"] == [["policy/rules.txt", on_disk]], err


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


def test_a_judge_that_breaks_fails_open_and_says_so(proj, monkeypatch, capsys):
    put(proj, "BROKEN\n")

    def broken(*args, **kwargs):
        raise RuntimeError("the judge broke")

    monkeypatch.setattr(watch, "evaluate", broken)
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


# item 1: inputs. A verdict is for the watched file's bytes and the bytes of its inputs; a ledger from before inputs still covers its candidates.

INPUT_WATCH = [{"name": "stub", "files": ["app.txt"], "run": RUN, "inputs": ["policy/*.txt"]}]


def records(root, folder=".loop"):
    """The ledger's lines that are records (a JSON object with check, path and gate). A test writes torn lines on purpose, and ledger()
    stops at the first one; this one reads past them."""
    path = root / folder / "watch.jsonl"
    out = []
    for line in path.read_bytes().split(b"\n") if path.exists() else []:
        try:
            obj = json.loads(line.decode("utf-8")) if line.strip() else None
        except ValueError:
            continue
        if isinstance(obj, dict) and {"check", "path", "gate"} <= set(obj):
            out.append(obj)
    return out


def test_a_changed_input_judges_the_watched_file_again_though_its_bytes_did_not_change(proj, monkeypatch, capsys):
    setcfg(proj, watch=INPUT_WATCH)
    (proj / "policy").mkdir()
    (proj / "policy" / "rules.txt").write_text("v1\n", encoding="utf-8")
    put(proj, "LOAD=1\n")
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0 and len(records(proj)) == 1   # nothing changed: nothing is judged
    (proj / "policy" / "rules.txt").write_text("v2\n", encoding="utf-8")                      # the input changed; app.txt did not
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0
    first, second = records(proj)
    assert first["sha"] == second["sha"] and first["cand"] != second["cand"]
    assert second["inputs"] == [["policy/rules.txt", hashlib.sha256(b"v2\n").hexdigest()]]


def test_an_input_glob_that_matches_nothing_is_said_and_counts_as_a_change(proj, monkeypatch, capsys):
    setcfg(proj, watch=INPUT_WATCH)
    put(proj, "LOAD=1\n")
    assert watch.main(["eval"]) == 0
    assert "watch stub: input glob matches nothing: policy/*.txt" in capsys.readouterr().out
    assert watch.main(["status"]) == 0 and "input glob matches nothing: policy/*.txt" in capsys.readouterr().out
    (proj / "policy").mkdir()
    (proj / "policy" / "rules.txt").write_text("v1\n", encoding="utf-8")                      # it matches now: a change
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0 and len(records(proj)) == 2
    (proj / "policy" / "rules.txt").unlink()                                                  # it matches nothing again: a change
    assert hook_run(monkeypatch, capsys, proj, "stop")[0] == 0 and len(records(proj)) == 3


def test_a_ledger_written_before_inputs_existed_is_not_judged_again_and_says_what_it_does_not_know(proj, monkeypatch, capsys):
    """A record in the form the code before inputs (and before the note of a pass) wrote: the upgrade judges nothing again, and its pass
    says that what it did not run was not recorded."""
    put(proj, "LOAD=1\n")
    old = {"at": "2026-11-09T10:00:00+00:00", "id": "0f1e2d3c", "check": "stub", "path": "app.txt",
           "sha": hashlib.sha256(b"LOAD=1\n").hexdigest(), "config": watch.command_hash(RUN), "gate": "pass",
           "vector": {"errors": 0, "load": 1.0}, "layers": {"stub": "go"}, "tail": "", "trigger": "post",
           "supersedes": None, "dominated_by": None, "snapshot": None}
    (proj / ".loop").mkdir()
    (proj / ".loop" / "watch.jsonl").write_text(json.dumps(old, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 0 and records(proj) == [old]                                                 # nothing judged, nothing appended
    assert "watch stub app.txt (what did not run was not recorded)" in err, err


def test_the_state_folder_is_never_an_input(proj, monkeypatch, capsys):
    setcfg(proj, state_dir="loop-state", watch=[{"name": "stub", "files": ["app.txt"], "run": RUN, "inputs": ["**/*"]}])
    put(proj, "LOAD=1\n")
    hook_run(monkeypatch, capsys, proj, "post")                                              # one record; the state folder fills up
    assert len(records(proj, "loop-state")) == 1
    capsys.readouterr()
    rc, out, _ = hook_run(monkeypatch, capsys, proj, "post")                                 # its post counter changed: no judgement
    assert rc == 0 and out == "" and len(records(proj, "loop-state")) == 1


# item 2: a ledger line that is not a record is skipped, said once per run, and its bytes are judged again.

TORN = '{"at": "2026-11-10T09:00:00+00:00", "id": "9f'      # a write cut off before its end: no newline, and not JSON


def tear(root, text, folder=".loop"):
    (root / folder).mkdir(exist_ok=True)
    with (root / folder / "watch.jsonl").open("a", encoding="utf-8") as f:
        f.write(text)


def test_a_torn_line_is_skipped_said_once_and_the_bytes_it_was_for_are_judged_again(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    hook_run(monkeypatch, capsys, proj, "post")                                              # line 1: a record for these bytes
    tear(proj, TORN)                                                                         # line 2: torn; meant for the next bytes
    put(proj, "BROKEN\n")
    rc, out, err = hook_run(monkeypatch, capsys, proj, "post")
    assert rc == 0 and err.count("watch ledger: ") == 1 and "watch ledger: 1 unreadable line(s) skipped: line 2" in err, err
    assert "FAIL" in context(out) and [r["gate"] for r in records(proj)] == ["pass", "fail"]


def test_a_stop_whose_only_record_is_torn_judges_the_bytes_and_says_so(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    tear(proj, TORN)
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 0 and err.count("watch ledger: ") == 1 and "line 1" in err, err
    assert [r["gate"] for r in records(proj)] == ["pass"] and "fails open" not in err


def test_a_line_that_is_no_record_is_skipped_and_the_records_around_it_still_count(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    hook_run(monkeypatch, capsys, proj, "post")                                              # line 1: the record for these bytes
    tear(proj, "[1, 2]\n{}\n")                                                               # lines 2 and 3: JSON, and no record
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 0 and "watch ledger: 2 unreadable line(s) skipped: line 2, line 3" in err, err
    assert len(records(proj)) == 1 and "fails open" not in err


def test_a_record_written_after_a_torn_line_is_a_line_of_its_own(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    tear(proj, TORN)                                                                         # the file ends with no newline
    rc, _, err = hook_run(monkeypatch, capsys, proj, "post")
    assert rc == 0 and "watch ledger: 1 unreadable line(s) skipped: line 1" in err, err
    recs = records(proj)
    assert [r["gate"] for r in recs] == ["pass"] and recs[0]["path"] == "app.txt"


def test_status_reads_past_a_torn_line_and_says_it_once(proj, capsys):
    put(proj, "LOAD=1\n")
    watch.main(["eval"])
    tear(proj, TORN)
    capsys.readouterr()
    assert watch.main(["status"]) == 0
    out, err = capsys.readouterr()
    assert "PASS" in out and err.count("watch ledger: ") == 1, (out, err)


# item 4: the watch lock. A post that finds it held judges nothing and says so; a stop waits for it inside its budget and refuses what it
# could not judge.

def test_a_post_that_finds_the_watch_lock_held_judges_nothing_and_says_so(proj, monkeypatch, capsys):
    import fcntl
    put(proj, "LOAD=1\n")
    (proj / ".loop").mkdir()
    with open(proj / ".loop" / "watch.lock", "w") as held:
        fcntl.flock(held, fcntl.LOCK_EX)                                                     # another run is judging
        t0 = time.monotonic()
        rc, out, err = hook_run(monkeypatch, capsys, proj, "post", tool_name="Edit")
        elapsed = time.monotonic() - t0
    assert (rc, out) == (0, "") and "another run is judging" in err and elapsed < 2, (rc, out, err, elapsed)
    assert records(proj) == []


def test_a_stop_that_cannot_get_the_watch_lock_within_its_budget_refuses_what_it_could_not_judge(proj, monkeypatch, capsys):
    import fcntl
    put(proj, "LOAD=1\n")
    (proj / ".loop").mkdir()
    monkeypatch.setenv("LOOP_HOOK_BUDGET_S", "1")                                            # the stop's budget: one second
    with open(proj / ".loop" / "watch.lock", "w") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        t0 = time.monotonic()
        rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
        elapsed = time.monotonic() - t0
    assert rc == 2 and "refusal 1 of 2" in err and "did not run: watch stub app.txt" in err and "not evaluated (lock held)" in err, err
    assert elapsed < 4 and records(proj) == [], elapsed


# item 5: a PASS says what its check did not run, wherever it is said.

ENGINE_CHAIN = json.dumps({"provenance": {"source": "narrated", "date": "2026-11-10", "who": "made up for a loop test"},
                           "task": "Open the settings of a made-up app",
                           "steps": [{"op": "NAVIGATE", "held": ["goal: settings"], "target": "open the app"},
                                     {"op": "ANCHOR", "anchor": "edge", "target": "the gear icon, top right"},
                                     "TAP Settings"]})


def test_a_pass_of_another_command_keeps_unreported_coverage_unknown(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    assert "PASS (coverage beyond reported layers is unknown)" in context(hook_run(monkeypatch, capsys, proj, "post")[1])


def test_a_pass_of_the_engine_verdict_says_what_the_engine_did_not_run(proj, monkeypatch, capsys):
    """The real verdict (checks/verdict.py) on a chain that passes: no smoke layer (--no-smoke), and the two things its own report
    names as not in the verdict yet. The names are taken from its report, and smoke from the layers it can run."""
    (proj / "trial.chain.json").write_text(ENGINE_CHAIN, encoding="utf-8")
    setcfg(proj, watch=[{"name": "engine", "files": ["app.txt"],
                         "run": ["python3", "-I", str(KIT / "checks" / "verdict.py"), "{path}", "--no-smoke", "--chain", "trial.chain.json"]}])
    put(proj, "a file the engine judges\n")
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "PASS (not run: smoke, explore, chains captured from a driven run)" in ctx, ctx


def test_the_layers_a_pass_leaves_out_are_the_ones_the_engine_assigns():
    """The layer names the emu adapter knows are those checks/verdict.py assigns to its layers; a layer added there must be added here."""
    src = (KIT / "checks" / "verdict.py").read_text(encoding="utf-8")
    assigned = set(re.findall(r'layers\["(\w+)"\] = ', src))
    assert assigned == set(emu.EMU_LAYERS), (sorted(assigned), emu.EMU_LAYERS)


def test_a_pass_whose_verdict_says_nothing_about_what_it_leaves_out_says_it_is_unknown():
    note = watch.pass_note(["python3", "-I", "checks/verdict.py", "{path}"], {"chain": "pass"}, 'chain: pass\n{"gate": "pass"}\n')
    assert note == "not run: unknown, the verdict did not say what it leaves out", note


def test_a_stop_that_lets_a_pass_through_says_what_the_pass_did_not_run(proj, monkeypatch, capsys):
    put(proj, "LOAD=1\n")
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 0 and "loop hook stop: passed: watch stub app.txt (coverage beyond reported layers is unknown)" in err, err


def test_status_names_what_a_pass_did_not_run(proj, capsys):
    put(proj, "LOAD=1\n")
    watch.main(["eval"])
    capsys.readouterr()
    assert watch.main(["status"]) == 0
    assert "PASS (coverage beyond reported layers is unknown)" in capsys.readouterr().out


# retired checks/emu_loop.py (docs/EMU-LOOP-RETIRED.md): the engine's verdict judged through watch, a missing trial chain, a restore
# hint that names a copy with its inputs, the event a post answers, and the error line of a check that did not run under a banner.

CHAIN_BAD = KIT / "checks" / "fixtures" / "chains" / "hw1_correction_pass.json"         # recorded: 'expensive' trips the verifiers
CHAIN_GOOD = KIT / "checks" / "fixtures" / "chains" / "hw1_correction_pass_fixed.json"   # designed: no findings
VERDICT = str(KIT / "checks" / "verdict.py")


def verdict_entry(name, chain):
    return {"name": name, "files": ["app.txt"], "run": ["python3", "-I", VERDICT, "{path}", "--no-smoke", "--chain", str(chain)]}


def test_the_engine_verdict_fails_the_known_bad_chain_and_passes_the_known_good_one_through_watch(proj):
    setcfg(proj, watch=[verdict_entry("bad", CHAIN_BAD), verdict_entry("good", CHAIN_GOOD)])
    put(proj, "an artifact the verdict reads\n")
    cfg = config.load()
    bad = watch.evaluate(cfg, cfg["watch"][0], "app.txt", "manual", force=True)
    good = watch.evaluate(cfg, cfg["watch"][1], "app.txt", "manual", force=True)
    assert bad["gate"] == "fail" and good["gate"] == "pass", (bad["tail"], good["tail"])
    assert bad["vector"]["chain_findings"] > good["vector"]["chain_findings"], (bad["vector"], good["vector"])
    assert bad["vector"]["chain_load"] > good["vector"]["chain_load"], (bad["vector"], good["vector"])


def test_a_missing_trial_chain_holds_the_stop_through_watch(proj, monkeypatch, capsys, tmp_path):
    trial = tmp_path / "trial.chain.json"
    setcfg(proj, watch=[verdict_entry("verdict", trial)])
    put(proj, "an artifact the verdict reads\n")
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")          # no trial chain: the chain layer did not run
    assert rc == 2 and "did not run" in err, err
    trial.write_bytes(CHAIN_GOOD.read_bytes())                        # the trial appears
    rc, _, err = hook_run(monkeypatch, capsys, proj, "stop")
    assert rc == 0, err


def test_a_regression_offers_no_one_line_restore_when_its_inputs_differ(proj, monkeypatch, capsys):
    setcfg(proj, watch=INPUT_WATCH)
    (proj / "policy").mkdir()
    (proj / "policy" / "rules.txt").write_text("v1\n", encoding="utf-8")
    put(proj, "LOAD=1\n")
    hook_run(monkeypatch, capsys, proj, "post")                       # candidate A: passes at load 1, with inputs v1
    put(proj, "LOAD=2\n")                                             # B: dominated by A, judged with the same inputs
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "REGRESSION" in ctx and "cp " in ctx, ctx                  # control: same inputs, so the copy restores the candidate
    (proj / "policy" / "rules.txt").write_text("v2\n", encoding="utf-8")   # the inputs change
    put(proj, "LOAD=2 \n")                                            # C: dominated by A, judged with inputs v2
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "REGRESSION" in ctx and "cp " not in ctx and "inputs differ" in ctx, ctx


def test_the_post_output_names_the_event_it_answers_and_exits_0(proj, monkeypatch, capsys):
    put(proj, "BROKEN\n")
    rc, out, _ = hook_run(monkeypatch, capsys, proj, "post", tool_name="Edit")
    assert rc == 0 and json.loads(out)["hookSpecificOutput"]["hookEventName"] == "PostToolUse", out


BANNER_CHECK = '''import sys
print("Traceback (most recent call last):", file=sys.stderr)
print("RuntimeError: the page did not mount", file=sys.stderr)
for line in ("+----------------------------+", "| Playwright was just updated |", "| <3 the Playwright team     |", "+----------------------------+"):
    print(line, file=sys.stderr)
sys.exit(3)
'''


def test_a_check_error_under_a_banner_still_reaches_the_session(proj, monkeypatch, capsys):
    (proj / "banner_check.py").write_text(BANNER_CHECK, encoding="utf-8")
    setcfg(proj, watch=[{"name": "banner", "files": ["app.txt"], "run": ["python3", "-I", "banner_check.py", "{path}"]}])
    put(proj, "an artifact\n")
    ctx = context(hook_run(monkeypatch, capsys, proj, "post")[1])
    assert "NOT EVALUATED" in ctx and "RuntimeError: the page did not mount" in ctx, ctx


def test_generic_checker_without_layers_says_so():
    assert watch.pass_note(["python3", "check.py"], {}, "") == "the check reports no layers"


def test_emu_adapter_preserves_complete_and_partial_coverage():
    assert emu.accepts(["bash", "bin/emu", "verdict", "page.html"])
    assert not emu.accepts(["python3", "check.py"])
    assert emu.pass_note({"smoke": "pass", "chain": "pass"}, "not in the verdict yet:  are not in this loop") == "all layers ran"
    assert emu.pass_note({"chain": "pass"}, "not in the verdict yet: explore (optional) and chains captured from a driven run are not in this loop") == "not run: smoke, explore, chains captured from a driven run"
