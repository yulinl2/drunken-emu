"""One session, end to end, through the real entry: the six verbs close into one loop, for one project and one session.

Each verb has its own tests beside this file. This is the only place where the output of one verb is the input of the next:
what `record` banks is what `gate` resolves a quote against; what `gate` decides is what `hook stop` refuses on and what
`tick` runs; what `keep backup` pushes is what `keep replay` rebuilds from. It is also where a machine is shared: another
project's session, newer than ours, sits in the same transcripts folder and fires the same user-level hooks.

INVARIANT: a message of the principal is banked once and a wait passes the gate only with a chain that resolves in that bank; a stop runs keep and record on the transcript its own event names, is refused while the gate fails and is let through at the cap; a write to a protected branch is denied; the tick runs the due check; a file written outside git comes back from the backup branch alone; nothing of another project's session is banked, backed up, reprinted to or guarded; where no loop.json names a project, nothing is taken or sent.
FAILS WHEN: a step needs a file that no verb of the kit writes; a hook command works only from the project's own directory; a hook acts on the newest transcript of the machine and not on its event's; an install, dry or not, banks or backs up; a process of this test reads or writes the real user settings (every process gets a temporary HOME).
"""
import json, os, pathlib, subprocess, sys, time

KIT = pathlib.Path(__file__).resolve().parents[2]
LOOP = KIT / "bin" / "loop"
METHOD = "Evidence before judgements."
SAID = "Ship nothing that was not tested."
ASKED = "Is the small version enough?"
ELSEWHERE = "Words typed in another project's session."
NOTE = "a note the session wrote outside git\n"
WRITTEN_UNDER = "/fake-root/"
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]


def said(uuid, sec, text):
    return {"type": "user", "uuid": uuid, "timestamp": f"2026-01-01T00:00:{sec:02d}.000Z",
            "message": {"role": "user", "content": text}}


TRANSCRIPT = [
    said("said-1", 1, SAID),
    {"type": "assistant", "uuid": "a-1", "timestamp": "2026-01-01T00:00:02.000Z", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "id": "w-1", "name": "Write", "input": {"file_path": WRITTEN_UNDER + "note.md", "content": NOTE}}]}},
    {"type": "user", "uuid": "r-1", "timestamp": "2026-01-01T00:00:03.000Z", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "w-1", "content": "ok", "is_error": False}]}},
    said("asked-1", 4, ASKED),
]


def tree(root_link):
    """A goal with one wait under it. The wait's chain: the root link given, then a line of the method file."""
    chain = [root_link, {"node": "W", "quote": METHOD, "source": "path:PRINCIPAL-METHOD.md", "fit": "supports",
                         "why": "the method line is what this wait rests on"}]
    wait = {"id": "W", "title": "ask whether the small version is enough", "status": "wait: the principal", "chain": chain,
            "evidence": [["REPRODUCED", "ran it", "here"]], "reproduction_na": "a question to the principal has no artifact"}
    return {"roots": [{"id": "R", "title": "ship only what was tested", "status": "goal", "children": [wait]}]}


def root_link(quote, source):
    return {"node": "R", "quote": quote, "source": source, "fit": "states", "speech_act": "assert", "why": ""}


def wait_for(fn, seconds=90):
    end = time.time() + seconds
    while time.time() < end:
        got = fn()
        if got:
            return got
        time.sleep(0.5)
    return fn()


class Session:
    """A project with a remote, on a machine that another project shares; a transcript under a temporary HOME; and the two
    ways a verb is reached: the entry, and the command a hook registered, run by a shell from another directory with the
    payload the harness sends (the event's own transcript and the session's working directory)."""

    def __init__(self, tmp):
        self.home, self.proj, self.origin, self.away = tmp / "home", tmp / "proj", tmp / "origin.git", tmp / "away"
        self.projects = self.home / ".claude" / "projects"
        for d in (self.projects / "-proj", self.proj, self.away):
            d.mkdir(parents=True)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("LOOP_")}
        self.env["HOME"] = str(self.home)
        assert self.home.resolve().is_relative_to(tmp.resolve())   # never the real settings
        run = lambda *a: subprocess.run(a, check=True, capture_output=True)
        run("git", "init", "-q", "--bare", str(self.origin))
        run("git", "init", "-q", "-b", "main", str(self.proj))
        (self.proj / "PRINCIPAL-METHOD.md").write_text(METHOD + "\n", encoding="utf-8")
        self.config(reread_every=2, backup={"remote": "origin"})
        run(*GIT, "-C", str(self.proj), "add", "-A")
        run(*GIT, "-C", str(self.proj), "commit", "-q", "-m", "start")
        run("git", "-C", str(self.proj), "remote", "add", "origin", str(self.origin))
        self.transcript = self.projects / "-proj" / "session-1.jsonl"
        self.transcript.write_text("".join(json.dumps(r) + "\n" for r in TRANSCRIPT), encoding="utf-8")
        self.settings = self.home / ".claude" / "settings.json"
        self.tree_file = self.proj / "loop-state" / "tree.json"

    def elsewhere(self):
        """Another project's session on the same machine: its transcript is the newest one under the transcripts folder."""
        other = self.projects / "-other" / "other-1.jsonl"
        other.parent.mkdir()
        other.write_text(json.dumps(said("o-1", 9, ELSEWHERE)) + "\n", encoding="utf-8")
        later = time.time() + 60
        os.utime(other, (later, later))
        return other

    def config(self, **keys):
        path = self.proj / "loop.json"
        cfg = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        cfg.update(keys)
        path.write_text(json.dumps(cfg, indent=1), encoding="utf-8")

    def plant(self, link):
        self.tree_file.parent.mkdir(exist_ok=True)
        self.tree_file.write_text(json.dumps(tree(link)), encoding="utf-8")

    def loop(self, *argv, _cwd=None, **env):
        """A verb through the entry, run for this session: the project and the transcript are named, as a hook names them."""
        r = subprocess.run([sys.executable, "-I", str(LOOP), *argv], stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           cwd=str(_cwd or self.away), timeout=300,
                           env={**self.env, "LOOP_PROJECT": str(self.proj), "LOOP_TRANSCRIPT": str(self.transcript), **env})
        return r.returncode, r.stdout, r.stderr

    def event(self, name, **fields):
        groups = json.loads(self.settings.read_text(encoding="utf-8"))["hooks"][name]
        commands = [h["command"] for g in groups for h in g["hooks"]]
        assert len(commands) == 1, (name, commands)
        payload = {"session_id": "session-1", "transcript_path": str(self.transcript), "cwd": str(self.proj),
                   "hook_event_name": name, **fields}
        r = subprocess.run(commands[0], shell=True, input=json.dumps(payload), capture_output=True, text=True,
                           cwd=str(self.away), env=self.env, timeout=300)
        return r.returncode, r.stdout, r.stderr

    def bank(self):
        path = self.proj / "loop-state" / "bank.jsonl"
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()] if path.exists() else []

    def bank_texts(self):
        return sorted(r["text"] for r in self.bank())

    def backups(self):
        refs = subprocess.run(["git", "-C", str(self.origin), "for-each-ref", "--format=%(refname:short)"],
                              capture_output=True, text=True).stdout.split()
        return [r for r in refs if r.startswith("backup/")]

    def backed_up(self):
        """The paths on the backup branches of the remote."""
        return [n for b in self.backups() for n in subprocess.run(
            ["git", "-C", str(self.origin), "ls-tree", "-r", "--name-only", b], capture_output=True, text=True).stdout.split("\n") if n]

    def files(self):
        """Every file of the project (git's own folder apart) and of the home folder."""
        found = []
        for top in (self.proj, self.home):
            for p in top.rglob("*"):
                if p.is_file() and ".git" not in p.relative_to(top).parts:
                    found.append(str(p.relative_to(top.parent)))
        return sorted(found)


def test_one_session_closes_the_loop(tmp_path):
    s = Session(tmp_path)

    # 0. the kit sees the project and all six verbs
    rc, out, err = s.loop("doctor")
    seen = json.loads(out)
    assert rc == 0 and seen["project"] == str(s.proj) and all(seen["verbs_present"].values()), (out, err)

    # 1. hook install: from here on the session's own events call the loop. The install itself takes and sends nothing.
    rc, out, err = s.loop("hook", "install", "--user")
    assert rc == 0, (out, err)
    hooks = json.loads(s.settings.read_text(encoding="utf-8"))["hooks"]
    assert set(hooks) == {"UserPromptSubmit", "PostToolUse", "PreToolUse", "Stop", "PreCompact"}, sorted(hooks)
    assert s.bank() == [] and s.backups() == []

    # 2. a prompt: the principal's method is printed again
    rc, out, err = s.event("UserPromptSubmit", prompt=SAID)
    assert rc == 0 and METHOD in out, (out, err)

    # 3. tool calls: every second one (reread_every is 2) carries the method again
    posts = [s.event("PostToolUse", tool_name="Read") for _ in range(4)]
    assert [rc for rc, _, _ in posts] == [0, 0, 0, 0] and sum(METHOD in o for _, o, _ in posts) == 2, posts

    # 4. guard: a write to the protected branch is denied; a harmless call passes with nothing said
    rc, out, err = s.event("PreToolUse", tool_name="Bash", tool_input={"command": "git push origin main"})
    assert rc == 0 and '"deny"' in out, (out, err)
    rc, out, err = s.event("PreToolUse", tool_name="Bash", tool_input={"command": "git status"})
    assert rc == 0 and out.strip() == "", (out, err)

    # 5. a stop: keep and record run. Both messages are in the bank once each, however often the stop has run, and one
    #    backup branch is on the remote.
    rc, out, err = s.event("Stop")
    assert rc == 0, (out, err)
    assert s.event("Stop")[0] == 0
    assert s.bank_texts() == sorted([SAID, ASKED])
    key = {r["text"]: r["key"] for r in s.bank()}
    assert len(wait_for(s.backups)) == 1, s.backups()

    # 6. gate: the wait passes with a chain whose root is the banked message; a question cited as an assertion fails
    s.plant(root_link(SAID, key[SAID]))
    rc, out, err = s.loop("gate", "check")
    assert rc == 0, (out, err)
    s.plant(root_link(ASKED, key[ASKED]))
    rc, out, err = s.loop("gate", "check")
    report = (s.proj / ".loop" / "chain-gate.json").read_text(encoding="utf-8")
    assert rc == 1 and "question" in report, (out, err, report[:600])

    # 7. the stop is refused while the gate fails, stop_cap times in a row; then it is let through and stays open; one
    #    pass arms it again
    s.config(stop_blocks_on=[["gate", "check"]], stop_cap=2)
    assert [s.event("Stop")[0] for _ in range(4)] == [2, 2, 0, 0]
    s.plant(root_link(SAID, key[SAID]))
    assert s.event("Stop")[0] == 0
    s.plant(root_link(ASKED, key[ASKED]))
    assert s.event("Stop")[0] == 2

    # 8. tick: the due check runs; liveness agrees
    s.plant(root_link(SAID, key[SAID]))
    s.config(checks=[{"name": "gate", "run": ["gate", "check"], "every_s": 60}])
    rc, out, err = s.loop("tick", "run", LOOP_NOW="1000")
    ran = json.loads(out.strip().splitlines()[-1])
    assert rc == 0 and ran["ran"] == "gate" and ran["ok"] is True, (out, err)
    rc, out, err = s.loop("tick", "liveness", LOOP_NOW="1001")
    assert rc == 0 and json.loads(out.strip().splitlines()[-1])["ok"] is True, (out, err)

    # 9. keep: from the backup branch alone, the file the session wrote outside git comes back
    subprocess.run(["git", "-C", str(s.proj), "fetch", "-q", "origin"], check=True, capture_output=True)
    rebuilt = tmp_path / "rebuilt"
    rc, out, err = s.loop("keep", "replay", "rebuild", "--ref", "origin/" + s.backups()[0], "--out", str(rebuilt),
                          "--root", WRITTEN_UNDER)
    assert rc == 0, (out, err)
    assert (rebuilt / "note.md").read_text(encoding="utf-8") == NOTE


def test_a_fresh_project_fails_closed_until_something_is_banked(tmp_path):
    """The joint between record and gate: with no bank the gate names it as missing; after `record bank` the same tree passes.
    And with no remote named, the backup refuses and the prompt says so."""
    s = Session(tmp_path)
    s.plant(root_link(SAID, "said-1"))
    rc, out, err = s.loop("gate", "check")
    assert rc == 1 and "bank.jsonl" in out, (out, err)
    s.config(backup={"remote": ""})
    rc, out, err = s.loop("keep", "backup", "--wait")
    assert rc == 1 and "no remote is named" in err and s.backups() == [], (out, err)
    assert "nothing of this session is kept" in s.loop("hook", "prompt")[1]
    rc, out, err = s.loop("record", "bank")
    assert rc == 0, (out, err)
    rc, out, err = s.loop("gate", "check")
    assert rc == 0, (out, err)


def test_a_failed_backup_reaches_the_next_prompt(tmp_path):
    """The joint between keep and hook: a backup that could not reach its remote is said at the next prompt and shown by
    doctor, not left in a file that nobody opens."""
    s = Session(tmp_path)
    subprocess.run(["git", "-C", str(s.proj), "remote", "set-url", "origin", str(tmp_path / "no-such-remote.git")], check=True)
    rc, out, err = s.loop("keep", "backup", "--wait")
    assert rc == 1 and "FAILED" in err, (out, err)
    rc, out, err = s.loop("hook", "prompt")
    assert rc == 0 and METHOD in out and "the last backup did not succeed" in out, (out, err)
    assert json.loads(s.loop("doctor")[1])["last_backup"].startswith("FAILED")


def test_a_stop_acts_only_on_the_session_that_stopped(tmp_path):
    """A machine is shared: the newest transcript on it belongs to another project, whose session fires the same user-level
    hooks. A stop banks and backs up the transcript its own event names; a session that works outside the project is not
    banked, not backed up, not given this project's method and not guarded by its rules, unless its command names the project."""
    s = Session(tmp_path)
    other = s.elsewhere()
    assert s.loop("hook", "install", "--user")[0] == 0
    assert s.event("Stop")[0] == 0
    assert s.bank_texts() == sorted([SAID, ASKED])
    names = wait_for(s.backed_up)
    assert any("session-1" in n for n in names) and not any("other" in n for n in names), names

    theirs = {"transcript_path": str(other), "cwd": str(s.away)}
    assert s.event("Stop", **theirs)[0] == 0
    assert s.bank_texts() == sorted([SAID, ASKED])
    assert s.event("UserPromptSubmit", **theirs)[1] == ""
    rc, out, err = s.event("PreToolUse", tool_name="Bash", tool_input={"command": "git push origin main"}, **theirs)
    assert rc == 0 and out.strip() == "", (out, err)
    rc, out, err = s.event("PreToolUse", tool_name="Bash", tool_input={"command": f"git -C {s.proj} push origin main"}, **theirs)
    assert rc == 0 and '"deny"' in out, (out, err)

    # a payload that names a transcript and no working directory: the hooks that take data do not act on it; the guard,
    # for which acting is the safe direction, still reads it
    assert s.event("Stop", transcript_path=str(other), cwd="")[0] == 0
    assert s.bank_texts() == sorted([SAID, ASKED]) and not any("other" in n for n in s.backed_up())
    rc, out, err = s.event("PreToolUse", cwd="", tool_name="Bash", tool_input={"command": "git push origin main"})
    assert rc == 0 and '"deny"' in out, (out, err)

    # a verb run with no transcript named takes nothing; only a project that says the whole machine is its own takes the newest
    rc, out, err = s.loop("record", "bank", LOOP_TRANSCRIPT="")
    assert rc == 1 and "no transcript is named" in err, (out, err)
    rc, out, err = s.loop("keep", "backup", "--wait", LOOP_TRANSCRIPT="")
    assert rc == 1 and "no transcript is named" in err, (out, err)
    s.config(sessions="all")
    rc, out, err = s.loop("record", "bank", LOOP_TRANSCRIPT="")
    assert rc == 0 and ELSEWHERE in s.bank_texts(), (out, err)


def test_without_a_loop_json_nothing_is_taken_or_sent(tmp_path):
    """A repository that does not name itself is not a project (the kit's own clone is one such repository): install, bank,
    backup and the hooks refuse, whether the root is given or found from the working directory, and nothing is written."""
    s = Session(tmp_path)
    (s.proj / "loop.json").unlink()
    before = s.files()
    for argv in (["hook", "install", "--user", "--dry-run"], ["hook", "install", "--user"], ["record", "bank"], ["keep", "backup", "--wait"]):
        for found_from_cwd in (False, True):
            rc, out, err = s.loop(*argv, _cwd=s.proj, LOOP_PROJECT="") if found_from_cwd else s.loop(*argv)
            assert rc == 1 and "no project at" in err, (argv, found_from_cwd, out, err)
    for sub in ("post", "stop", "compact"):
        rc, out, err = s.loop("hook", sub)
        assert rc == 0 and "no project at" in err, (sub, out, err)
    assert s.files() == before, sorted(set(s.files()) ^ set(before))


def test_a_dry_run_install_writes_nothing_anywhere(tmp_path):
    """An install tries each command once before it writes. A trial starts the command and nothing more, so a dry run leaves
    no bank, no backup, no counter and no settings file, even in a project that takes every transcript on the machine."""
    s = Session(tmp_path)
    s.elsewhere()
    s.config(sessions="all")
    before = s.files()
    rc, out, err = s.loop("hook", "install", "--user", "--dry-run", LOOP_TRANSCRIPT="")
    assert rc == 0 and '"hooks"' in out, (out, err)
    assert s.files() == before and s.backups() == [], sorted(set(s.files()) ^ set(before))


def test_a_trial_is_marked_in_the_payload_not_in_the_environment(tmp_path):
    """The payload of an install's trial makes a stop do nothing. A variable of that name in a session's environment does
    not: nothing in the environment can switch the loop off with nothing said."""
    s = Session(tmp_path)
    assert s.loop("hook", "install", "--user")[0] == 0
    assert s.event("Stop", loop_trial=True)[0] == 0 and s.bank() == []
    s.env["LOOP_TRIAL"] = "1"
    assert s.event("Stop")[0] == 0 and s.bank_texts() == sorted([SAID, ASKED])


def test_two_sessions_of_one_project_each_keep_their_own_backup(tmp_path):
    """Each session has its own backup branch and its own worktree: the second session's stop succeeds, and neither branch
    holds the other's transcript."""
    s = Session(tmp_path)
    again = "A second session of the same project."
    second = s.projects / "-proj" / "second-2.jsonl"
    second.write_text(json.dumps(said("t-1", 7, again)) + "\n", encoding="utf-8")
    assert s.loop("hook", "install", "--user")[0] == 0

    def ok(sid):
        last = s.proj / ".loop" / f"backup-wt-{sid}" / "LAST-RUN"
        return last.is_file() and last.read_text(encoding="utf-8").startswith("ok")

    def on(branch):
        return subprocess.run(["git", "-C", str(s.origin), "ls-tree", "-r", "--name-only", branch], capture_output=True, text=True).stdout

    assert s.event("Stop")[0] == 0 and wait_for(lambda: ok("session-"))
    assert s.event("Stop", transcript_path=str(second), session_id="second-2")[0] == 0 and wait_for(lambda: ok("second-2"))
    assert sorted(s.backups()) == ["backup/second-2", "backup/session-"]
    assert "session-1" in on("backup/session-") and "second-2" not in on("backup/session-")
    assert "second-2" in on("backup/second-2") and "session-1" not in on("backup/second-2")
    assert again in s.bank_texts()


def test_a_backup_that_cannot_make_its_worktree_still_reaches_the_prompt(tmp_path):
    """LAST-RUN lives in the backup's worktree. In a repository with no commit yet the worktree cannot be made: the failure
    is kept beside it, a waited run returns 1, and the next prompt says so."""
    import shutil
    s = Session(tmp_path)
    shutil.rmtree(s.proj / ".git")
    subprocess.run(["git", "init", "-q", "-b", "main", str(s.proj)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(s.proj), "remote", "add", "origin", str(s.origin)], check=True, capture_output=True)
    rc, out, err = s.loop("keep", "backup", "--wait")
    assert rc == 1 and "FAILED" in err and "no worktree" in err, (out, err)
    assert "the last backup did not succeed" in s.loop("hook", "prompt")[1]
