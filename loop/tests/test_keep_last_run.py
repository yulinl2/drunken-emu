"""Tests of keep.last_run and of the backup line doctor prints: this machine's LAST-RUN or status file first; with none, the
first two lines of LAST-RUN on the session's backup branch at the remote (one fetch of at most 5 s into a scratch repository,
so no ref of the project and no file of its work tree is touched); the prompt notice stays failure-only. Every test points
HOME, LOOP_PROJECT, LOOP_PROJECTS_DIR and LOOP_TRANSCRIPT at folders under tmp_path."""
import hashlib, json, os, pathlib, re, shutil, subprocess, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from loop import cli, config, hook, keep

GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_NOSYSTEM": "1"}
SID = "abcd1234"                 # the session: the first 8 characters of its transcript's name
BR = "backup/abcd1234"           # the session's branch at the remote: the prefix backup/ and the session
STAMP = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ"


def git(*a, cwd=None, data=None):
    """stdout of a git command, stripped; a command that fails fails the test."""
    return subprocess.run(["git", *a], cwd=cwd, input=data, capture_output=True, text=True, check=True).stdout.strip()


class Project:
    """A project whose loop.json names a backup remote (a bare repository, named origin) and one session's transcript.
    Nothing is backed up until a test runs a backup."""

    def __init__(self, tmp, monkeypatch):
        self.tmp = tmp.resolve()
        self.bare, self.repo, self.projects = self.tmp / "origin.git", self.tmp / "repo", self.tmp / "projects"
        self.transcript = self.projects / "-p" / (SID + "-x.jsonl")
        self.transcript.parent.mkdir(parents=True)
        self.transcript.write_text('{"turn": 1}\n', encoding="utf-8")
        home = self.tmp / "home"
        home.mkdir()
        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setenv("LOOP_PROJECT", str(self.repo))
        monkeypatch.setenv("LOOP_PROJECTS_DIR", str(self.projects))
        monkeypatch.setenv("LOOP_TRANSCRIPT", str(self.transcript))
        for k, v in GIT_ENV.items():
            monkeypatch.setenv(k, v)
        git("init", "-q", "--bare", str(self.bare), cwd=self.tmp)
        self.repo.mkdir()
        git("init", "-q", "-b", "main", cwd=self.repo)
        (self.repo / "loop.json").write_text(json.dumps({"sessions": "all", "backup": {"remote": "origin"}}), encoding="utf-8")
        git("add", "-A", cwd=self.repo)
        git("commit", "-qm", "r", cwd=self.repo)
        git("remote", "add", "origin", str(self.bare), cwd=self.repo)

    def backup(self):
        """One waited backup run of the session; it must end without a refusal."""
        assert keep.main(["backup", "--wait"]) == 0

    def forget_state(self):
        """What a reclaimed machine leaves behind: this machine's state folder is gone."""
        shutil.rmtree(self.repo / ".loop")

    def move_remote_away(self):
        """The remote path no longer exists, so a fetch of it fails at once."""
        self.bare.rename(self.tmp / "moved.git")


def push_last_run(bare, text):
    """Make the session's branch on the bare repository, holding one file LAST-RUN with text (plumbing only: no work tree)."""
    blob = git("--git-dir", str(bare), "hash-object", "-w", "--stdin", data=text)
    tree = git("--git-dir", str(bare), "mktree", data=f"100644 blob {blob}\tLAST-RUN\n")
    commit = git("--git-dir", str(bare), "commit-tree", tree, "-m", "t")
    git("--git-dir", str(bare), "update-ref", f"refs/heads/{BR}", commit)


def doctor_json(capsys):
    """What doctor printed, as a dict; doctor must exit 0."""
    capsys.readouterr()
    assert cli.doctor() == 0
    return json.loads(capsys.readouterr().out)


def work_tree(root):
    """Every file under root except the git directory, and every folder of it, as {relative path: sha256 of the bytes, or "dir"}."""
    seen = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        for name in sorted(files) + dirs:
            path = pathlib.Path(base, name)
            seen[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "dir"
    return seen


def test_the_pushed_copy_answers_when_this_machine_has_no_state(tmp_path, monkeypatch):
    p = Project(tmp_path, monkeypatch)
    p.backup()
    p.forget_state()
    refs = git("for-each-ref", cwd=p.repo)
    got = keep.last_run(config.load(), SID)
    assert re.fullmatch(r"running since " + STAMP + r"\nprevious run: none", str(got)), repr(got)
    assert got.source == "pushed", got.source
    assert git("for-each-ref", cwd=p.repo) == refs, "the project's refs changed"
    assert not (p.repo / ".loop").exists(), "a state folder was made to read the remote"


def test_after_a_second_run_the_pushed_copy_carries_the_outcome_of_the_first(tmp_path, monkeypatch):
    p = Project(tmp_path, monkeypatch)
    p.backup()
    p.backup()
    p.forget_state()
    got = keep.last_run(config.load(), SID)
    first, second = str(got).split("\n")
    assert first.startswith("running since ") and re.fullmatch(r"previous run: ok " + STAMP, second), repr(got)
    assert got.source == "pushed", got.source


def test_an_unreachable_remote_gives_nothing_within_the_limit_and_doctor_says_so(tmp_path, monkeypatch, capsys):
    p = Project(tmp_path, monkeypatch)
    p.backup()
    p.forget_state()
    p.move_remote_away()
    started = time.monotonic()
    got = keep.last_run(config.load(), SID)
    assert time.monotonic() - started < 6
    assert str(got) == "" and got.source == "unreachable", repr(got)
    out = doctor_json(capsys)
    assert out["last_backup"] is None and out["last_backup_source"] == "unreachable", out
    assert not (p.repo / ".loop").exists()


def test_a_pushed_running_line_and_the_run_before_are_both_returned(tmp_path, monkeypatch):
    p = Project(tmp_path, monkeypatch)
    push_last_run(p.bare, "running since 2026-01-02T03:04:05Z\nprevious run: ok 2026-01-01T00:00:00Z\n")
    got = keep.last_run(config.load(), SID)
    assert str(got) == "running since 2026-01-02T03:04:05Z\nprevious run: ok 2026-01-01T00:00:00Z", repr(got)
    assert got.source == "pushed", got.source


def test_a_local_file_wins_and_no_git_runs_to_read_the_remote(tmp_path, monkeypatch, capsys):
    p = Project(tmp_path, monkeypatch)
    p.backup()
    p.move_remote_away()
    fake = tmp_path / "fakebin"
    fake.mkdir()
    calls = tmp_path / "git-calls.txt"
    (fake / "git").write_text(f'#!/bin/sh\necho "$*" >> "{calls}"\nexit 1\n', encoding="utf-8")
    (fake / "git").chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake}{os.pathsep}{os.environ['PATH']}")
    got = keep.last_run(config.load(), SID)
    assert re.fullmatch(r"ok " + STAMP, str(got)), repr(got)
    assert got.source == "local", got.source
    out = doctor_json(capsys)
    assert out["last_backup"] == str(got) and out["last_backup_source"] == "local", out
    assert not calls.exists(), "a git command ran: " + calls.read_text(encoding="utf-8")


def test_a_reachable_remote_without_the_branch_says_none(tmp_path, monkeypatch):
    Project(tmp_path, monkeypatch)
    got = keep.last_run(config.load(), SID)
    assert str(got) == "" and got.source == "none", repr(got)


def test_fetch_false_never_reads_the_remote(tmp_path, monkeypatch):
    p = Project(tmp_path, monkeypatch)
    push_last_run(p.bare, "ok 2026-01-01T00:00:00Z\n")
    got = keep.last_run(config.load(), SID, fetch=False)
    assert str(got) == "" and got.source == "none", repr(got)


def test_a_pushed_running_line_that_last_run_returns_for_the_prompt_reaches_no_prompt(tmp_path, monkeypatch, capsys):
    p = Project(tmp_path, monkeypatch)
    push_last_run(p.bare, "running since 2026-01-02T03:04:05Z\nprevious run: ok 2026-01-01T00:00:00Z\n")
    payload = {"cwd": str(p.repo), "transcript_path": str(p.transcript)}
    monkeypatch.setattr(hook, "_payload", lambda: payload)
    seen = keep.last_run(config.load(), keep.session_id(payload["transcript_path"]))   # the call that cmd_prompt makes
    assert str(seen).startswith("running since "), repr(seen)   # the untouched tree returns "" here, so this test fails there
    assert seen.source == "pushed", seen.source
    capsys.readouterr()
    assert hook.cmd_prompt([]) == 0
    out = capsys.readouterr().out
    assert "last backup" not in out and "running since" not in out, out


def test_a_fetch_that_hangs_is_ended_at_the_limit_and_reads_as_unreachable(tmp_path, monkeypatch):
    p = Project(tmp_path, monkeypatch)
    real_git = shutil.which("git")
    fake = tmp_path / "fakebin"
    fake.mkdir()
    (fake / "git").write_text(f'#!/bin/sh\ncase " $* " in *" fetch "*) sleep 30;; *) exec "{real_git}" "$@";; esac\n', encoding="utf-8")
    (fake / "git").chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake}{os.pathsep}{os.environ['PATH']}")
    started = time.monotonic()
    got = keep.last_run(config.load(), SID)
    took = time.monotonic() - started
    assert 4.5 < took < 9, took
    assert str(got) == "" and got.source == "unreachable", repr(got)
    assert p.repo.exists()


def test_reading_the_pushed_copy_leaves_the_work_tree_and_the_branches_as_they_were(tmp_path, monkeypatch):
    p = Project(tmp_path, monkeypatch)
    p.backup()
    p.forget_state()
    before = (git("for-each-ref", cwd=p.repo), git("rev-parse", "HEAD", cwd=p.repo), work_tree(p.repo))
    got = keep.last_run(config.load(), SID)
    assert got.source == "pushed", got.source   # the remote really was read
    assert (git("for-each-ref", cwd=p.repo), git("rev-parse", "HEAD", cwd=p.repo), work_tree(p.repo)) == before


def test_the_fallback_adds_no_setting():
    """The 5 s limit and the words git uses for a missing branch are constants of keep.py, not keys of loop.json. If a later change adds a
    setting on purpose, this list changes with it."""
    assert sorted(config.DEFAULTS) == ["backup", "bank", "chain_debt", "checks", "clause_bank_dir", "not_principal_prefixes", "principal_method",
                                       "protected_branches", "reread_every", "revisit", "sessions", "state_dir", "stop_blocks_on", "stop_cap",
                                       "stop_runs", "transcripts_dir", "tree", "verdicts", "watch", "words"]
    assert sorted(config.DEFAULTS["backup"]) == ["extra_dirs", "prefix", "remote"]


def test_only_the_first_two_lines_of_the_pushed_copy_are_returned(tmp_path, monkeypatch):
    p = Project(tmp_path, monkeypatch)
    push_last_run(p.bare, "running since 2026-01-02T03:04:05Z\nprevious run: ok 2026-01-01T00:00:00Z\na third line\nand a fourth\n")
    got = keep.last_run(config.load(), SID)
    assert str(got) == "running since 2026-01-02T03:04:05Z\nprevious run: ok 2026-01-01T00:00:00Z", repr(got)   # with no cap, the two lines after come back too
    assert got.source == "pushed", got.source


def test_the_pushed_copy_is_read_from_the_branch_under_the_configured_prefix(tmp_path, monkeypatch):
    p = Project(tmp_path, monkeypatch)
    (p.repo / "loop.json").write_text(json.dumps({"sessions": "all", "backup": {"remote": "origin", "prefix": "keep/"}}), encoding="utf-8")
    blob = git("--git-dir", str(p.bare), "hash-object", "-w", "--stdin", data="running since 2026-01-02T03:04:05Z\n")
    tree = git("--git-dir", str(p.bare), "mktree", data=f"100644 blob {blob}\tLAST-RUN\n")
    commit = git("--git-dir", str(p.bare), "commit-tree", tree, "-m", "t")
    git("--git-dir", str(p.bare), "update-ref", "refs/heads/keep/" + SID, commit)   # the same plumbing as push_last_run, under the configured prefix
    got = keep.last_run(config.load(), SID)
    assert str(got) == "running since 2026-01-02T03:04:05Z", repr(got)   # a backup/ prefix fixed in the code finds no branch and returns ""
    assert got.source == "pushed", got.source


def test_the_pushed_copy_is_read_from_the_remote_the_setting_names(tmp_path, monkeypatch):
    p = Project(tmp_path, monkeypatch)
    git("remote", "rename", "origin", "bk", cwd=p.repo)
    (p.repo / "loop.json").write_text(json.dumps({"sessions": "all", "backup": {"remote": "bk"}}), encoding="utf-8")
    push_last_run(p.bare, "running since 2026-01-02T03:04:05Z\nprevious run: ok 2026-01-01T00:00:00Z\n")
    got = keep.last_run(config.load(), SID)
    assert str(got) == "running since 2026-01-02T03:04:05Z\nprevious run: ok 2026-01-01T00:00:00Z", repr(got)   # a remote hard-coded as origin does not exist here
    assert got.source == "pushed", got.source
