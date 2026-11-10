"""Tests of the keep verb: loop/keep_backup.sh (the 24 tests of the source backup), loop/keep.py replay (the 14 tests of the
source replay tool) and restore. Every test points HOME, LOOP_PROJECT and LOOP_PROJECTS_DIR at folders under tmp_path."""
import contextlib, fcntl, io, json, os, pathlib, re, shutil, subprocess, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from loop import keep

SCRIPT = pathlib.Path(keep.__file__).with_name("keep_backup.sh")
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_NOSYSTEM": "1"}
K = "scratch"                        # the name of the extra folder: its key in the backup
BR = "backup/abcd1234"               # the prefix "backup/" and the first 8 characters of the newest transcript's name
OK = re.compile(r"^ok \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
DEAD = "gitdir: no-such-git-dir\n"   # a pointer file that leads nowhere


def git(*a, cwd, check=True):
    return subprocess.run(["git", *a], cwd=cwd, env={**os.environ, **GIT_ENV}, capture_output=True, text=True, check=check)


class Fixture:
    """A project repository whose loop.json names the extra folder K, a bare origin, a transcripts folder with a transcript
    and a subagent transcript, and the extra folder K: a plain file, a folder with spaces, a clone, a folder with a dead
    .git pointer and a 21 MB sparse file."""

    def __init__(self, tmp, monkeypatch, capfd):
        self.tmp = tmp.resolve()
        self.r, self.bare, self.projects = self.tmp / "repo", self.tmp / "origin.git", self.tmp / "projects"
        self.sp = self.tmp / K
        self.capfd = capfd
        home = self.tmp / "home"
        home.mkdir()
        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setenv("LOOP_PROJECT", str(self.r))
        monkeypatch.setenv("LOOP_PROJECTS_DIR", str(self.projects))
        monkeypatch.delenv("LOOP_TRANSCRIPT", raising=False)
        for k, v in GIT_ENV.items():
            monkeypatch.setenv(k, v)
        proj = self.projects / "-p"
        (proj / "abcd1234-x" / "subagents").mkdir(parents=True)
        (proj / "abcd1234-x.jsonl").write_text('{"turn": 1}\n')
        self.agent = proj / "abcd1234-x" / "subagents" / "agent-1.jsonl"
        self.agent.write_text('{"agent": 1}\n')
        sp = self.sp
        sp.mkdir()
        (sp / "plain.txt").write_text("plain\n")
        (sp / "sp ace").mkdir()
        (sp / "sp ace" / "y z.txt").write_text("spaces\n")
        clone = sp / "my clone"
        clone.mkdir()
        git("init", "-q", cwd=clone)
        (clone / "inside.txt").write_text("in the clone\n")
        git("add", "-A", cwd=clone)
        git("commit", "-qm", "c", cwd=clone)
        (sp / "ptr" / "deep").mkdir(parents=True)
        (sp / "ptr" / ".git").write_text(DEAD)
        (sp / "ptr" / "deep" / "f.txt").write_text("behind a dead pointer\n")
        with open(sp / "big.bin", "wb") as f:
            f.truncate(21 * 1024 * 1024)
        git("init", "-q", "--bare", str(self.bare), cwd=self.tmp)
        self.r.mkdir()
        git("init", "-q", "-b", "main", cwd=self.r)
        (self.r / "loop.json").write_text(json.dumps({"sessions": "all", "backup": {"remote": "origin", "extra_dirs": [str(sp)]}}))
        git("add", "-A", cwd=self.r)
        git("commit", "-qm", "r", cwd=self.r)
        git("remote", "add", "origin", str(self.bare), cwd=self.r)
        (self.r / "un tracked.txt").write_text("untracked\n")
        n = self.r / "nested"
        n.mkdir()
        git("init", "-q", cwd=n)
        (n / "n.txt").write_text("n\n")
        git("add", "-A", cwd=n)
        git("commit", "-qm", "n", cwd=n)
        (self.r / "rptr").mkdir()
        (self.r / "rptr" / ".git").write_text(DEAD)
        (self.r / "rptr" / "r.txt").write_text("r\n")
        self.state = self.r / ".loop"
        self.w = self.state / "backup-wt-abcd1234"   # one worktree for each session: the transcript here is abcd1234-x.jsonl
        self.log = self.state / "backup-abcd1234.log"
        self.lock = self.state / "backup-abcd1234.lock"

    def run(self, *args):
        rc = keep.main(["backup", *args])
        out, err = self.capfd.readouterr()
        assert (rc, out, err) == (0, "", ""), self.logtext()

    def run_failing(self, *args):
        """A waited run that cannot push: it returns 1 and says its FAILED line on standard error. The script itself still
        exits 0, so that a stop is never held by a backup."""
        rc = keep.main(["backup", *args])
        out, err = self.capfd.readouterr()
        assert rc == 1 and out == "" and err.startswith("keep backup: FAILED"), (rc, out, err, self.logtext())

    def logtext(self):
        return self.log.read_text() if self.log.exists() else "(no log)"

    def last_run(self):
        return (self.w / "LAST-RUN").read_text().splitlines()

    def tip(self, ref=BR):
        """(mode, path) of every entry of the origin's branch."""
        out = git("ls-tree", "-r", "-z", ref, cwd=self.bare).stdout
        return [(e.split(" ", 1)[0], e.split("\t", 1)[1]) for e in out.split("\0") if e]

    def paths(self, ref=BR):
        return [p for _, p in self.tip(ref)]

    def show(self, path, ref=BR):
        return git("show", f"{ref}:{path}", cwd=self.bare).stdout

    def head(self, where):
        if where == "origin":
            return git("rev-parse", BR, cwd=self.bare).stdout.strip()
        return git("rev-parse", "HEAD", cwd=self.w).stdout.strip()

    def break_origin(self):
        git("remote", "set-url", "origin", str(self.tmp / "no-such-origin.git"), cwd=self.r)

    def mend_origin(self):
        git("remote", "set-url", "origin", str(self.bare), cwd=self.r)


def test_a_waited_run_prints_nothing_exits_0_says_ok_and_the_origin_holds_the_worktree_head(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert f.head("origin") == f.head("worktree")
    assert f"extra/{K}/plain.txt" in f.paths()
    assert "FAILED" not in f.logtext()


def test_nested_repositories_are_listed_in_NESTED_tsv_and_none_of_their_files_is_copied(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    rows = [r.split("\t") for r in f.show("NESTED.tsv").splitlines()]
    got = {(r[0], r[1]): r[2] for r in rows}
    assert got[(K, "my clone")].startswith("dir ref: refs/heads/"), rows
    assert got[(K, "ptr")] == "file " + DEAD.strip()
    assert ("git/untracked", "nested/") in got, rows
    for p in f.paths():
        for root in (f"extra/{K}/my clone/", f"extra/{K}/ptr/", "git/untracked/nested"):
            assert not p.startswith(root), p
    assert not (f.w / "extra" / K / "my clone").exists()
    assert not (f.w / "git" / "untracked" / "nested").exists()


def test_no_path_named_dot_git_and_no_gitlink_reaches_the_commit(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    tip = f.tip()
    assert tip
    assert [p for m, p in tip if m == "160000"] == []
    assert [p for _, p in tip if ".git" in p.split("/")] == []
    assert [p for p in f.w.rglob(".git") if p != f.w / ".git"] == []


def test_a_file_over_20_MB_is_listed_in_LARGE_tsv_and_not_stored(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    rows = [r.split("\t") for r in f.show("LARGE.tsv").splitlines()]
    assert [(r[0], r[2]) for r in rows] == [(str(21 * 1024 * 1024), str(f.sp / "big.bin"))]
    assert re.fullmatch(r"[0-9a-f]{64}", rows[0][1])
    assert f"extra/{K}/big.bin" not in f.paths()


def test_the_transcripts_and_the_subagent_transcripts_are_stored_in_parts(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    assert f.show("transcripts/-p__abcd1234-x.jsonl.parts/part-000") == '{"turn": 1}\n'
    assert f.show("transcripts/subagents__agent-1.jsonl.parts/part-000") == '{"agent": 1}\n'


def test_names_with_spaces_are_copied_whole(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    assert f.show(f"extra/{K}/sp ace/y z.txt") == "spaces\n"
    assert f.show("git/untracked/un tracked.txt") == "untracked\n"


def test_LAST_RUN_says_running_since_during_the_push_and_ok_only_after_it(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    probe = f.tmp / "probe.txt"
    hook = f.r / ".git" / "hooks" / "pre-push"
    hook.write_text(f'#!/bin/sh\ncat "{f.w}/LAST-RUN" > "{probe}"\n')
    hook.chmod(0o755)
    f.run("--wait")
    assert re.match(r"^running since \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$", probe.read_text().splitlines()[0])
    assert f.show("LAST-RUN").splitlines()[0].startswith("running since ")
    assert OK.match(f.last_run()[0]), f.logtext()


def test_a_failed_push_writes_FAILED_step_git_push_with_the_log_and_never_ok_and_the_next_run_pushes_it(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    first = f.head("origin")
    (f.sp / "new.txt").write_text("made while the origin was gone\n")
    f.break_origin()
    f.run_failing("--wait")
    lines = f.last_run()
    assert re.match(r"^FAILED \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ: step git push, see " + re.escape(str(f.log)) + "$", lines[0]), lines
    assert not any(OK.match(x) for x in lines)
    assert f.head("origin") == first
    assert "step git push" in f.logtext()
    f.mend_origin()
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert f.head("origin") == f.head("worktree")
    assert f"extra/{K}/new.txt" in f.paths()
    assert re.match(r"^previous run: FAILED .*: step git push, see ", f.show("LAST-RUN").splitlines()[1])


def test_a_gitlink_left_in_the_index_by_an_earlier_run_leaves_it_and_its_folder_is_left_out_from_then_on(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    old = f.w / "extra" / K / "old"
    (old / "sub").mkdir(parents=True)
    (old / ".git").write_text(DEAD)
    (old / "a.txt").write_text("a\n")
    (old / "sub" / "b.txt").write_text("b\n")
    sha = git("rev-parse", "HEAD", cwd=f.r).stdout.strip()   # a gitlink to a copy whose .git points nowhere
    git("update-index", "--add", "--cacheinfo", f"160000,{sha},extra/{K}/old", cwd=f.w)
    listed = [(e.split(" ")[0], e.split("\t")[1]) for e in git("ls-files", "-s", cwd=f.w).stdout.splitlines()]
    assert ("160000", f"extra/{K}/old") in listed
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert [p for m, p in f.tip() if m == "160000"] == []
    assert f"extra/{K}/old" in f.show("LEFT-OUT.txt").splitlines()
    assert [p for p in f.paths() if p.startswith(f"extra/{K}/old/")] == []
    assert "left out of the backup from now on" in f.logtext()
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()   # the gitlink is gone now: the folder still stays out
    assert [p for p in f.paths() if p.startswith(f"extra/{K}/old")] == []
    assert f.head("origin") == f.head("worktree")


def test_a_left_out_folder_whose_name_holds_glob_characters_leaves_out_only_itself(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    nested = f.w / "extra" / K / "old [1]"
    nested.mkdir()
    (nested / ".git").write_text(DEAD)
    (nested / "x.txt").write_text("x\n")
    (f.sp / "old 1").write_text("later\n")
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert f"extra/{K}/old [1]" in f.show("LEFT-OUT.txt").splitlines()
    assert f"extra/{K}/old [1]/x.txt" not in f.paths()
    assert f"extra/{K}/old 1" in f.paths()   # a glob reading of "old [1]" would match the file "old 1" and leave it out too


def test_a_second_run_with_nothing_changed_commits_nothing_and_the_content_is_the_same(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    first = f.head("origin")
    fake = f.tmp / "fakebin"   # a fixed clock: LAST-RUN, git/state.txt and the commit message carry the time
    fake.mkdir()
    (fake / "date").write_text('#!/bin/sh\ncase "$*" in *%Y%m%d*) echo 20260106T000000Z;; *) echo 2026-01-06T00:00:00Z;; esac\n')
    (fake / "date").chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake}{os.pathsep}{os.environ['PATH']}")
    for _ in range(2):
        f.run("--wait")
    changed = git("diff", "--name-only", first, BR, cwd=f.bare).stdout.split()
    assert sorted(changed) == ["LAST-RUN", "git/state.txt"]
    before = f.head("origin")
    f.run("--wait")
    assert f.head("origin") == before and f.head("worktree") == before
    assert f.last_run()[0] == "ok 2026-01-06T00:00:00Z"


def test_a_copy_whose_source_is_gone_is_pruned_only_after_a_pushed_commit_holds_it(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    first = f.head("origin")
    copy = f.w / "extra" / K / "plain.txt"
    (f.sp / "plain.txt").unlink()
    f.break_origin()
    f.run_failing("--wait")
    assert copy.exists(), "pruned although the push failed"
    assert f.last_run()[0].startswith("FAILED ")
    f.mend_origin()
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert not copy.exists()
    assert f"extra/{K}/plain.txt" in f.paths()   # pruned in the worktree; the pushed tip still holds it
    assert "pruned 1 copies" in f.logtext()
    f.run("--wait")
    assert f"extra/{K}/plain.txt" not in f.paths()   # the next run records the removal
    assert git("show", f"{first}:extra/{K}/plain.txt", cwd=f.bare).stdout == "plain\n"
    assert f"extra/{K}/sp ace/y z.txt" in f.paths()


def test_transcripts_git_files_and_a_scratchpad_that_vanished_whole_are_never_pruned(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    other = f.tmp / "other"
    other.mkdir()
    (other / "o.txt").write_text("o\n")
    (f.r / "loop.json").write_text(json.dumps({"sessions": "all", "backup": {"remote": "origin", "extra_dirs": [str(f.sp), str(other)]}}))
    f.run("--wait")
    keep_paths = ["transcripts/subagents__agent-1.jsonl.parts/part-000", "git/untracked/un tracked.txt", "extra/other/o.txt"]
    for p in keep_paths:
        assert p in f.paths()
    f.agent.unlink()
    (f.r / "un tracked.txt").unlink()
    shutil.rmtree(other)
    for _ in range(2):
        f.run("--wait")
        assert OK.match(f.last_run()[0]), f.logtext()
    for p in keep_paths:
        assert p in f.paths()


def test_a_run_without_wait_returns_at_once_and_finishes_in_the_background(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    t = time.monotonic()
    assert keep.main(["backup"]) == 0
    assert time.monotonic() - t < 10
    assert capfd.readouterr() == ("", "")
    end = time.monotonic() + 60
    while time.monotonic() < end:
        if (f.w / "LAST-RUN").exists() and re.match(r"^(ok|FAILED) ", f.last_run()[0]):
            break
        time.sleep(0.2)
    assert OK.match(f.last_run()[0]), f.logtext()
    assert f.head("origin") == f.head("worktree")


def test_a_run_while_another_holds_the_lock_is_skipped_and_changes_nothing(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    before, head = f.last_run(), f.head("origin")
    with open(f.lock, "w") as h:
        fcntl.flock(h, fcntl.LOCK_EX)
        assert keep.main(["backup"]) == 0
        end = time.monotonic() + 20
        while time.monotonic() < end and "skipped" not in f.logtext():
            time.sleep(0.1)
    assert "skipped" in f.logtext()
    assert f.last_run() == before
    assert f.head("origin") == head


def test_the_worktree_is_made_in_the_state_directory_of_the_project(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert str(f.w).startswith(str(f.state) + os.sep)
    assert not (f.r.parent / "backup-wt").exists()


def test_a_scratchpad_that_is_itself_a_repository_has_its_files_copied_without_its_git(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    git("init", "-q", cwd=f.sp)
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert f"extra/{K}/plain.txt" in f.paths()
    assert [p for p in f.paths() if ".git" in p.split("/")] == []
    assert "." in [r.split("\t")[1] for r in f.show("NESTED.tsv").splitlines() if r.startswith(K + "\t")]


def test_a_scratchpad_file_deleted_between_find_and_the_copy_is_no_failure(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    (f.sp / "vanish.txt").write_text("v\n")
    fake = f.tmp / "fakebin"   # a cp that first deletes the source, as a tool's temp file vanishes mid-run
    fake.mkdir()
    real_cp = shutil.which("cp")
    assert real_cp, "no cp on PATH"
    (fake / "cp").write_text(f'#!/bin/sh\nfor a; do case "$a" in */{K}/vanish.txt) rm -f -- "$a";; esac; done\nexec "{real_cp}" "$@"\n')
    (fake / "cp").chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake}{os.pathsep}{os.environ['PATH']}")
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert f"extra/{K}/vanish.txt" not in f.paths()


def test_a_stale_index_lock_in_the_worktree_is_removed_under_the_lock_and_the_run_ends_ok(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    f.run("--wait")
    gd = pathlib.Path(git("rev-parse", "--absolute-git-dir", cwd=f.w).stdout.strip())
    (gd / "index.lock").write_text("")   # a run killed inside git add leaves one
    (f.sp / "after.txt").write_text("after\n")
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert f"extra/{K}/after.txt" in f.paths()
    assert "removed a stale" in f.logtext()


def test_a_snapshot_made_after_its_worktree_was_removed_reaches_a_remote_that_came_back(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    gone = f.tmp / "no-such-origin.git"
    f.break_origin()
    f.run_failing("--wait")   # the branch is made here and its push fails: the local branch exists, the remote has none
    assert git("show-ref", "--verify", "-q", f"refs/heads/{BR}", cwd=f.r, check=False).returncode == 0
    git("worktree", "remove", "--force", str(f.w), cwd=f.r)
    git("init", "-q", "--bare", str(gone), cwd=f.tmp)   # the remote exists now, and still has no backup branch
    f.bare = gone   # the remote the origin names, from here on
    with (f.projects / "-p" / "abcd1234-x.jsonl").open("a", encoding="utf-8") as h:
        h.write('{"turn": 2}\n')
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert f.show("transcripts/-p__abcd1234-x.jsonl.parts/part-000") == '{"turn": 1}\n{"turn": 2}\n'
    assert f.head("origin") == f.head("worktree")


def test_a_worktree_folder_deleted_by_hand_is_made_again_from_the_unpushed_branch(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    gone = f.tmp / "no-such-origin.git"
    f.break_origin()
    f.run_failing("--wait")
    shutil.rmtree(f.w)   # the folder goes; the project's repository still registers the worktree
    git("init", "-q", "--bare", str(gone), cwd=f.tmp)
    f.bare = gone
    f.run("--wait")
    assert OK.match(f.last_run()[0]), f.logtext()
    assert f.head("origin") == f.head("worktree")


def test_a_listing_that_fails_makes_the_copy_step_fail_and_LAST_RUN_names_it(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    fake = f.tmp / "fakebin"   # a find that does all its work and then exits 1, as one that met an unreadable folder does
    fake.mkdir()
    real_find = shutil.which("find")
    assert real_find, "no find on PATH"
    (fake / "find").write_text(f'#!/bin/sh\n"{real_find}" "$@"\nexit 1\n', encoding="utf-8")
    (fake / "find").chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake}{os.pathsep}{os.environ['PATH']}")
    f.run_failing("--wait")
    assert re.match(r"^FAILED \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ: step copy, see " + re.escape(str(f.log)) + "$", f.last_run()[0]), f.last_run()
    assert "step copy" in f.logtext()


def test_a_changed_binary_file_is_in_the_working_patch_as_content_and_git_apply_gives_back_its_bytes(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    before, after = b"\x00\x01binary\x00one\n", b"\x00\x02binary\x00two\xff\n"   # bytes that include NUL
    (f.r / "blob.bin").write_bytes(before)
    git("add", "blob.bin", cwd=f.r)
    git("commit", "-qm", "blob", cwd=f.r)
    (f.r / "blob.bin").write_bytes(after)   # changed, not committed
    f.run("--wait")
    patch = f.show("git/working.patch")
    assert "GIT binary patch" in patch and "Binary files" not in patch, patch
    clean = f.tmp / "clean"   # the project's commit, checked out clean
    git("clone", "-q", str(f.r), str(clean), cwd=f.tmp)
    (f.tmp / "working.patch").write_text(patch, encoding="utf-8")
    git("apply", str(f.tmp / "working.patch"), cwd=clean)
    assert (clean / "blob.bin").read_bytes() == after


def test_a_changed_binary_file_in_a_stash_is_in_its_stash_patch_as_content(tmp_path, monkeypatch, capfd):
    f = Fixture(tmp_path, monkeypatch, capfd)
    (f.r / "blob.bin").write_bytes(b"\x00\x01binary\x00one\n")
    git("add", "blob.bin", cwd=f.r)
    git("commit", "-qm", "blob", cwd=f.r)
    (f.r / "blob.bin").write_bytes(b"\x00\x02binary\x00two\xff\n")
    git("stash", "push", "-q", cwd=f.r)   # the change goes into a stash; the file is back at the commit
    f.run("--wait")
    patch = f.show("git/stash-0.patch")
    assert "GIT binary patch" in patch and "Binary files" not in patch, patch


KIT = pathlib.Path(__file__).resolve().parents[2]
ROOT = "/fake-root/"   # the path prefix the transcripts' files are written under (given to rebuild as --root)


def stamp(sec, ms=0):
    """A transcript timestamp in the form the transcripts use: UTC, milliseconds, Z."""
    return "2026-01-01T00:00:%02d.%03dZ" % (sec, ms)


def tool_use(sec, tid, name, inp):
    return {"type": "assistant", "timestamp": stamp(sec),
            "message": {"role": "assistant", "content": [{"type": "tool_use", "id": tid, "name": name, "input": inp}]}}


def tool_result(sec, tid, content, is_error=False):
    return {"type": "user", "timestamp": stamp(sec, 500),
            "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tid,
                                                     "content": content, "is_error": is_error}]}}


def write_call(sec, tid, path, content, error=False):
    return [tool_use(sec, tid, "Write", {"file_path": path, "content": content}),
            tool_result(sec, tid, "error: refused" if error else "ok", error)]


def edit_call(sec, tid, path, old, new, **extra):
    inp = {"file_path": path, "old_string": old, "new_string": new}
    inp.update(extra)
    return [tool_use(sec, tid, "Edit", inp), tool_result(sec, tid, "ok")]


def read_call(sec, tid, path, content, **extra):
    inp = {"file_path": path}
    inp.update(extra)
    return [tool_use(sec, tid, "Read", inp), tool_result(sec, tid, content)]


def jsonl_file(folder, name, lines):
    """Write lines to folder/name (dicts as JSON, bytes as they are) and return the path."""
    path = os.path.join(folder, name)
    with open(path, "wb") as f:
        for ln in lines:
            f.write(ln if isinstance(ln, bytes) else (json.dumps(ln) + "\n").encode("utf-8"))
    return path


def fresh(tmp_path, name):
    """A new folder under tmp_path and the output folder inside it, not yet created."""
    d = tmp_path / name
    d.mkdir()
    return str(d), str(d / "out")


def rebuild(transcripts, out):
    """Run replay rebuild in-process and return the JSON summary it prints."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert keep.main(["replay", "rebuild", "--transcript", *transcripts, "--out", out, "--root", ROOT]) == 0
    return json.loads(buf.getvalue())


def text_of(out, rel):
    with open(os.path.join(out, rel), encoding="utf-8", newline="") as f:
        return f.read()


def manifest(out):
    """(header, {path: row}) read from MANIFEST.tsv."""
    with open(os.path.join(out, "MANIFEST.tsv"), encoding="utf-8", newline="") as f:
        lines = f.read().split("\n")
    header = lines[0].split("\t")
    rows = {}
    for ln in lines[1:]:
        if ln:
            row = dict(zip(header, ln.split("\t")))
            rows[row["path"]] = row
    return header, rows


def tree(top):
    """Every file and folder under top, relative to top."""
    found = set()
    for d, dirs, files in os.walk(top):
        for name in dirs + files:
            found.add(os.path.relpath(os.path.join(d, name), top))
    return found


def test_a_write_then_edit_with_old_string_present(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "a")
    path = jsonl_file(tmp, "t.jsonl", write_call(1, "w1", "/fake-root/a.md", "one\ntwo\n") + edit_call(3, "e1", "/fake-root/a.md", "two", "2"))
    rebuild([path], out)
    assert text_of(out, "a.md") == "one\n2\n"
    row = manifest(out)[1]["a.md"]
    assert row["latest_source"] == "write+edit"
    assert row["writes"] == "1" and row["full_reads"] == "0" and row["edits_applied"] == "1"
    assert row["edits_not_fitting"] == "0"
    assert row["bytes"] == str(len("one\n2\n"))


def test_b_edit_with_absent_old_string_leaves_text_and_is_counted(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "b")
    path = jsonl_file(tmp, "t.jsonl", write_call(1, "w1", "/fake-root/b.md", "one\ntwo\n") + edit_call(3, "e1", "/fake-root/b.md", "three", "3"))
    rebuild([path], out)
    assert text_of(out, "b.md") == "one\ntwo\n"
    row = manifest(out)[1]["b.md"]
    assert row["edits_not_fitting"] == "1" and row["edits_applied"] == "0" and row["latest_source"] == "write"


def test_c_write_whose_result_is_an_error_is_not_applied(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "c1")
    only = jsonl_file(tmp, "only.jsonl", write_call(1, "w1", "/fake-root/c.md", "lost\n", error=True))
    rebuild([only], out)
    assert not os.path.exists(os.path.join(out, "c.md"))
    assert "c.md" not in manifest(out)[1]
    tmp2, out2 = fresh(tmp_path, "c2")
    after_good = jsonl_file(tmp2, "after.jsonl", write_call(1, "w1", "/fake-root/c.md", "good\n") + write_call(3, "w2", "/fake-root/c.md", "bad\n", error=True))
    rebuild([after_good], out2)
    assert text_of(out2, "c.md") == "good\n"
    row = manifest(out2)[1]["c.md"]
    assert row["writes"] == "1" and row["latest_source"] == "write"


def test_d_edit_replace_all_replaces_every_occurrence_otherwise_the_first_only(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "d")
    path = jsonl_file(tmp, "t.jsonl",
                      write_call(1, "w1", "/fake-root/d1.md", "cat cat dog cat\n")
                      + edit_call(3, "e1", "/fake-root/d1.md", "cat", "bird", replace_all=True)
                      + write_call(5, "w2", "/fake-root/d2.md", "cat cat dog cat\n")
                      + edit_call(7, "e2", "/fake-root/d2.md", "cat", "bird"))
    rebuild([path], out)
    assert text_of(out, "d1.md") == "bird bird dog bird\n"
    assert text_of(out, "d2.md") == "bird cat dog cat\n"
    _, rows = manifest(out)
    assert rows["d1.md"]["edits_applied"] == "1" and rows["d2.md"]["edits_applied"] == "1"


def test_e_full_read_after_a_write_with_other_text_sets_the_text_to_the_read(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    forms = [("tab", "     1\tnew\n     2\tline\n"), ("arrow", "     1→new\n     2→line\n")]
    for n, (form, numbered) in enumerate(forms):
        tmp, out = fresh(tmp_path, f"e{n}")
        path = jsonl_file(tmp, "t.jsonl", write_call(1, "w1", "/fake-root/e.md", "old\n") + read_call(3, "r1", "/fake-root/e.md", numbered))
        rebuild([path], out)
        assert text_of(out, "e.md") == "new\nline\n", form
        row = manifest(out)[1]["e.md"]
        assert row["latest_source"].startswith("read"), row["latest_source"]
        assert row["full_reads"] == "1" and row["writes"] == "1"


def test_f_read_with_offset_or_limit_is_ignored(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "f")
    partial = "     1\tone\n     2\ttwo\n"
    path = jsonl_file(tmp, "t.jsonl", write_call(1, "w1", "/fake-root/f.md", "one\ntwo\nthree\n")
                      + read_call(3, "r1", "/fake-root/f.md", partial, offset=1)
                      + read_call(5, "r2", "/fake-root/f.md", partial, limit=2))
    rebuild([path], out)
    assert text_of(out, "f.md") == "one\ntwo\nthree\n"
    row = manifest(out)[1]["f.md"]
    assert row["full_reads"] == "0" and row["latest_source"] == "write"


def test_g_read_of_2000_or_more_numbered_lines_is_ignored(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))

    def numbered(n):
        return "\n".join("%6d\tline %d" % (i, i) for i in range(1, n + 1))

    for n in (2000, 2500):
        tmp, out = fresh(tmp_path, f"g{n}")
        path = jsonl_file(tmp, "t.jsonl", write_call(1, "w1", "/fake-root/g.md", "keep\n") + read_call(3, "r1", "/fake-root/g.md", numbered(n)))
        rebuild([path], out)
        assert text_of(out, "g.md") == "keep\n"
        assert manifest(out)[1]["g.md"]["full_reads"] == "0"
    tmp, out = fresh(tmp_path, "g1999")   # the boundary: 1999 numbered lines are taken as the whole file
    path = jsonl_file(tmp, "t.jsonl", write_call(1, "w1", "/fake-root/g.md", "keep\n") + read_call(3, "r1", "/fake-root/g.md", numbered(1999)))
    rebuild([path], out)
    assert text_of(out, "g.md") == "".join("line %d\n" % i for i in range(1, 2000))
    row = manifest(out)[1]["g.md"]
    assert row["full_reads"] == "1" and row["latest_source"] == "read"


def test_h_file_path_outside_root_is_ignored(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "h")
    path = jsonl_file(tmp, "t.jsonl", write_call(1, "w1", "/elsewhere/h.md", "nope\n")
                      + write_call(2, "w2", "/fake-root-evil/h.md", "nope too\n")
                      + edit_call(3, "e1", "/elsewhere/h.md", "nope", "yes")
                      + write_call(4, "w3", "/fake-root/inside.md", "in\n"))
    rebuild([path], out)
    written = sorted(os.path.relpath(os.path.join(d, f), out) for d, _, fs in os.walk(out) for f in fs)
    assert written == ["MANIFEST.tsv", "inside.md"]
    assert sorted(manifest(out)[1]) == ["inside.md"]


def test_i_events_are_applied_in_timestamp_order_within_and_across_files(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "i1")   # one file: the Edit at 03 comes before the Write at 02 in the file
    path = jsonl_file(tmp, "t.jsonl", edit_call(3, "e1", "/fake-root/i.md", "b", "c") + write_call(2, "w1", "/fake-root/i.md", "ab\n"))
    rebuild([path], out)
    assert text_of(out, "i.md") == "ac\n"
    row = manifest(out)[1]["i.md"]
    assert row["edits_applied"] == "1" and row["edits_not_fitting"] == "0" and row["latest_source"] == "write+edit"
    tmp2, out2 = fresh(tmp_path, "i2")   # two files: the file with the later Edit is given first
    later = jsonl_file(tmp2, "later.jsonl", edit_call(3, "e1", "/fake-root/i.md", "b", "c"))
    earlier = jsonl_file(tmp2, "earlier.jsonl", write_call(2, "w1", "/fake-root/i.md", "ab\n"))
    rebuild([later, earlier], out2)
    assert text_of(out2, "i.md") == "ac\n"
    assert manifest(out2)[1]["i.md"]["edits_not_fitting"] == "0"


def test_j_manifest_header_and_nothing_written_outside_out(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "j")
    path = jsonl_file(tmp, "t.jsonl", write_call(1, "w1", "/fake-root/j.md", "j\n") + write_call(2, "w2", "/fake-root/sub/k.md", "k\n"))
    before = tree(tmp)
    rebuild([path], out)
    new = tree(tmp) - before
    assert "out" in new
    assert [p for p in new if p != "out" and not p.startswith("out" + os.sep)] == []
    with open(os.path.join(out, "MANIFEST.tsv"), encoding="utf-8", newline="") as f:
        first_line = f.readline()
    assert first_line == "\t".join(keep.MANIFEST_HEADER) + "\n"
    header, rows = manifest(out)
    assert len(header) == 9
    assert sorted(rows) == ["j.md", "sub/k.md"]


def test_k_lines_that_are_not_json_or_are_json_lists_are_skipped(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "k")
    path = jsonl_file(tmp, "t.jsonl", [
        b'{"type": "assistant", "message": {"content": [{"type": "tool_use", BROKEN\n',
        b'["tool_use", "tool_result"]\n',
        b"\n",
        b"not json at all, tool_result\n",
    ] + write_call(1, "w1", "/fake-root/k.md", "valid\n"))
    rebuild([path], out)
    assert text_of(out, "k.md") == "valid\n"
    assert manifest(out)[1]["k.md"]["writes"] == "1"


def test_l_copies_lists_a_named_file_on_the_ref_through_the_entry(tmp_path, monkeypatch, capfd):
    repo = tmp_path / "repo"
    (repo / "tools").mkdir(parents=True)
    (repo / "tools" / "restore.sh").write_text("echo restore\n")
    git("init", "-q", cwd=repo)
    git("add", "-A", cwd=repo)
    git("commit", "-qm", "t", cwd=repo)
    monkeypatch.setenv("LOOP_PROJECT", str(repo))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert keep.main(["replay", "copies", "--ref", "HEAD", "restore.sh"]) == 0
    assert any(ln.endswith("tools/restore.sh") for ln in buf.getvalue().splitlines()), buf.getvalue()
    proc = subprocess.run([sys.executable, "-I", str(KIT / "bin" / "loop"), "keep", "replay", "copies", "--ref", "HEAD", "restore.sh"],
                          capture_output=True, text=True, cwd=str(repo), env={**os.environ, "LOOP_PROJECT": str(repo)})
    assert proc.returncode == 0, proc.stderr
    assert any(ln.endswith("tools/restore.sh") for ln in proc.stdout.splitlines()), proc.stdout


def test_extra_m_long_line_flag_is_cleared_by_a_later_write(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "m")
    long_read = "     1\t" + "x" * 2000 + "\n     2\tend\n"
    path = jsonl_file(tmp, "t.jsonl", write_call(1, "w1", "/fake-root/m.md", "short\n")
                      + read_call(3, "r1", "/fake-root/m.md", long_read)
                      + write_call(5, "w2", "/fake-root/m.md", "fresh\n"))
    rebuild([path], out)
    assert text_of(out, "m.md") == "fresh\n"
    row = manifest(out)[1]["m.md"]
    assert row["latest_source"] == "write" and row["long_line_may_be_cut"] == "0"


def test_extra_n_dotdot_in_file_path_is_not_written_outside_out(tmp_path, monkeypatch):
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    tmp, out = fresh(tmp_path, "n")
    path = jsonl_file(tmp, "t.jsonl", write_call(1, "w1", "/fake-root/../escape.md", "x\n"))
    rebuild([path], out)
    assert not os.path.exists(os.path.join(tmp, "escape.md"))


def test_restore_a_newer_tool_wins(tmp_path, capsys):
    src, dest = tmp_path / "src", tmp_path / "dest"
    (src / "tools").mkdir(parents=True)
    (dest / "tools").mkdir(parents=True)
    (dest / "tools" / "tool.py").write_text("old\n")
    os.utime(dest / "tools" / "tool.py", (1000, 1000))
    (src / "tools" / "tool.py").write_text("new\n")
    os.utime(src / "tools" / "tool.py", (2000, 2000))
    assert keep.main(["restore", str(src), str(dest)]) == 0
    assert (dest / "tools" / "tool.py").read_text() == "new\n"
    assert json.loads(capsys.readouterr().out.strip().splitlines()[-1]) == {"copied": 1, "kept": 0}


def test_restore_an_older_tool_in_src_does_not_overwrite(tmp_path, capsys):
    src, dest = tmp_path / "src", tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    (dest / "tool.sh").write_text("kept\n")
    os.utime(dest / "tool.sh", (2000, 2000))
    (src / "tool.sh").write_text("older\n")
    os.utime(src / "tool.sh", (1000, 1000))
    assert keep.main(["restore", str(src), str(dest)]) == 0
    assert (dest / "tool.sh").read_text() == "kept\n"
    assert json.loads(capsys.readouterr().out.strip().splitlines()[-1]) == {"copied": 0, "kept": 1}


def test_restore_existing_state_is_never_overwritten(tmp_path, capsys):
    src, dest = tmp_path / "src", tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    (dest / "state.json").write_text("mine\n")
    (src / "state.json").write_text("theirs\n")
    os.utime(src / "state.json", (3000, 3000))
    assert keep.main(["restore", str(src), str(dest)]) == 0
    assert (dest / "state.json").read_text() == "mine\n"
    assert json.loads(capsys.readouterr().out.strip().splitlines()[-1]) == {"copied": 0, "kept": 1}


def test_restore_missing_files_are_copied(tmp_path, capsys):
    src, dest = tmp_path / "src", tmp_path / "dest"
    (src / "a").mkdir(parents=True)
    (src / "b").mkdir()
    (src / "a" / "new.txt").write_text("new\n")
    (src / "b" / "c.sh").write_text("echo c\n")
    assert keep.main(["restore", str(src), str(dest)]) == 0
    assert (dest / "a" / "new.txt").read_text() == "new\n"
    assert (dest / "b" / "c.sh").read_text() == "echo c\n"
    assert json.loads(capsys.readouterr().out.strip().splitlines()[-1]) == {"copied": 2, "kept": 0}


def test_restore_a_missing_source_is_a_failure_and_copies_nothing(tmp_path):
    dest = tmp_path / "dest"
    assert keep.main(["restore", str(tmp_path / "nope"), str(dest)]) == 1
    assert not dest.exists()


def test_the_manifest_does_not_follow_a_link_out_of_the_output_folder(tmp_path, monkeypatch):
    """The manifest is written inside --out like every rebuilt file: a MANIFEST.tsv that is already there as a link to a file
    elsewhere is replaced by a regular file, and the file it pointed at is left as it was."""
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    out, victim = tmp_path / "out", tmp_path / "victim.tsv"
    out.mkdir()
    victim.write_text("keep\n", encoding="utf-8")
    os.symlink(victim, out / "MANIFEST.tsv")
    path = jsonl_file(str(tmp_path), "t.jsonl", write_call(1, "w1", "/fake-root/ok.md", "ok\n"))
    assert keep.main(["replay", "rebuild", "--transcript", str(path), "--out", str(out), "--root", ROOT]) == 0
    assert victim.read_text(encoding="utf-8") == "keep\n"
    assert not (out / "MANIFEST.tsv").is_symlink() and (out / "MANIFEST.tsv").read_text(encoding="utf-8").startswith("path\t")
    assert (out / "ok.md").read_text(encoding="utf-8") == "ok\n"
    assert sorted(p.name for p in out.iterdir()) == ["MANIFEST.tsv", "ok.md"]
