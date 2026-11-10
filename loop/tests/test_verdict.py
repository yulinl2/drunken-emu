"""Tests of loop/verdict.py, the verdict verb of the guard, and of the guard's reading of the rows the verb writes.
Every name is invented (alice, bob, project-x, topic-a, example.invalid); every project is a folder under tmp_path."""
import ast, datetime, hashlib, json, os, pathlib, re, subprocess, sys
import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import guard, verdict

LOOP = KIT / "bin" / "loop"
H1, H2, BASE = "a" * 39 + "1", "b" * 39 + "2", "c" * 40
NOW = datetime.datetime(2026, 11, 5, 13, 30, 25, tzinfo=datetime.timezone.utc)
BRANCH = "claude/topic-a-2026-11-05-r5"
ANSWER = "advisor-answers/example.md"
LEDGER = "loop-state/verdicts.jsonl"
PUSH = f"git push origin {H1}:refs/heads/main"
LEASE_CMD = f"git push --force-with-lease=topic-old:{H1} origin :topic-old"
MERGE = "mcp__github__merge_pull_request"


def make_project(tmp_path, name="proj", origin=None, conf=None):
    """A project folder: loop.json, a git repository, and an origin remote when one is given."""
    root = tmp_path / name
    root.mkdir(parents=True)
    (root / "loop.json").write_text(json.dumps({"sessions": "all", **(conf or {})}), encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    if origin is not None:
        subprocess.run(["git", "-C", str(root), "remote", "add", "origin", origin], check=True, capture_output=True)
    return root


def answer_at(root, text=None):
    """The advisor's answer file under the project; by default it names H1."""
    path = root / ANSWER
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"verdict GO on {H1}\n" if text is None else text, encoding="utf-8")


def env_for(root):
    env = {k: v for k, v in os.environ.items() if not k.startswith("LOOP_")}
    env.update(HOME=str(root.parent / "home"), LOOP_PROJECT=str(root))
    return env


def run(root, *argv, stdin=""):
    """The loop entry, run for this project with a home folder of its own: (exit code, standard output, standard error)."""
    r = subprocess.run([sys.executable, "-I", str(LOOP), *argv], input=stdin, capture_output=True, text=True,
                       cwd=str(root), env=env_for(root), timeout=120)
    return r.returncode, r.stdout, r.stderr


def pre(root, command=None, tool=None, tool_input=None):
    """The guard's answer to one call in this project: the deny reason, or None when the call passes."""
    payload = {"tool_name": tool or "Bash", "tool_input": tool_input or {"command": command}, "cwd": str(root)}
    code, out, err = run(root, "guard", "pre", stdin=json.dumps(payload))
    assert code == 0, err
    if not out.strip():
        return None
    o = json.loads(out)["hookSpecificOutput"]
    assert o["permissionDecision"] == "deny", o
    return o["permissionDecisionReason"]


def rows(root, ledger=LEDGER):
    path = root / ledger
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []


def go_argv(head=H1, *, base=BASE, answer=ANSWER, extra=()):
    return ["guard", "verdict", "go", "--head", head, "--base", base, "--branch", BRANCH,
            "--by", "advisor example", "--answer", answer, "--note", "reviewed", *extra]


def merge_kw(root, **over):
    kw = dict(head=H1, base=BASE, branch=BRANCH, by="advisor example", answer=ANSWER, note="reviewed",
              rows=[], root=root, now=NOW)
    kw.update(over)
    return kw


# The port of the source's selftest, as tests of the functions.

def test_a_hold_row_ends_in_pending_and_carries_the_hold_undo(tmp_path):
    row = verdict.merge_row("hold", **merge_kw(tmp_path, by="root"))
    assert row["id"] == f"v-20261105T1330Z-topic-a-{H1[:8]}-pending"
    assert row["verdict"] == "hold" and row["kind"] == "merge" and row["head"] == H1
    assert row["undo"] == verdict.HOLD_UNDO and not guard.counts(row)


def test_a_second_row_of_the_same_head_and_verdict_is_refused(tmp_path):
    first = verdict.merge_row("hold", **merge_kw(tmp_path))
    with pytest.raises(verdict.Refused, match="exists"):
        verdict.merge_row("hold", **merge_kw(tmp_path, rows=[first]))
    answer_at(tmp_path)
    assert verdict.merge_row("go", **merge_kw(tmp_path, rows=[first]))["verdict"] == "go"      # a go is another verdict


def test_a_head_base_or_tree_that_is_not_40_lower_case_hex_is_refused(tmp_path):
    answer_at(tmp_path)
    for bad in ("zz", H1[:39], H1 + "0", H1.upper()):
        with pytest.raises(verdict.Refused, match="40"):
            verdict.merge_row("go", **merge_kw(tmp_path, head=bad))
    with pytest.raises(verdict.Refused, match="40"):
        verdict.merge_row("go", **merge_kw(tmp_path, base="c" * 39))
    with pytest.raises(verdict.Refused, match="40"):
        verdict.merge_row("go", **merge_kw(tmp_path, tree="g" * 40))


def test_a_go_row_needs_an_answer_file_on_disk_that_names_its_head(tmp_path):
    with pytest.raises(verdict.Refused, match="missing"):
        verdict.merge_row("go", **merge_kw(tmp_path))
    answer_at(tmp_path, "the advisor said yes to another head\n")
    with pytest.raises(verdict.Refused, match="does not name"):
        verdict.merge_row("go", **merge_kw(tmp_path))
    answer_at(tmp_path)
    row = verdict.merge_row("go", **merge_kw(tmp_path))
    assert row["id"] == f"v-20261105T1330Z-topic-a-{H1[:8]}" and row["undo"] == verdict.GO_UNDO and guard.counts(row)


# What the new verb adds to the port.

def test_the_fields_the_guard_reads_are_written_and_an_undo_given_replaces_the_default(tmp_path):
    answer_at(tmp_path)
    row = verdict.merge_row("go", **merge_kw(tmp_path, pr=7, repo="Alice/Project-X", tree=BASE, tests="12 OK"))
    assert (row["kind"], row["pr"], row["repo"], row["tree"], row["tests"]) == ("merge", 7, "alice/project-x", BASE, "12 OK")
    assert guard.counts(row) and not guard.counts({**row, "undo": " "}) and not guard.counts({**row, "verdict": "hold"})
    undo = verdict.merge_row("go", **merge_kw(tmp_path, pr=7, repo="alice/project-x", undo="git revert -m 1 <merge sha>"))["undo"]
    assert undo == "git revert -m 1 <merge sha>"


@pytest.mark.parametrize("remote, repo", [
    ("example.invalid:Alice/Project-X.git", "alice/project-x"),
    ("example.invalid:alice/project-x", "alice/project-x"),
    ("ssh://example.invalid/Alice/Project-X.git", "alice/project-x"),
    ("example.invalid:alice/project-x/extra", None),
    ("example.invalid:alice", None),
    ("local-origin.git", None),
])
def test_the_repository_of_the_origin_remote_is_read_lower_case_and_only_a_two_part_path_names_one(remote, repo):
    assert verdict.repo_of_remote(remote) == repo


def test_a_command_row_is_named_by_its_string_and_takes_the_go_undo(tmp_path):
    answer_at(tmp_path)
    kw = dict(command=LEASE_CMD, by="reviewer", answer=ANSWER, note="reviewed", rows=[], root=tmp_path, now=NOW)
    row = verdict.command_row(**kw)
    digest = hashlib.sha256(LEASE_CMD.encode("utf-8")).hexdigest()[:8]
    assert row["id"] == f"v-20261105T1330Z-command-{digest}" and row["kind"] == "command" and row["command"] == LEASE_CMD
    assert row["verdict"] == "go" and row["undo"] == verdict.GO_UNDO and guard.counts(row)
    with pytest.raises(verdict.Refused, match="exists"):
        verdict.command_row(**{**kw, "rows": [row]})


def test_a_withdrawal_names_a_row_the_file_holds(tmp_path):
    answer_at(tmp_path)
    row = verdict.command_row(command=LEASE_CMD, by="reviewer", answer=ANSWER, note="n", rows=[], root=tmp_path, now=NOW)
    assert verdict.withdrawal(row["id"], rows=[row], note="changed my mind", now=NOW) == {
        "verdict": "withdrawn", "of": row["id"], "at": "2026-11-05T13:30:25Z", "note": "changed my mind"}
    with pytest.raises(verdict.Refused, match="no verdict row"):
        verdict.withdrawal("v-nope", rows=[row], now=NOW)


def test_the_slug_is_the_branch_name_without_its_date_and_round_in_lower_case_letters_digits_and_hyphens(tmp_path):
    row = verdict.merge_row("hold", **merge_kw(tmp_path, branch="claude/Topic_A.2-2026-11-05-r5"))
    assert row["id"] == f"v-20261105T1330Z-topic-a-2-{H1[:8]}-pending"
    row = verdict.merge_row("hold", **merge_kw(tmp_path, head=H2, slug="Topic A!"))
    assert row["id"] == f"v-20261105T1330Z-topic-a-{H2[:8]}-pending"


def test_the_module_imports_the_standard_library_and_the_kit_only():
    assert callable(verdict.main)
    tree = ast.parse((KIT / "loop" / "verdict.py").read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    allowed = {"argparse", "contextlib", "datetime", "fcntl", "hashlib", "json", "os", "pathlib", "re", "shlex", "subprocess", "sys", "loop"}
    assert names <= allowed, names


# The verb, through the entry.

def test_a_dry_run_writes_nothing_and_exits_0(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    code, out, err = run(root, *go_argv(extra=("--dry-run",)))
    assert code == 0, err
    assert json.loads(out.splitlines()[0])["verdict"] == "go" and "nothing written" in out
    assert not (root / "loop-state").exists()


def test_the_row_goes_to_the_configured_verdict_file_and_nowhere_else(tmp_path):
    root = make_project(tmp_path, conf={"verdicts": "evidence/verdicts.jsonl"})
    answer_at(root)
    code, out, err = run(root, *go_argv())
    assert code == 0, err
    assert len(rows(root, "evidence/verdicts.jsonl")) == 1 and not (root / "loop-state").exists()


def test_the_row_that_is_printed_is_the_row_that_is_written(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    code, out, err = run(root, *go_argv())
    assert code == 0, err
    row = rows(root)[0]
    assert json.loads(out.splitlines()[0]) == row and f"appended {row['id']}" in out
    assert re.fullmatch(r"v-\d{8}T\d{4}Z-topic-a-" + H1[:8], row["id"]), row["id"]


REFUSALS = [
    ("REFUSED", "a head that is not 40 hex", go_argv("zz")),
    ("REFUSED", "a base that is not 40 hex", go_argv(base="c" * 39)),
    ("REFUSED", "a tree that is not 40 hex", go_argv(extra=("--tree", "g" * 40))),
    ("REFUSED", "a go row with no answer file", go_argv(answer="advisor-answers/none.md")),
    ("REFUSED", "a go row whose answer file does not name its head", go_argv(H2)),
    ("--repo", "--pr with no repository", go_argv(extra=("--pr", "7"))),
    ("REFUSED", "a withdrawal of an id the file does not hold", ["guard", "verdict", "withdraw", "v-20261105T1330Z-nope-aaaaaaaa"]),
    ("REFUSED", "a command row with no answer file", ["guard", "verdict", "command", "--command", "git status", "--by", "reviewer",
                                                       "--answer", "advisor-answers/none.md", "--note", "n"]),
    ("required", "a required argument missing", ["guard", "verdict", "go", "--head", H1]),
    ("REFUSED", "a dry run of a refused row", go_argv("zz", extra=("--dry-run",))),
]


@pytest.mark.parametrize("said, name, argv", REFUSALS, ids=[r[1] for r in REFUSALS])
def test_a_refused_row_exits_2_and_writes_nothing(tmp_path, said, name, argv):
    root = make_project(tmp_path)
    answer_at(root)
    code, out, err = run(root, *argv)
    assert code == 2 and said in err, (name, err)
    assert not (root / "loop-state").exists() and not out.startswith("{"), (name, out)


def test_without_a_loop_json_nothing_is_written(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    (root / "loop.json").unlink()
    code, out, err = run(root, *go_argv())
    assert code == 2 and "no project" in err and not (root / "loop-state").exists(), err


def test_a_verdict_file_that_cannot_be_opened_refuses_with_exit_2(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    (root / "loop-state" / "verdicts.jsonl").mkdir(parents=True)
    code, out, err = run(root, *go_argv())
    assert code == 2 and "cannot be read or written" in err, err
    code, out, err = run(root, *go_argv(extra=("--dry-run",)))
    assert code == 2 and "cannot be read or written" in err, err


def test_a_second_hold_of_one_head_is_refused_and_the_file_keeps_one_row(tmp_path):
    root = make_project(tmp_path)
    hold = ["guard", "verdict", "hold", "--head", H1, "--base", BASE, "--branch", BRANCH, "--by", "root",
            "--answer", ANSWER, "--note", "n"]
    assert run(root, *hold)[0] == 0
    code, out, err = run(root, *hold)
    assert code == 2 and "exists" in err, err
    assert len(rows(root)) == 1 and rows(root)[0]["id"].endswith("-pending")


def test_a_withdrawn_go_row_still_blocks_a_new_go_row_for_its_head(tmp_path):
    """The source's rule, kept: a second go row for one head is refused whether or not the first was withdrawn."""
    root = make_project(tmp_path)
    answer_at(root)
    assert run(root, *go_argv())[0] == 0
    assert run(root, "guard", "verdict", "withdraw", rows(root)[0]["id"])[0] == 0
    code, out, err = run(root, *go_argv())
    assert code == 2 and "exists" in err, err


def test_pr_needs_a_repository_and_the_origin_remote_or_the_repo_option_names_one(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    code, out, err = run(root, *go_argv(extra=("--pr", "7")))
    assert code == 2 and "--repo" in err, err
    code, out, err = run(root, *go_argv(extra=("--pr", "7", "--repo", "Bob/Other-Repo")))
    assert code == 0, err
    assert rows(root)[0]["repo"] == "bob/other-repo" and rows(root)[0]["pr"] == 7
    named = make_project(tmp_path, name="named", origin="example.invalid:Alice/Project-X.git")
    answer_at(named)
    code, out, err = run(named, *go_argv(extra=("--pr", "7")))
    assert code == 0, err
    assert rows(named)[0]["repo"] == "alice/project-x"


def test_two_writers_at_once_append_two_whole_lines(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    procs = [subprocess.Popen([sys.executable, "-I", str(LOOP), "guard", "verdict", "command", "--command",
                               f"git push origin :topic-{name}", "--by", "reviewer", "--answer", ANSWER, "--note", "n"],
                              cwd=str(root), env=env_for(root), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
             for name in ("a", "b")]
    assert sorted(p.wait(timeout=120) for p in procs) == [0, 0]
    text = (root / LEDGER).read_text(encoding="utf-8")
    lines = text.splitlines()
    assert text.endswith("\n") and len(lines) == 2, text
    assert sorted(json.loads(line)["command"] for line in lines) == ["git push origin :topic-a", "git push origin :topic-b"]


def test_two_writers_of_one_row_at_once_write_one_and_refuse_the_other(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    procs = [subprocess.Popen([sys.executable, "-I", str(LOOP), *go_argv()], cwd=str(root), env=env_for(root),
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for _ in range(2)]
    assert sorted(p.wait(timeout=120) for p in procs) == [0, 2]
    assert len(rows(root)) == 1


# The guard reads what the verb writes.

def test_the_guard_denies_the_push_until_a_go_row_names_its_head_and_a_withdrawal_takes_it_back(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    before = pre(root, PUSH)
    assert before is not None and before.endswith("--note <text>") and f"guard verdict go --head {H1} " in before, before
    code, out, err = run(root, *go_argv())
    assert code == 0, err
    assert pre(root, PUSH) is None
    assert pre(root, f"git push origin {H2}:refs/heads/main") is not None
    code, out, err = run(root, "guard", "verdict", "withdraw", rows(root)[0]["id"], "--note", "changed my mind")
    assert code == 0, err
    assert pre(root, PUSH) is not None


def test_a_command_row_lets_exactly_its_string_through(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    assert pre(root, LEASE_CMD) is not None
    code, out, err = run(root, "guard", "verdict", "command", "--command", LEASE_CMD, "--by", "reviewer",
                         "--answer", ANSWER, "--note", "reviewed")
    assert code == 0, err
    assert pre(root, LEASE_CMD) is None
    reason = pre(root, LEASE_CMD.replace(H1, H2))
    assert reason is not None and reason.endswith("--answer <file> --note <text>") and "guard verdict command --command " in reason, reason


def test_a_merge_with_no_verdict_is_denied_with_the_command_that_writes_one(tmp_path):
    root = make_project(tmp_path)
    call = {"owner": "alice", "repo": "project-x", "pullNumber": 7, "merge_method": "merge", "expectedHeadSha": H1, "commit_message": "m"}
    reason = pre(root, tool=MERGE, tool_input=call)
    assert "no go verdict of kind merge for alice/project-x#7" in reason and f"guard verdict go --head {H1} " in reason, reason
    assert reason.endswith("--pr 7 --repo alice/project-x"), reason


def test_the_guard_lists_the_verdict_verb_and_the_verb_lists_its_forms(tmp_path):
    root = make_project(tmp_path)
    code, out, err = run(root, "guard", "-h")
    assert code == 0 and "verdict" in out, err
    code, out, err = run(root, "guard", "verdict", "-h")
    assert code == 0 and all(word in out for word in ("hold", "go", "command", "withdraw")), err


# With the fcntl module missing (a platform without file locks): the entry runs with that module made unimportable.

NO_FCNTL = ("import runpy, sys\n"
            "sys.modules['fcntl'] = None\n"        # an import of fcntl now raises ImportError
            "sys.argv = sys.argv[1:]\n"
            "runpy.run_path(sys.argv[0], run_name='__main__')\n")


def run_without_fcntl(root, *argv, stdin=""):
    """The loop entry, run for this project with the fcntl module unimportable: (exit code, standard output, standard error)."""
    r = subprocess.run([sys.executable, "-I", "-c", NO_FCNTL, str(LOOP), *argv], input=stdin, capture_output=True, text=True,
                       cwd=str(root), env=env_for(root), timeout=120)
    return r.returncode, r.stdout, r.stderr


def test_guard_pre_denies_a_push_to_a_protected_branch_without_a_verdict_as_it_does_with_fcntl(tmp_path):
    """The guard does its work where fcntl cannot be imported: the deny is the same as the one with the module present."""
    root = make_project(tmp_path)
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": PUSH}, "cwd": str(root)})
    code, out, err = run(root, "guard", "pre", stdin=payload)
    assert code == 0 and '"permissionDecision": "deny"' in out, (code, out, err)
    code, plain, err = run_without_fcntl(root, "guard", "pre", stdin=payload)
    assert code == 0 and plain == out, (code, plain, err)


def test_the_verdict_module_imports_with_fcntl_missing_and_holds_no_lock():
    code = "import sys; sys.modules['fcntl'] = None; sys.path.insert(0, sys.argv[1]); from loop import verdict; print(verdict.fcntl)"
    r = subprocess.run([sys.executable, "-I", "-c", code, str(KIT)], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0 and r.stdout.strip() == "None", r.stderr


WRITES = [
    ("go", go_argv()),
    ("hold", ["guard", "verdict", "hold", "--head", H1, "--base", BASE, "--branch", BRANCH, "--by", "root", "--answer", ANSWER, "--note", "n"]),
    ("command", ["guard", "verdict", "command", "--command", LEASE_CMD, "--by", "reviewer", "--answer", ANSWER, "--note", "n"]),
    ("withdraw", ["guard", "verdict", "withdraw", "v-20261105T1330Z-topic-a-aaaaaaaa"]),
    ("dry-run", go_argv(extra=("--dry-run",))),
]


@pytest.mark.parametrize("name, argv", WRITES, ids=[w[0] for w in WRITES])
def test_with_fcntl_missing_every_verb_that_writes_refuses_with_exit_2_in_one_line_and_writes_nothing(tmp_path, name, argv):
    root = make_project(tmp_path)
    answer_at(root)
    code, out, err = run_without_fcntl(root, *argv)
    assert code == 2 and len(err.splitlines()) == 1 and "the lock is not available here" in err, (name, code, err)
    assert out == "" and not (root / "loop-state").exists(), (name, out)


def test_with_fcntl_missing_a_withdrawal_leaves_the_ledger_as_it_was(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    assert run(root, *go_argv())[0] == 0
    before = (root / LEDGER).read_bytes()
    code, out, err = run_without_fcntl(root, "guard", "verdict", "withdraw", rows(root)[0]["id"])
    assert code == 2 and "the lock is not available here" in err, err
    assert (root / LEDGER).read_bytes() == before and out == "", out


# Advisor pins (probe copies only; every name invented).

def _fill(cmd):
    return (cmd.replace("<40 hex>", BASE).replace("<branch>", BRANCH).replace("<who>", "'advisor example'")
               .replace("<file>", ANSWER).replace("<text>", "reviewed"))


def test_pin_the_command_a_deny_names_records_the_verdict_from_the_project_folder(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    reason = pre(root, PUSH)
    cmd = _fill(reason.split("record the advisor's verdict first, with: ", 1)[1])
    env = {k: v for k, v in env_for(root).items() if k != "LOOP_PROJECT"}
    # run from a folder outside the project: the command must not depend on where it is run
    r = subprocess.run(cmd, shell=True, cwd=str(tmp_path), env=env, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, (cmd, r.stderr)
    assert pre(root, PUSH) is None


def test_pin_a_command_row_with_a_blank_answer_file_is_refused(tmp_path):
    root = make_project(tmp_path)
    answer_at(root, " \n")
    code, out, err = run(root, "guard", "verdict", "command", "--command", LEASE_CMD, "--by", "reviewer", "--answer", ANSWER, "--note", "n")
    assert code == 2 and "empty" in err and not (root / "loop-state").exists(), err


def test_pin_an_answer_that_holds_the_head_only_inside_a_longer_hex_run_is_refused(tmp_path):
    answer_at(tmp_path, f"verdict GO on 5{H1}\n")
    with pytest.raises(verdict.Refused, match="does not name"):
        verdict.merge_row("go", **merge_kw(tmp_path))


def test_pin_an_answer_that_names_the_head_in_upper_case_is_accepted(tmp_path):
    answer_at(tmp_path, f"verdict GO on {H1.upper()}\n")
    assert verdict.merge_row("go", **merge_kw(tmp_path))["head"] == H1


def test_pin_a_hold_after_a_counting_go_of_the_same_head_is_refused(tmp_path):
    answer_at(tmp_path)
    g = verdict.merge_row("go", **merge_kw(tmp_path))
    with pytest.raises(verdict.Refused, match="withdraw"):
        verdict.merge_row("hold", **merge_kw(tmp_path, rows=[g]))
    w = verdict.withdrawal(g["id"], rows=[g], now=NOW)
    assert verdict.merge_row("hold", **merge_kw(tmp_path, rows=[g, w]))["verdict"] == "hold"


def test_pin_a_loop_json_that_is_not_json_makes_the_verb_refuse_with_exit_2_in_one_line(tmp_path):
    root = make_project(tmp_path)
    answer_at(root)
    (root / "loop.json").write_text("{", encoding="utf-8")
    code, out, err = run(root, *go_argv())
    assert code == 2 and len(err.splitlines()) == 1 and not (root / "loop-state").exists(), (code, err)

