"""Tests of loop/guard.py: the ported push-guard, artifact-guard and apply-permissions checks, with invented names (alice, project-x, topic-a).
The permission rules here are a fixture, not any project's shipped rules. Every test runs with HOME and LOOP_PROJECT in a temporary directory."""
import contextlib, io, json, os, pathlib, re, subprocess, sys, tempfile, unittest, unittest.mock
KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import guard
LOOP = KIT / "bin" / "loop"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
ISO = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

def repo(branch, upstream=None):
    d = pathlib.Path(tempfile.mkdtemp()); g = lambda *a: subprocess.run(["git", *a], cwd=d, env=ENV, capture_output=True, text=True, check=True)
    g("init", "-q"); g("commit", "-q", "--allow-empty", "-m", "x"); g("checkout", "-q", "-B", branch)
    if upstream: g("config", f"branch.{branch}.remote", "origin"); g("config", f"branch.{branch}.merge", f"refs/heads/{upstream}")
    return str(d)

def write(obj):
    p = pathlib.Path(tempfile.mkdtemp()) / "x.json"; p.write_text(obj if isinstance(obj, str) else json.dumps(obj), encoding="utf-8"); return p

@contextlib.contextmanager
def project(*rows, raw=None, where="loop-state/verdicts.jsonl", protected=None):
    """A temporary project: loop.json with the verdict path (and the protected branches); the verdict rows written to that path."""
    root = pathlib.Path(tempfile.mkdtemp())
    conf = {"sessions": "all", "verdicts": where, **({"protected_branches": protected} if protected else {})}
    (root / "loop.json").write_text(json.dumps(conf), encoding="utf-8")
    if rows or raw is not None:
        f = root / where; f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(raw if raw is not None else "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    with unittest.mock.patch.dict(os.environ, {"LOOP_PROJECT": str(root)}):
        guard._configure(); yield root

def raw_pre(text):
    out, err = io.StringIO(), io.StringIO()
    with unittest.mock.patch("sys.stdin", io.StringIO(text)), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = guard.main(["pre"])
    return code, out.getvalue(), err.getvalue()

def decision(tool, ti, cwd):
    """The hook's printed answer for one call (None when it printed nothing); the exit code must be 0."""
    code, out, err = raw_pre(json.dumps({"tool_name": tool, "tool_input": ti, "cwd": cwd}))
    if code != 0: raise AssertionError(f"exit {code}: {err}")
    return json.loads(out)["hookSpecificOutput"] if out.strip() else None

def hook(tool, ti, cwd):
    """The deny reason for a call; None when it passes. Any answer other than a deny fails."""
    o = decision(tool, ti, cwd)
    if o is None: return None
    assert o["hookEventName"] == "PreToolUse" and o["permissionDecision"] == "deny", o
    return o["permissionDecisionReason"]

class Base(unittest.TestCase):
    def setUp(self):
        self.home = pathlib.Path(tempfile.mkdtemp())
        p = unittest.mock.patch.dict(os.environ, {"LOOP_PROJECT": str(self.home), "HOME": str(self.home)}); p.start(); self.addCleanup(p.stop)
        # these tests model a machine whose every session is the project's: their payloads work in a clone outside the project root
        (self.home / "loop.json").write_text(json.dumps({"sessions": "all"}), encoding="utf-8")
        guard._configure()

STOP = ["git push -vf origin topic-b", "git push origin -qd topic-b", "git push --force origin x", "git push -f", "git push origin +x", "git push origin :x", "git push origin HEAD:main", "git push origin HEAD:refs/heads/main",
        "git push origin main", "git push origin refs/heads/master", "git push origin x:refs/heads/main", "git push --all", "git push --mirror", "git push --prune origin", "git push --delete origin x", "git push --force-with-lease origin x",
        "git -C nowhere push -f origin y", "git -c user.name=t push -f origin y", "bash -c 'git push -f origin y'", 'sh -c "cd nowhere && git push origin main"', 'git push origin "$B"', "git push origin $(git branch --show-current)",
        "git commit -qm x && git push -uf origin x", "echo hi; git push -vf origin x", "FOO=1 git push -vf origin x", "git push origin 'unclosed", "git fetch -q && git push -u origin x --delete",
        "git push --dele origin topic-b", "git push --forc origin x", "git push --mirr", "git push --pru origin", "git push --al",
        "bash -lc 'git push origin :x'", "sh -ec 'git push -f origin x'", "bash -o errexit -c 'git push -f origin x'", "zsh -xc 'git push origin main'",
        "git push origin 'refs/heads/*:refs/heads/*'", "git push origin '+refs/heads/*:refs/heads/*'",
        "env -i git push origin :x", "sudo -u deploy git push -f origin x", "nice -n 5 git push -f origin x", "sudo -u u bash -lc 'git push origin :x'",
        "eval 'git push origin :x'", "eval git push -f origin x", "echo :x | xargs git push origin", "xargs -I{} git push origin {}",
        "if true; then git push -f origin x; fi", "{ git push -f origin x; }", "! git push -f origin x", "while true; do git push -f origin x; done", "echo `git push origin :x`", "`git push -f origin x`",
        "git -c alias.p=push p origin :x", "git -c 'alias.p=push -f' p origin x",
        "python3 -I - <<'PY'\nprint('git push -f origin main')\nPY\ngit status -sb", "cat <<EOF | bash\ngh pr merge 5\nEOF", "python3 -c \"import subprocess; subprocess.run(['git', 'push', 'origin', 'main'])\"", "python3.12 -Ic 'import os; os.system(\"gh api -X PUT x\")'",
        "tools/git push -f origin x", "env tools/git push origin :x",
        "gh pr merge 5", "gh pr merge --auto --squash 5 -R o/r", "gh pr -R o/r merge 5", "bash -c 'gh pr merge 5'", "xargs gh pr merge", "env GH_TOKEN=x gh pr merge 5",
        "gh api -X PUT repos/o/r/pulls/1/merge", "gh api repos/o/r/git/refs/heads/x -X DELETE", "gh api --method DELETE repos/o/r/rulesets/1", "gh api --method=PATCH repos/o/r", "gh api -XPOST repos/o/r/issues", "gh api -X=POST x",
        "gh api repos/o/r/issues -f title=x", "gh api repos/o/r/issues -F n=1", "gh api graphql -f query=q", "gh api repos/o/r/issues --field a=b", "gh api repos/o/r/issues --raw-field a=b", "gh api x --input body.json", "gh api -ftitle=x repos/o/r/issues",
        "gh api -iX POST repos/o/r/issues", "gh api -H 'Accept: x' -X POST repos/o/r/issues", "gh api -X", "xargs gh api repos/o/r/issues",
        "gh repo edit o/r --visibility private", "bash -lc 'gh repo edit o/r --default-branch x'",
        "timeout 60 git push origin HEAD:main", "timeout -k 5 60 git push -f origin x", "timeout 60 git push origin :topic-old", "timeout 60 git push --delete origin topic-old", "timeout 60 git push --mirror origin", "timeout 5 bash -c 'git push origin HEAD:main'", "timeout 5 sh -c 'git push -f origin x'", "timeout 9 git push origin $B",
        "stdbuf -oL git push origin HEAD:main", "setsid git push -f origin x", "ionice -c3 git push origin :x", "flock lockfile git push --delete origin x", "timeout 30 gh api -X PATCH repos/o/r/git/refs/heads/main -f sha=x", "timeout 30 gh api -X PATCH repos/o/r/git/refs/heads/main -f sha=x -f force=true",
        "# push the reviewed head\ngit push origin HEAD:main", "git status # check first\ngit push origin :topic-old", "git push origin \\\n  HEAD:main", "git push origin topic-old \\\n  --force", "gh api repos/o/r/git/refs/heads/main \\\n  -X PATCH -f sha=x",
        "timeout 60 tools/git push origin HEAD:main", "sudo -u x tools/git push -f origin x", "tools/env git push origin :x", "timeout 5 tools/bash -c 'git push origin HEAD:main'",
        'out="$(git push origin HEAD:main 2>&1)"; echo "$out"', 'echo "$(git push -f origin x)"', "echo '$(git push -f origin x)'", 'git commit -qm "reads \\$(git push -f origin x) as text"',
        'msg="$(git push origin HEAD:main 2>&1 || echo "push failed (rc $?)")"', "echo \"$(git push -f origin x 2>&1 | grep -E '(rejected|error)')\"", 'out="$(git push origin "$(git rev-parse HEAD)":refs/heads/main 2>&1)"', 'echo "$( (git push --delete origin topic-old) 2>&1)"', "out=`git push origin HEAD:main`",
        "# push the reviewed head \\\ngit push origin HEAD:main", "git status # check \\\ngit push -f origin x", "echo foo#bar; git push origin HEAD:main", "[ ${#h} -eq 40 ] && git push -f origin x",
        "bash -c 'git push origin \\\n  HEAD:main'", "timeout 60 bash -c 'git push origin \\\n  HEAD:main'", "eval 'git push origin \\\n  HEAD:main'", "sh -c 'git push origin \\\n  :topic-old'", "eval 'git push \\\n  --force origin x'", "bash -c 'bash -c \"git push origin \\\n  HEAD:main\"'",
        "echo \"$(echo ')'; git push -f origin x)\"", "echo \"$(grep -c ')' f; git push --delete origin topic-old)\"", 'echo "$(echo \\); git push -f origin x)"']
GH_OK = ["gh api repos/o/r/pulls/5", "gh api -X GET repos/o/r/issues", "gh api --method GET repos/o/r", "gh api --method=get repos/o/r", "gh api -XGET x", "gh api -H 'Accept: application/json' -q .name repos/o/r", "gh api -i repos/o/r", "gh api --paginate repos/o/r/pulls",
         "gh pr view 5", "gh pr list", "gh pr create --title x --body y", "gh pr comment 5 -b 'ready to merge'", "gh repo view o/r", "gh issue list", "python3 -c 'print(1)'", "python3 -m tool.deck x", "python3 -I bin/build_tool.py", "python3 -c 'print(\"gh is a word\")'"]
OK = ["git push -q -u origin topic-d", "cd sub && git fetch -q origin && git push -q -u origin topic-d 2>&1 | tail -2", "git push -n origin topic-b", "git push --dry-run origin topic-b",
      "git push origin topic-b:topic-b", "git push origin main:topic-backup", "git push origin topic-b topic-c", "git push -u origin HEAD", "git push", "git push origin",
      "echo 'git push -f origin main'", "git commit -q -m 'git push -vf is flagged'", "git log --oneline | head -3",
      "git pull origin main", "git fetch origin main", "git merge origin/main", "git branch -d topic-old", "git diff --stat origin/main...HEAD", "",
      "git push --set-upstream origin topic-b", "git push --no-verify origin topic-b", "git push --porcelain origin topic-b", "git push --atomic origin topic-b", "git push --follow-tags origin topic-b", "git push --tags origin",
      "bash -lc 'git status'", "bash -c 'ls'", "bash script.sh", "sh -c 'echo git push -f origin main'",
      "env -i git status", "sudo -u deploy git status", "eval 'echo hi'", "echo :x | xargs echo", "if true; then git status; fi", "{ echo hi; }", "echo `date`", "git -c alias.s=status s", "git status", "git commit -qm 'xargs git push'",
      "echo start # ; git push origin HEAD:main", "# a note about git push -f\ngit status", "git status # a note \\\necho next", 'echo "${#PATH}" $#', "git log --grep=#41 -1",
      "bash -c 'git status \\\n  -sb'", 'echo "$(echo \')\'; echo ok)"',
      'echo "$(git status)"', 'branch=$(git rev-parse --abbrev-ref HEAD); echo "$branch"', 'git log --oneline "$(git merge-base HEAD origin/main)"..HEAD', *GH_OK]

class PushGuard(Base):
    def setUp(self):
        super().setUp()      # the source's protected set, main and master, which is also the package default
        (self.home / "loop.json").write_text(json.dumps({"sessions": "all", "protected_branches": ["main", "master"]}), encoding="utf-8"); guard._configure()
    @classmethod
    def setUpClass(cls):
        cls.feature, cls.on_main, cls.tracks_main, cls.tracks_self = repo("topic-a"), repo("main", "main"), repo("topic-b", "main"), repo("topic-c", "topic-c")
    def test_risky_calls_are_held(self):
        for c in STOP: self.assertTrue(guard.decide(c, self.feature), c)
    def test_ordinary_pushes_and_other_commands_say_nothing(self):
        for c in OK: self.assertEqual(guard.decide(c, self.feature), [], c)
    def test_an_implied_destination_is_held_only_when_it_is_main(self):
        for c in ("git push", "git push origin", "git push origin HEAD", "git push -u origin HEAD", "timeout 60 git push", "flock lockfile git push origin HEAD"):
            self.assertTrue(guard.decide(c, self.on_main), c); self.assertTrue(guard.decide(c, self.tracks_main), c)
            self.assertEqual(guard.decide(c, self.feature), [], c); self.assertEqual(guard.decide(c, self.tracks_self), [], c)
        self.assertTrue(guard.decide(f"cd {self.on_main} && git push", self.feature)); self.assertTrue(guard.decide(f"git -C {self.on_main} push origin HEAD", self.feature))
    def test_configured_destinations_are_held_when_no_refspec_names_the_branch(self):
        up = [("remote.upstream.push", "HEAD:main"), ("branch.topic-a.pushRemote", "upstream")]
        cases = [([("remote.origin.push", "HEAD:refs/heads/main")], "git push origin", True), ([("remote.origin.push", "HEAD:refs/heads/main")], "git push", True),
                 ([("remote.origin.push", "HEAD:refs/heads/main")], "git push origin topic-a", False),      # a refspec on the command line overrides the configuration
                 ([("remote.origin.push", "refs/heads/*:refs/heads/*")], "git push origin", True), ([("remote.origin.push", "HEAD:refs/heads/topic-a")], "git push origin", False),
                 ([("remote.origin.mirror", "true")], "git push origin", True), ([("push.default", "matching")], "git push origin", True), ([("push.default", "matching")], "git push origin topic-a", False),
                 ([("push.default", "current")], "git push origin", False), (up, "git push", True), (up, "git push origin", False), ([("remote.pushDefault", "upstream"), ("remote.upstream.push", "HEAD:main")], "git push", True)]
        for config, cmd, asks in cases:
            d = repo("topic-a")
            for k, v in config: subprocess.run(["git", "config", k, v], cwd=d, check=True)
            self.assertEqual(bool(guard.decide(cmd, d)), asks, (config, cmd))
    def test_a_git_alias_for_push_is_read_from_the_configuration(self):
        cases = [([("alias.p", "push")], "git p origin :x", True), ([("alias.p", "push")], "git p origin topic-a", False), ([("alias.p", "push -f")], "git p origin x", True), ([("alias.q", "!git push origin :x")], "git q", True),
                 ([("alias.st", "status")], "git st", False), ([("alias.p", "push")], "git status", False)]
        for config, cmd, asks in cases:
            d = repo("topic-a")
            for k, v in config: subprocess.run(["git", "config", k, v], cwd=d, check=True)
            self.assertEqual(bool(guard.decide(cmd, d)), asks, (config, cmd))
    def test_what_really_changes_a_remote_is_held(self):
        """Each spelling runs against a local bare remote: where git deleted a branch or moved main, the guard must have held it; an ordinary push must not."""
        env = {**ENV, **ISO}
        def sh(wd, *a): return subprocess.run(["git", *a], cwd=wd, env=env, capture_output=True, text=True, check=True).stdout.strip()
        def pair(config, advance):
            t = pathlib.Path(tempfile.mkdtemp()); bare, w = t / "r.git", t / "w"; sh(t, "init", "-q", "--bare", "-b", "main", str(bare)); sh(t, "clone", "-q", str(bare), str(w))
            sh(w, "checkout", "-q", "-b", "main"); (w / "a").write_text("1"); sh(w, "add", "a"); sh(w, "commit", "-q", "-m", "m1"); sh(w, "push", "-q", "-u", "origin", "main"); sh(w, "branch", "topic"); sh(w, "push", "-q", "origin", "topic")
            sh(w, "checkout", "-q", "-b", "feat"); (w / "b").write_text("2"); sh(w, "add", "b"); sh(w, "commit", "-q", "-m", "f1")
            if advance: sh(w, "checkout", "-q", "main"); (w / "c").write_text("3"); sh(w, "add", "c"); sh(w, "commit", "-q", "-m", "m2"); sh(w, "checkout", "-q", "feat")
            for k, v in config: sh(w, "config", k, v)
            return bare, w
        refs = lambda bare: dict(l.split("=") for l in sh(bare, "for-each-ref", "--format=%(refname:short)=%(objectname)", "refs/heads").split("\n"))
        mainhead = [("remote.origin.push", "HEAD:refs/heads/main")]
        cases = [("git push --delete origin topic", (), False, True), ("git push --dele origin topic", (), False, True), ("bash -lc 'git push origin :topic'", (), False, True), ("git push origin", mainhead, False, True),
                 ("git push origin", [("push.default", "matching")], True, True), ("git push origin 'refs/heads/*:refs/heads/*'", (), True, True), ("env -i git push origin :topic", (), False, True), ("eval 'git push origin :topic'", (), False, True), ("echo :topic | xargs git push origin", (), False, True),
                 ("git -c alias.p=push p origin :topic", (), False, True), ("if true; then git push origin :topic; fi", (), False, True), ("echo `git push origin :topic`", (), False, True),
                 ("git push origin feat", (), False, False), ("git push -u origin feat", (), False, False)]
        with unittest.mock.patch.dict(os.environ, ISO):
            for cmd, config, advance, dangerous in cases:
                bare, w = pair(config, advance); before = refs(bare); asked = bool(guard.decide(cmd, str(w)))
                subprocess.run(cmd, shell=True, cwd=w, env=env, capture_output=True); after = refs(bare)
                did = any(k not in after for k in before) or after["main"] != before["main"]
                self.assertEqual(did, dangerous, ("git did not behave as the case assumes", cmd, before, after)); self.assertEqual(asked, dangerous, cmd)
    def test_the_hook_prints_deny_json_for_a_risky_push_and_nothing_otherwise(self):
        def run(cmd): return subprocess.run([sys.executable, "-I", str(LOOP), "guard", "pre"], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": self.feature}), capture_output=True, text=True, env=os.environ)
        r = run("git push -vf origin topic-b"); self.assertEqual(r.returncode, 0, r.stderr); o = json.loads(r.stdout)["hookSpecificOutput"]
        self.assertEqual(o["permissionDecision"], "deny"); self.assertIn("-vf", o["permissionDecisionReason"]); self.assertNotIn("owner", o["permissionDecisionReason"])
        for c in ("git push -q -u origin topic-d", "ls -la", ""): r = run(c); self.assertEqual((r.returncode, r.stdout.strip()), (0, ""), c)
        for bad in ("", "{not json", "[]", "null"):
            r = subprocess.run([sys.executable, "-I", str(LOOP), "guard", "pre"], input=bad, capture_output=True, text=True, env=os.environ)
            self.assertEqual((r.returncode, r.stdout), (0, ""), bad)
        self.assertIn("guard pre:", subprocess.run([sys.executable, "-I", str(LOOP), "guard", "pre"], input="{not json", capture_output=True, text=True, env=os.environ).stderr)
    def test_a_heredoc_that_says_git_and_much_later_push_is_not_a_mention_but_a_near_one_is(self):
        far = "Use git for the history.\n" + "x" * 200 + "\nWe push on Friday.\n"
        self.assertEqual(guard.decide(f"git commit -q -F - <<'EOF'\n{far}EOF", self.feature), [])
        self.assertTrue(guard.decide("git commit -q -F - <<'EOF'\nrun git push later\nEOF", self.feature)); self.assertTrue(guard.decide("python3 - <<'PY'\nrun(['git',\n  'push'])\nPY", self.feature))
        self.assertTrue(guard.decide("python3 -c \"run(['gh',\n 'pr', 'merge'])\"", self.feature)); self.assertTrue(guard.decide("git commit -m 'unclosed git" + " " * 200 + "push", self.feature))
    def test_a_hook_input_without_a_tool_name_is_read_as_bash(self):
        code, out, _ = raw_pre(json.dumps({"tool_input": {"command": "git push -f origin x"}, "cwd": self.feature}))
        self.assertEqual(code, 0); self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], "deny")

H1, H2, BASE = "a" * 39 + "1", "b" * 39 + "2", "c" * 40
def merge_row(**kw): return {"id": "v-0001", "at": "2026-01-01T00:00:00Z", "by": "advisor example", "answer": "advisor-answers/example.md", "repo": "alice/project-x", "kind": "merge", "pr": 7, "head": H1, "base": BASE, "tree": BASE, "tests": "12 OK", "verdict": "go", "undo": "git revert -m 1 <merge sha>", **kw}
LEASE_CMD = f"git push --force-with-lease=topic-old:{H1} origin :topic-old"
def cmd_row(command, **kw): return {"id": "v-0002", "at": "2026-01-01T00:10:00Z", "by": "reviewer https://example.invalid/review", "answer": "advisor-answers/example-2.md", "repo": "alice/project-x", "kind": "command", "command": command, "verdict": "go", "undo": f"git push origin {H1}:refs/heads/topic-old", **kw}
def merge_call(**kw): return {"owner": "alice", "repo": "project-x", "pullNumber": 7, "merge_method": "merge", "expectedHeadSha": H1, "commit_title": "Merge #7", "commit_message": "Advisor-verdict: v-0001", **kw}
MERGE = "mcp__github__merge_pull_request"

class Verdicts(Base):
    """A risky call is denied with no verdict, passes with the matching one, and is denied with a verdict for something else (another SHA, PR, repo or command)."""
    @classmethod
    def setUpClass(cls):
        cls.feature, cls.on_main = repo("topic-a"), repo("main", "main")
    def test_a_merge_is_denied_with_no_verdict_and_passes_with_the_matching_one(self):
        f = self.feature
        with project(): self.assertIn("no go verdict", hook(MERGE, merge_call(), f))
        with project(raw=""): self.assertIn("no go verdict", hook(MERGE, merge_call(), f))
        with project(merge_row()): self.assertIsNone(hook(MERGE, merge_call(), f)); self.assertIsNone(hook(MERGE, merge_call(owner="ALICE", repo="PROJECT-X", expectedHeadSha=H1.upper()), f))
        with project(merge_row(pr="7")): self.assertIsNone(hook(MERGE, merge_call(pullNumber=7.0), f))
    def test_a_merge_is_denied_with_a_verdict_for_another_sha_pr_repo_or_kind(self):
        f = self.feature
        with project(merge_row()):
            why = hook(MERGE, merge_call(expectedHeadSha=H2), f); self.assertIn("head", why); self.assertIn(H1[:7], why); self.assertIn(H2[:7], why)
            self.assertIn("no go verdict", hook(MERGE, merge_call(pullNumber=62), f)); self.assertIn("no go verdict", hook(MERGE, merge_call(repo="other"), f))
        with project(merge_row(head=H2)): self.assertIn("head", hook(MERGE, merge_call(), f))
        with project(cmd_row("gh pr merge 7", pr=7, head=H1)): self.assertIn("no go verdict", hook(MERGE, merge_call(), f))
    def test_a_merge_needs_the_method_the_sha_and_the_verdict_id_in_the_message(self):
        f = self.feature
        with project(merge_row()):
            self.assertIn("merge_method", hook(MERGE, merge_call(merge_method="squash"), f)); self.assertIn("merge_method", hook(MERGE, {k: v for k, v in merge_call().items() if k != "merge_method"}, f))
            for bad in (None, "", "abc", H1[:7], H1 + "0"): self.assertIn("expectedHeadSha", hook(MERGE, merge_call(expectedHeadSha=bad), f), bad)
            self.assertIn("verdict id", hook(MERGE, merge_call(commit_message="no id here"), f)); self.assertIn("verdict id", hook(MERGE, {k: v for k, v in merge_call().items() if k != "commit_message"}, f))
    def test_a_verdict_that_is_not_a_go_or_is_incomplete_or_withdrawn_does_not_count(self):
        f = self.feature; withdrawn = {"id": "w1", "verdict": "withdrawn", "of": merge_row()["id"]}
        for rows, raw in (([merge_row(verdict="no-go")], None), ([merge_row(), withdrawn], None), ([merge_row(undo="")], None), ([{k: v for k, v in merge_row().items() if k != "by"}], None), ([{k: v for k, v in merge_row().items() if k != "answer"}], None), ([], "{not json\n[1]\n")):
            with project(*rows, raw=raw): self.assertIn("no go verdict", hook(MERGE, merge_call(), f), (rows, raw))
        with project(merge_row(), {"id": "w1", "verdict": "withdrawn", "of": "another-id"}): self.assertIsNone(hook(MERGE, merge_call(), f))
        with project(raw="{not json\n" + json.dumps(merge_row()) + "\n"): self.assertIsNone(hook(MERGE, merge_call(), f))      # a broken line is skipped, it cannot grant anything
    def test_files_pushed_through_the_api_are_denied_on_main_and_master_only(self):
        f = self.feature
        with project(protected=["main", "master"]):
            for tool in ("push_files", "create_or_update_file", "delete_file"):
                for branch in ("main", "master", "refs/heads/main", " main"): self.assertIn("merge through a PR", hook("mcp__github__" + tool, {"owner": "alice", "repo": "project-x", "branch": branch, "message": "m", "path": "p"}, f), (tool, branch))
                for ti in ({"owner": "alice", "repo": "project-x", "message": "m"}, {"owner": "alice", "repo": "project-x", "branch": ""}): self.assertIn("default branch", hook("mcp__github__" + tool, ti, f), (tool, ti))
                for branch in ("topic-a", "main-2", "domain-x", "refs/heads/topic/main"): self.assertIsNone(hook("mcp__github__" + tool, {"owner": "alice", "repo": "project-x", "branch": branch, "message": "m", "path": "p"}, f), (tool, branch))
    def test_a_push_to_main_is_denied_even_with_a_verdict_for_that_exact_command(self):
        f = self.feature
        for cmd, wd in (("git push origin main", f), ("git push origin HEAD", self.on_main), ("git push -f origin HEAD:main", f), (f"git push --force-with-lease=main:{H1} origin :main", f), ("git push --mirror", f), ("gh pr merge 5", f)):
            with project(): self.assertIsNotNone(hook("Bash", {"command": cmd}, wd), cmd)
            with project(cmd_row(cmd)): self.assertIsNotNone(hook("Bash", {"command": cmd}, wd), cmd)
        with project(): self.assertIn("merge through a PR", hook("Bash", {"command": "git push origin main"}, f))
    def test_a_fast_forward_push_of_a_verdict_head_to_main_passes_and_no_other_push_to_main_does(self):
        f = self.feature; ff = f"git push origin {H1}:refs/heads/main"
        with project(): self.assertIn("no go verdict of kind merge", hook("Bash", {"command": ff}, f))
        with project(): self.assertIsNotNone(hook("Bash", {"command": f"timeout 60 git push origin {H1}:refs/heads/main"}, f))
        with project(merge_row()):
            for c in (ff, f"git push origin {H1}:main", f"git -C {f} push origin {H1}:refs/heads/main", f"git push -q origin {H1}:refs/heads/main", f"timeout 60 git push origin {H1}:refs/heads/main"):
                self.assertIsNone(hook("Bash", {"command": c}, f), c)
            for c in (f"git push origin {H2}:refs/heads/main", f"git push origin +{H1}:main", f"git push -f origin {H1}:main", f"git push --force-with-lease=main:{BASE} origin {H1}:main",
                      f"git push origin {H1[:12]}:main", f"git push origin {H1.upper()}:main", "git push origin main", "git push origin HEAD:main", f"git push origin {H1}:main && gh api -X POST repos/alice/project-x/issues"):
                self.assertIsNotNone(hook("Bash", {"command": c}, f), c)
            for c in (f"git push origin {H1}:refs/heads/main \\\n  -f", f"git push origin {H1}:refs/heads/main # ok\ngit push origin :topic-x"): self.assertIsNotNone(hook("Bash", {"command": c}, f), c)
            self.assertIsNotNone(hook("Bash", {"command": "git push origin HEAD"}, self.on_main))
        for row in (merge_row(verdict="go-conditional"), merge_row(undo=""), cmd_row(ff)):
            with project(row): self.assertIsNotNone(hook("Bash", {"command": ff}, f), row)
    def test_a_wrapper_with_arguments_of_its_own_does_not_change_what_the_guard_decides(self):
        """timeout, stdbuf, setsid, ionice and flock are looked through, with their own arguments: each wrapped call is judged exactly as the bare one."""
        f = self.feature; ff = f"git push origin {H1}:refs/heads/main"
        cases = [(ff, True, False), (f"bash -c '{ff}'", True, False), ("git push origin HEAD:main", True, True), ("git push -f origin x", True, True), ("git push origin :topic-x", True, True), ("git push --delete origin topic-x", True, True), ("git push --mirror origin", True, True),
                 ("sh -c 'git push -f origin x'", True, True), ("gh api -X PATCH repos/o/r/git/refs/heads/main -f sha=x -f force=true", True, True), ("git push origin topic-x", False, False), ("git status", False, False)]      # (command, denied with no verdict, denied with a go row for H1)
        for rows, col in (((), 1), ((merge_row(),), 2)):
            with project(*rows):
                for w in ("timeout 60", "timeout -k 5 60", "timeout --kill-after=5 60", "stdbuf -oL", "setsid", "ionice -c3", "flock lockfile", "timeout 5 nice -n 5"):
                    for case in cases:
                        got = hook("Bash", {"command": f"{w} {case[0]}"}, f); self.assertEqual(got is not None, case[col], (w, case[0], bool(rows)))
                        self.assertEqual(got, hook("Bash", {"command": case[0]}, f), (w, case[0], bool(rows)))
    def test_a_force_or_delete_push_needs_a_command_verdict_for_the_whole_string_and_a_lease(self):
        f = self.feature
        with project(): self.assertIn("no command verdict", hook("Bash", {"command": LEASE_CMD}, f))
        with project(cmd_row(LEASE_CMD)):
            self.assertIsNone(hook("Bash", {"command": LEASE_CMD}, f)); self.assertIsNone(hook("Bash", {"command": LEASE_CMD + "  "}, f))
            other = LEASE_CMD.replace(H1, H2); self.assertIn("no command verdict", hook("Bash", {"command": other}, f))
            self.assertIn("among its own arguments", hook("Bash", {"command": LEASE_CMD + " && git push origin :topic-other"}, f)); self.assertIn("no command verdict", hook("Bash", {"command": LEASE_CMD + " && git push --force-with-lease=topic-other:" + "b" * 40 + " origin :topic-other"}, f))
            self.assertIn("no command verdict", hook("Bash", {"command": "echo x; " + LEASE_CMD}, f))
        plain = "git push origin --delete topic-old"
        with project(cmd_row(plain)): self.assertIn("--force-with-lease=<ref>:<40 hex sha>", hook("Bash", {"command": plain}, f))
        for lease in ("--force-with-lease", "--force-with-lease=topic-old", f"--force-with-lease=topic-old:{H1[:12]}", f"--force-with-lease=topic-old:{H1}0"):
            c = f"git push {lease} origin :topic-old"
            with project(cmd_row(c)): self.assertIn("--force-with-lease", hook("Bash", {"command": c}, f), lease)
        with project(cmd_row(LEASE_CMD, kind="merge", pr=1, head=H1)): self.assertIn("no command verdict", hook("Bash", {"command": LEASE_CMD}, f))
    def test_gh_writes_need_a_command_verdict_for_the_whole_string(self):
        f = self.feature
        for cmd in ("gh api -X PUT repos/alice/project-x/rulesets/1 -f enforcement=active", "gh api repos/alice/project-x/issues -f title=x", "gh repo edit alice/project-x --default-branch x", "bash -c 'gh api -X DELETE repos/alice/project-x/git/refs/heads/topic-old'"):
            with project(): self.assertIn("no command verdict", hook("Bash", {"command": cmd}, f), cmd)
            with project(cmd_row(cmd)): self.assertIsNone(hook("Bash", {"command": cmd}, f), cmd)
            with project(cmd_row(cmd + " --extra")): self.assertIn("no command verdict", hook("Bash", {"command": cmd}, f), cmd)
        with project(): self.assertIsNone(hook("Bash", {"command": "gh api repos/alice/project-x/pulls/7 -q .head.sha"}, f))
    def test_the_verdict_file_is_the_configured_one_only(self):
        """The file is the one loop.json names (default loop-state/verdicts.jsonl); a file at the default place is not read when another place is configured."""
        with project(where="evidence/verdicts.jsonl") as root:
            (root / "loop-state").mkdir(); (root / "loop-state" / "verdicts.jsonl").write_text(json.dumps(merge_row()) + "\n", encoding="utf-8")
            self.assertIn("no go verdict", hook(MERGE, merge_call(), self.feature))
    def test_a_failure_denies_a_call_that_mentions_push_merge_or_api(self):
        f = self.feature
        with project() as root:
            (root / "loop-state" / "verdicts.jsonl").mkdir(parents=True)          # a verdict path that cannot be read
            self.assertIn("guard failed", hook(MERGE, merge_call(), f)); self.assertIn("guard failed", hook("Bash", {"command": LEASE_CMD}, f)); self.assertIn("guard failed", hook("Bash", {"command": "gh api -X POST x"}, f)); self.assertIn("guard failed", hook("Bash", {"command": "gh repo edit alice/project-x"}, f))
            self.assertIsNone(hook("Bash", {"command": "git status"}, f)); self.assertIsNone(hook("Bash", {"command": "git push -u origin topic-a"}, f))
        with project():
            with unittest.mock.patch.object(guard, "decide", side_effect=RuntimeError("boom")):
                for cmd in ("git push origin topic-b", "git merge x", "gh api repos/alice/project-x"): self.assertIn("guard failed", hook("Bash", {"command": cmd}, f), cmd)
                code, out, err = raw_pre(json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}, "cwd": f}))
                self.assertEqual(code, 1); self.assertEqual(out, ""); self.assertIn("does not mention push, merge or api", err)
            with unittest.mock.patch.object(guard, "read_verdicts", side_effect=RuntimeError("boom")):
                for tool, ti in (("push_files", {"branch": "main"}), ("create_or_update_file", {"branch": "main"}), ("delete_file", {"branch": 5})): self.assertIsNotNone(hook("mcp__github__" + tool, ti, f), tool)
                self.assertIn("guard failed", hook(MERGE, merge_call(), f))
    def test_the_guard_never_asks_and_never_allows(self):
        for c in STOP[:40]:
            with project(cmd_row(c)): hook("Bash", {"command": c}, self.feature)          # hook() asserts the decision is deny whenever there is one
        src = pathlib.Path(guard.__file__).read_text(encoding="utf-8")
        self.assertEqual(src.count('_emit("ask"'), 1); self.assertNotIn('_emit("allow"', src)

class TheEntry(Base):
    """The entry (bin/loop guard pre) is non-blocking for a bad payload and keeps the decision for a guarded call."""
    @classmethod
    def setUpClass(cls): cls.feature = repo("topic-a")
    def test_the_matcher_names_bash_and_the_four_github_tools(self):
        self.assertIn("Matcher: Bash, and mcp__github__ merge_pull_request, push_files, create_or_update_file, delete_file.", guard.__doc__)
    def test_a_bad_payload_through_the_entry_is_non_blocking(self):
        r = subprocess.run([sys.executable, "-I", str(LOOP), "guard", "pre"], input="{not json", capture_output=True, text=True, env=os.environ)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
    def test_a_guarded_call_through_the_entry_is_denied_with_exit_0(self):
        r = subprocess.run([sys.executable, "-I", str(LOOP), "guard", "pre"], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push -f origin x"}, "cwd": self.feature}), capture_output=True, text=True, env=os.environ)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
        r = subprocess.run([sys.executable, "-I", str(LOOP), "guard", "permissions", "apply"], capture_output=True, text=True, env=os.environ)
        self.assertEqual(r.returncode, 64)      # a missing --rules is an argument error

class ArtifactGuard(Base):
    def asks(self, ti):
        code, out, err = raw_pre(json.dumps({"tool_name": "Artifact", "tool_input": ti})); self.assertEqual(code, 0, err)
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else None
    def test_delete_and_force_ask(self):
        for i in ({"action": "delete", "url": "u"}, {"action": "delete", "url": "u", "path": "id"}, {"action": "delete_asset"}, {"file_path": "p", "force": True}): self.assertEqual(self.asks(i), "ask", i)
    def test_everything_else_passes_silently(self):
        for i in ({"action": "list"}, {"action": "read", "url": "u"}, {"file_path": "p", "url": "u"}, {"file_path": "p", "force": False}, {"action": "publish", "asset": True}, {}): self.assertIsNone(self.asks(i), i)
    def test_a_broken_input_never_says_ask_and_never_blocks(self):
        for t in ("", "{not json", "[]", "null"):
            code, out, _ = raw_pre(t); self.assertNotIn("ask", out, t); self.assertEqual(code, 0, t)

FIX = {"allow": ["Agent", "Skill(design-review)", "mcp__github__get_commit", "mcp__Claude_Docs__batch", "Bash(git status:*)"],
       "ask": ["Bash(claude *)", "Bash(git push *://*)"],
       "deny": ["mcp__github__enable_pr_auto_merge", "Bash(gh repo delete*)"],
       "retired": [{"rule": "Bash(git push *main*)", "reason": "decided by guard pre: a verdict or a denial, never a prompt"},
                   {"rule": "mcp__github__merge_pull_request", "reason": "decided by guard pre: a merge verdict or a denial"},
                   {"rule": "mcp__github__push_files", "reason": "decided by guard pre: a protected branch is denied"},
                   {"rule": "mcp__github__create_or_update_file", "reason": "decided by guard pre: a protected branch is denied"},
                   {"rule": "mcp__github__delete_file", "reason": "decided by guard pre: a protected branch is denied"}]}
RETIRED = [e["rule"] for e in FIX["retired"]]

def apply(settings, rules, *extra):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = guard.main(["permissions", "apply", "--rules", str(rules), "--settings", str(settings), *extra])
    return code, out.getvalue(), err.getvalue()

BAD_RULES = [{"retired": [{"rule": "Bash(git push *main*)"}]}, {"retired": [{"rule": "Bash(git push *main*)", "reason": ""}]}, {"retired": ["Bash(git push *main*)"]},
             {"retired": [{"rule": "Bash(git push *main*)", "reason": "x"}] * 2}, {"retired": [{"rule": "Bash(git push *main*)", "reason": "x"}], "ask": ["Bash(git push *main*)"]},
             {"retired": [{"rule": "Bash(git push *main*)", "reason": "x"}], "allow": ["Bash(git push *main*)"]}, {"deny": ["Agent"], "allow": ["Agent"]}, {"deny": ["Agent"], "ask": ["Agent"]},
             {"allow": ["Bash"]}, {"allow": ["Bash(*)"]}, {"allow": ["Bash(:*)"]}, {"allow": ["mcp__github"]}, {"allow": ["mcp__github__*"]}, {"allow": [5]}, {"allow": ["Agent", "Bash"]},
             {"ask": [None]}, {"ask": ["two\nlines(x)"]}, {"allow": "Agent"}, {"deny": ["Bash(*)"]}, ["not", "an", "object"]]

class ApplyPermissions(Base):
    def test_the_union_keeps_every_other_key_and_the_order_and_a_second_run_changes_nothing(self):
        start = {"hooks": {"Stop": []}, "autoMode": {"allow": ["$defaults"]}, "permissions": {"allow": ["Agent", "Bash(git push:*)"], "defaultMode": "default"}}
        s, r = write(start), write(FIX); code, out, _ = apply(s, r); self.assertEqual(code, 0)
        got = json.loads(s.read_text()); self.assertEqual(got["hooks"], start["hooks"]); self.assertEqual(got["autoMode"], start["autoMode"])
        self.assertEqual(got["permissions"]["allow"][:2], ["Agent", "Bash(git push:*)"]); self.assertEqual(got["permissions"]["defaultMode"], "default")
        self.assertTrue(set(FIX["allow"]) <= set(got["permissions"]["allow"])); self.assertEqual(got["permissions"]["ask"], FIX["ask"]); self.assertEqual(got["permissions"]["deny"], FIX["deny"])
        first = s.read_text(); self.assertIn("0 allow and 0 ask rules", apply(s, r)[1]); self.assertEqual(s.read_text(), first)
    def test_a_rule_the_repository_asks_about_leaves_allow(self):
        s = write({"permissions": {"allow": ["Bash(claude *)", "Bash(git push *://*)", "Agent"]}}); apply(s, write(FIX))
        got = json.loads(s.read_text())["permissions"]
        for rule in ("Bash(claude *)", "Bash(git push *://*)"): self.assertNotIn(rule, got["allow"]); self.assertIn(rule, got["ask"])
        self.assertIn("Agent", got["allow"])
    def test_exactly_the_retired_rules_leave_the_live_ask_list_and_nothing_else_does(self):
        mine = ["Bash(my own ask:*)", "mcp__elsewhere__tool"]
        start = {"hooks": {"Stop": []}, "permissions": {"allow": ["Agent", "Bash(git push:*)", "mcp__github__merge_pull_request", RETIRED[3]], "ask": [mine[0], *RETIRED, mine[1], *FIX["ask"]], "deny": ["WebFetch"], "defaultMode": "default"}}
        s = write(start); code, out, _ = apply(s, write(FIX)); got = json.loads(s.read_text()); p = got["permissions"]
        self.assertEqual(code, 0); self.assertEqual(set(start["permissions"]["ask"]) - set(p["ask"]), set(RETIRED)); self.assertEqual(p["ask"], [mine[0], mine[1], *FIX["ask"]])
        self.assertEqual(p["allow"][:4], start["permissions"]["allow"]); self.assertEqual(p["defaultMode"], "default"); self.assertEqual(got["hooks"], start["hooks"])
        self.assertEqual(p["deny"], ["WebFetch", *FIX["deny"]]); self.assertIn(f"{len(RETIRED)} retired ask rules removed", out); self.assertIn(f"{len(FIX['deny'])} deny rules added", out)
        first = s.read_text(); self.assertIn("0 retired ask rules removed, 0 deny rules added", apply(s, write(FIX))[1]); self.assertEqual(s.read_text(), first)
    def test_a_rule_that_is_not_retired_is_never_removed_even_when_it_looks_like_one(self):
        rules = write({"allow": ["Agent"], "ask": ["Bash(claude *)"], "retired": [{"rule": "Bash(git push *main*)", "reason": "the guard"}]})
        s = write({"permissions": {"ask": ["Bash(git push *main*)", "Bash(git push *main*) ", "Bash(git push *main*x)", "Bash(git push *--force*)", "mcp__github__merge_pull_request"], "allow": ["Bash(git push *main*)"]}})
        apply(s, rules); p = json.loads(s.read_text())["permissions"]
        self.assertEqual(p["ask"], ["Bash(git push *main*) ", "Bash(git push *main*x)", "Bash(git push *--force*)", "mcp__github__merge_pull_request", "Bash(claude *)"]); self.assertIn("Bash(git push *main*)", p["allow"])
    def test_check_reports_what_would_be_removed_and_writes_nothing(self):
        start = json.dumps({"permissions": {"ask": [RETIRED[0]]}}); s = write(start); out = apply(s, write(FIX), "--check")[1]
        self.assertIn("1 retired ask rules would be removed", out); self.assertIn("nothing written", out); self.assertEqual(s.read_text(), start)
    def test_a_retired_entry_without_a_reason_or_a_retired_rule_that_is_asked_or_allowed_refuses_the_whole_file(self):
        for bad in BAD_RULES[:12]:
            s = write("{}"); code, _, err = apply(s, write(bad)); self.assertEqual(code, 1, bad); self.assertIn("nothing written", err, bad); self.assertEqual(s.read_text(), "{}", bad)
        s = write("{}"); self.assertEqual(apply(s, write({"ask": ["Bash(claude *)"], "deny": ["Bash(gh repo delete*)"], "retired": [{"rule": "Bash(gh repo delete*)", "reason": "now a static deny"}]}))[0], 0)
        self.assertEqual(json.loads(s.read_text())["permissions"], {"allow": [], "ask": ["Bash(claude *)"], "deny": ["Bash(gh repo delete*)"]})
    def test_a_missing_file_is_created_and_a_broken_one_is_left_alone(self):
        s = pathlib.Path(tempfile.mkdtemp()) / "new.json"; self.assertEqual(apply(s, write(FIX))[0], 0)
        self.assertEqual(json.loads(s.read_text())["permissions"]["ask"], FIX["ask"])
        b = write("{not json"); code, _, err = apply(b, write(FIX)); self.assertEqual(code, 1); self.assertIn("left as it is", err); self.assertEqual(b.read_text(), "{not json")
    def test_check_writes_nothing(self):
        start = '{"permissions": {"allow": ["Agent"]}}'; s = write(start); apply(s, write(FIX), "--check"); self.assertEqual(s.read_text(), start)
    def test_retired_asks_stay_when_the_guard_was_not_installed(self):
        rules = {"ask": [], "retired": [{"rule": "Bash(git push *main*)", "reason": "x"}]}; s = {"permissions": {"ask": ["Bash(git push *main*)"]}}
        with unittest.mock.patch.dict(os.environ, {"PERMISSIONS_KEEP_RETIRED": "1"}): guard.merge_rules(s, rules)
        self.assertEqual(s["permissions"]["ask"], ["Bash(git push *main*)"])
        guard.merge_rules(s, rules); self.assertEqual(s["permissions"]["ask"], [])

class TheSource(Base):
    def test_a_rules_file_that_does_not_exist_writes_nothing(self):
        s = write("{}"); code, _, err = apply(s, pathlib.Path(tempfile.mkdtemp()) / "no-such.json")
        self.assertEqual(code, 1); self.assertIn("nothing written", err); self.assertEqual(s.read_text(), "{}")
    def test_the_default_settings_file_is_under_the_home_directory_and_the_report_says_so(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out): code = guard.main(["permissions", "apply", "--rules", str(write(FIX)), "--check"])
        self.assertEqual(code, 0); self.assertIn(str(self.home / ".claude" / "settings.json"), out.getvalue()); self.assertFalse((self.home / ".claude").exists())
    def test_blanket_and_malformed_rules_refuse_the_whole_file(self):
        for bad in ({"allow": ["Bash"]}, {"allow": ["Bash(*)"]}, {"allow": ["Bash(:*)"]}, {"allow": ["mcp__github"]}, {"allow": ["mcp__github__*"]}, {"allow": [5]}, {"allow": ["Agent", "Bash"]}, {"ask": [None]}, {"ask": ["two\nlines(x)"]}, {"allow": "Agent"}, ["not", "an", "object"]):
            s = write("{}"); code, _, _ = apply(s, write(bad)); self.assertEqual(code, 1, bad); self.assertEqual(s.read_text(), "{}", bad)
    def test_ordinary_rules_pass(self):
        rules = write({"allow": ["Agent", "Skill(artifact-design)", "mcp__github__get_commit", "mcp__Claude_Docs__batch", "Bash(git status:*)", "Bash(git merge --abort)"], "ask": ["Bash(git push *main*)", "mcp__github__merge_pull_request"]}); s = write("{}")
        apply(s, rules); self.assertEqual(len(json.loads(s.read_text())["permissions"]["allow"]), 6)
    def test_the_fixture_rules_pass_the_checks_the_script_applies(self):
        guard.check_rules(FIX)

class TheRulesFile(Base):
    def matches(self, rules, cmd):
        pats = [re.compile("^" + ".*".join(re.escape(x) for x in r[len("Bash("):-1].split("*")) + "$") for r in rules if r.startswith("Bash(")]
        return any(p.match(cmd) for p in pats)
    def test_nothing_is_listed_twice_or_both_allowed_and_asked(self):
        for k in ("allow", "ask", "deny"): self.assertEqual(len(FIX[k]), len(set(FIX[k])), k)
        self.assertEqual(len(RETIRED), len(set(RETIRED)))
        self.assertFalse(set(FIX["allow"]) & set(FIX["ask"])); self.assertFalse(set(FIX["deny"]) & (set(FIX["allow"]) | set(FIX["ask"]))); self.assertFalse(set(RETIRED) & (set(FIX["allow"]) | set(FIX["ask"])))
    def test_every_retired_rule_has_a_reason_that_says_what_decides_the_call_now(self):
        for e in FIX["retired"]:
            self.assertEqual(set(e), {"rule", "reason"}, e); self.assertIn("guard pre", e["reason"], e["rule"])
    def test_the_asks_that_stay_are_not_retired(self):
        self.assertFalse(set(FIX["ask"]) & set(RETIRED))
    def test_no_reserved_decision_is_allowed_asked_or_left_to_a_prompt_and_each_is_retired_or_denied(self):
        reserved = ["mcp__github__merge_pull_request", "mcp__github__push_files", "mcp__github__create_or_update_file", "mcp__github__delete_file", "mcp__github__enable_pr_auto_merge"]
        for r in reserved: self.assertNotIn(r, FIX["allow"], r); self.assertNotIn(r, FIX["ask"], r); self.assertTrue(r in RETIRED or r in FIX["deny"], r)
    def test_the_retired_patterns_cover_the_spellings_they_name_and_nothing_else(self):
        bash_retired = [r for r in RETIRED if r.startswith("Bash(")]
        self.assertTrue(self.matches(bash_retired, "git push origin main")); self.assertFalse(self.matches(bash_retired, "git status"))
        self.assertTrue(self.matches(FIX["deny"], "gh repo delete alice/project-x")); self.assertTrue(self.matches(FIX["ask"], "git push https://example.invalid/o/r.git HEAD"))
    def test_every_mcp_rule_is_spelled_with_a_server_and_a_tool_name(self):
        for r in FIX["allow"] + FIX["ask"] + FIX["deny"] + RETIRED:
            if r.startswith("mcp__"): self.assertRegex(r, r"^mcp__[A-Za-z_]+__[a-z_]+$", r)

class TheOnePathRule(Base):
    """A verdict in the configured file lets the exact act through; a different head does not (the new check of the work order)."""
    def test_a_verdict_in_the_configured_file_lets_the_exact_act_through_and_a_different_head_does_not(self):
        f = repo("topic-a")
        with project(merge_row(), where="evidence/verdicts.jsonl") as root:
            self.assertIsNone(hook(MERGE, merge_call(), f))
            self.assertIn("head", hook(MERGE, merge_call(expectedHeadSha=H2), f))
            self.assertIsNone(hook("Bash", {"command": f"git push origin {H1}:refs/heads/main"}, f))
            self.assertIsNotNone(hook("Bash", {"command": f"git push origin {H2}:refs/heads/main"}, f))
            self.assertFalse((root / "loop-state").exists())
    def test_pre_with_an_empty_payload_exits_0_with_a_note_on_standard_error(self):
        code, out, err = raw_pre("")
        self.assertEqual((code, out), (0, "")); self.assertIn("empty", err)
        r = subprocess.run([sys.executable, "-I", str(LOOP), "guard", "pre"], input="", capture_output=True, text=True, env=os.environ)
        self.assertEqual((r.returncode, r.stdout), (0, ""))


class ALeaseIsAnOptionOfThePushAndNotAWordInIt(Base):
    """Found on 2026-11-10 by a review of the ported guard: a lease-shaped word that git takes as the value of another option was counted as a lease."""
    @classmethod
    def setUpClass(cls): cls.feature = repo("topic-l")
    def held(self, args): return any(c == guard.DENY and "among its own arguments" in x for c, x in guard.push_reasons(args, self.feature))
    def test_a_lease_shaped_value_of_another_option_is_not_a_lease(self):
        lease = "--force-with-lease=topic:" + "a" * 40
        for args in (["-f", "-o", lease, "origin", "topic"], ["-f", "--push-option", lease, "origin", "topic"], ["-fo", lease, "origin", "topic"],
                     ["-f", "--push-opt", lease, "origin", "topic"], ["-f", "--exec", lease, "origin", "topic"], ["-f", "--receive-p", lease, "origin", "topic"]):
            self.assertTrue(self.held(args), args)
        for args in (["-f", lease, "origin", "topic"], [lease, "-f", "-o", "ci.skip", "origin", "topic"], ["-fo", "ci.skip", lease, "origin", "topic"], ["-f", "--push-option=x", lease, "origin", "topic"]):
            self.assertFalse(self.held(args), args)
    def test_an_ordinary_push_with_a_push_option_still_goes_on(self):
        for c in ("git push -o ci.skip origin topic", "git push --push-option ci.skip origin topic", "git push -uo ci.skip origin topic"): self.assertEqual(guard.decide(c, self.feature), [], c)
    def test_an_abbreviated_repo_selects_the_remote_too(self):
        for k, v in (("remote.upstream.url", "x"), ("remote.upstream.push", "HEAD:main")): subprocess.run(["git", "config", k, v], cwd=self.feature, check=True)
        for c in ("git push --rep upstream", "git push --rep=upstream"): self.assertTrue(guard.decide(c, self.feature), c)



class ALeaseProtectsOnlyWhenItIsTheOnlyForce(Base):
    """Seen with git 2.43.0 on 2026-11-10: beside -f, --force or a + refspec, a stale lease does not stop a push. And two findings of a review:
    a short cluster with an attached value hid its f, and a later --no-force-with-lease did not clear the lease."""
    @classmethod
    def setUpClass(cls): cls.feature = repo("topic-p")
    def said(self, args, text): return any(c == guard.DENY and text in x for c, x in guard.push_reasons(args, self.feature))
    def test_a_plain_force_is_refused_whatever_lease_it_carries(self):
        lease = "--force-with-lease=topic:" + "a" * 40
        for args in (["-f", lease, "origin", "topic"], ["--force", lease, "origin", "topic"], ["--forc", lease, "origin", "topic"], [lease, "origin", "+topic"],
                     ["-uf", lease, "origin", "topic"], ["-f", "origin", "topic"], ["origin", "+topic"]):
            self.assertTrue(self.said(args, "the lease must be the only force"), args)
        for args in ([lease, "origin", "topic"], [lease, "origin", ":topic"], [lease, "--delete", "origin", "topic"], [lease, "-d", "origin", "topic"]):
            reasons = guard.push_reasons(args, self.feature)
            self.assertTrue(reasons and all(c != guard.DENY for c, _ in reasons), (args, reasons))      # held for a verdict, not refused outright
    def test_the_f_of_a_cluster_is_read_whatever_value_is_attached_to_its_o(self):
        for args in (["-fo=ci.skip", "origin", "topic"], ["-fo", "ci.skip", "origin", "topic"], ["-qfo=x.y", "origin", "topic"]):
            self.assertTrue(self.said(args, "the lease must be the only force"), args)
        for c in ("git push -o=ci.skip origin topic", "git push -uo ci.skip origin topic", "git push -qo=f.d origin topic"): self.assertEqual(guard.decide(c, self.feature), [], c)
    def test_a_later_no_force_with_lease_cancels_the_lease(self):
        lease = "--force-with-lease=topic:" + "a" * 40
        for args in ([lease, "--no-force-with-lease", "origin", ":topic"], [lease, "--no-force-with-l", "--delete", "origin", "topic"]):
            self.assertTrue(self.said(args, "among its own arguments"), args)
        self.assertFalse(self.said(["--no-force-with-lease", lease, "origin", ":topic"], "among its own arguments"))      # a lease after the cancel counts



class ALeaseProtectsOnlyTheRefItNamesAtTheShaItNames(Base):
    """The rule, read from what git does (the class below runs git itself): every lease of a push is written out in full, each ref the push deletes is named
    by one of its leases, and the value of --recurse-submodules is not taken for the remote."""
    @classmethod
    def setUpClass(cls): cls.feature = repo("topic-n")
    def said(self, args, text): return any(c == guard.DENY and text in x for c, x in guard.push_reasons(args, self.feature))
    def test_every_lease_of_a_push_is_written_out_in_full(self):
        lease, other = "--force-with-lease=topic:" + "a" * 40, "--force-with-lease=other:" + "b" * 40
        for args in ([lease, "--force-with-lease", "origin", "topic", "other"], [lease, "--force-with-lease=other", "origin", "topic", "other"],
                     [lease, "--force-with-lease=other:origin/other", "origin", "topic", "other"], [lease, "--force-with-l", "origin", "topic"], ["--force-with-lease", "origin", "topic"]):
            self.assertTrue(self.said(args, "must be written out as"), args)
        for args in ([lease, "origin", "topic"], [lease, other, "origin", "topic", "other"], ["--force-with-lease", "--no-force-with-lease", lease, "origin", "topic"]):
            self.assertFalse(self.said(args, "must be written out as"), args)
    def test_a_delete_is_named_by_a_lease_of_its_push(self):
        lease, other = "--force-with-lease=topic:" + "a" * 40, "--force-with-lease=other:" + "b" * 40
        for args in ([lease, "origin", ":other"], [lease, "--delete", "origin", "other"], [lease, "-d", "origin", "topic", "other"], [lease, "origin", "topic", ":other"],
                     ["--force-with-lease=refs/heads/topic:" + "a" * 40, "origin", ":topic"]):
            self.assertTrue(self.said(args, "names the ref it deletes"), args)
        for args in ([lease, "origin", ":topic"], [lease, "--delete", "origin", "topic"], [lease, "-d", "origin", "topic"], [lease, "origin", ":refs/heads/topic"],
                     [lease, other, "origin", ":topic", ":other"], [lease, "origin", "topic"]):
            self.assertFalse(self.said(args, "names the ref it deletes"), args)
    def test_the_value_of_recurse_submodules_is_not_the_remote(self):
        for k, v in (("remote.upstream.url", "x"), ("remote.upstream.push", "HEAD:main")): subprocess.run(["git", "config", k, v], cwd=self.feature, check=True)
        for c in ("git push --recurse-submodules no upstream", "git push --recurse-sub on-demand upstream"): self.assertTrue(guard.decide(c, self.feature), c)
        self.assertEqual(guard.decide("git push --recurse-submodules check origin topic", self.feature), [])
    def test_every_option_git_lists_with_a_separate_value_is_known(self):
        import re
        usage = subprocess.run(["git", "push", "-h"], cwd=self.feature, capture_output=True, text=True)
        listed = {m.group(1).replace("[no-]", "") for m in re.finditer(r"^\s+(?:-\w, )?(--(?:\[no-\])?[\w-]+) [<(]", usage.stdout + usage.stderr, re.M)}
        if not listed: self.skipTest("this git does not list an option of git push as `--name <value>`")
        self.assertEqual(listed - guard.TAKES_ARG, set(), "the installed git takes a separate value for an option the guard does not know")


class TheGitFactsTheLeaseRuleRestsOn(Base):
    """What git does with a lease, seen on 2026-11-10 with git 2.43.0 and run again here against a temporary bare repository, so that a git which behaves
    otherwise fails in this class and the rule in push_reasons is read again. Before each push the remote's main and side are at B; the clone's main is at C,
    which is not a descendant of B; a lease on A is stale. after() gives (main, side) on the remote as letters, "-" for a ref that is gone."""
    @classmethod
    def setUpClass(cls):
        import os, tempfile
        cls.top = tempfile.mkdtemp(prefix="lease-facts-")
        cls.env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
                   "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
        g = cls.git
        g(".", "init", "-q", "--bare", "-b", "main", "remote.git"); g("remote.git", "config", "receive.advertisePushOptions", "true")
        g(".", "clone", "-q", "remote.git", "w"); g("w", "symbolic-ref", "HEAD", "refs/heads/main")
        g("w", "commit", "-q", "--allow-empty", "-m", "A"); g("w", "push", "-q", "origin", "main", "main:side"); cls.A = g("w", "rev-parse", "HEAD")
        g(".", "clone", "-q", "remote.git", "w2"); g("w2", "commit", "-q", "--allow-empty", "-m", "B"); g("w2", "push", "-q", "origin", "main", "main:side"); cls.B = g("w2", "rev-parse", "HEAD")
        g("w", "commit", "-q", "--allow-empty", "-m", "C"); cls.C = g("w", "rev-parse", "HEAD")
    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.top, ignore_errors=True)
    @classmethod
    def git(cls, where, *a, check=True):
        import os
        r = subprocess.run(["git", *a], cwd=os.path.join(cls.top, where), env=cls.env, capture_output=True, text=True)
        if check and r.returncode: raise AssertionError(f"git {' '.join(a)}: {r.stderr}")
        return r.stdout.strip()
    def after(self, *args, fetch=False):
        g = self.git
        g("w2", "push", "-q", "-f", "origin", self.B + ":refs/heads/main", self.B + ":refs/heads/side")
        if fetch: g("w", "fetch", "-q", "origin")
        g("w", "push", *[a.replace("<A>", self.A).replace("<B>", self.B) for a in args], check=False)
        letter = {self.A: "A", self.B: "B", self.C: "C", "": "-"}
        return tuple(letter.get(g("remote.git", "rev-parse", "-q", "--verify", "refs/heads/" + n, check=False), "?") for n in ("main", "side"))
    def test_a_stale_lease_stops_a_push_only_when_it_is_the_only_force(self):
        stale = "--force-with-lease=main:<A>"
        self.assertEqual(self.after(stale, "origin", "main"), ("B", "B"))
        self.assertEqual(self.after("--force-with-lease=main:<B>", "origin", "main"), ("C", "B"))
        for args in (("-f", stale, "origin", "main"), ("--force", stale, "origin", "main"), (stale, "origin", "+main"), ("-fo=ci.skip", "origin", "main")):
            self.assertEqual(self.after(*args), ("C", "B"), args)
        self.assertEqual(self.after("--force-with-lease=main:<B>", "--no-force-with-lease", "origin", "main"), ("B", "B"))
    def test_a_lease_protects_only_the_ref_it_names(self):
        self.assertEqual(self.after("--force-with-lease=main:<A>", "origin", ":side"), ("B", "-"))
        for args in (("--force-with-lease=side:<A>", "origin", ":side"), ("--force-with-lease=side:<A>", "--delete", "origin", "side"), ("--force-with-lease=side:<A>", "origin", ":refs/heads/side")):
            self.assertEqual(self.after(*args), ("B", "B"), args)
        self.assertEqual(self.after("-f", "--force-with-lease=side:<A>", "--delete", "origin", "side"), ("B", "-"))
    def test_a_lease_with_no_sha_expects_what_the_remote_tracking_ref_holds(self):
        self.git("w", "update-ref", "refs/remotes/origin/main", self.A)          # the clone has not seen B
        self.assertEqual(self.after("--force-with-lease", "origin", "main"), ("B", "B"))
        for args in (("--force-with-lease", "origin", "main"), ("--force-with-lease=side:<B>", "--force-with-lease", "origin", "main"), ("--force-with-lease=main", "origin", "main")):
            self.assertEqual(self.after(*args, fetch=True), ("C", "B"), args)
    def test_the_value_of_recurse_submodules_may_be_the_next_word(self):
        self.git("w", "push", "--recurse-submodules", "no", "origin", "HEAD:refs/heads/new1")
        self.assertEqual(self.git("remote.git", "rev-parse", "refs/heads/new1"), self.C)


class TheGuardAgreesWithGit(Base):
    """An oracle, not a model: a slice of loop/tests/oracle_push.py. Every shape of `git push` that the guard does not refuse outright is run by git against a temporary
    bare repository. None may destroy or delete a branch there (every lease in a shape is stale or weak), and one that the guard lets go on with nothing said may
    not write main. The whole sweep (about 29,000 shapes): python3 -I loop/tests/oracle_push.py --depth 2 --jobs 4."""
    def test_no_push_the_guard_lets_through_destroys_a_branch_or_writes_main_unseen(self):
        import importlib.util, pathlib
        spec = importlib.util.spec_from_file_location("oracle_push", pathlib.Path(__file__).with_name("oracle_push.py"))
        oracle = importlib.util.module_from_spec(spec); spec.loader.exec_module(oracle)
        got = oracle.sweep(guard, oracle.grammar(depth=1, small=True))
        self.assertGreater(got["run"], 50, got)          # git did run: a guard that refuses every shape would hold both properties and be of no use
        self.assertEqual(got["broken"], [], got["broken"][:5])


if __name__ == "__main__": unittest.main()


class FindingsOfTheFirstPublishedReview(Base):
    """Two holes in the reading of a push."""
    @classmethod
    def setUpClass(cls): cls.feature = repo("topic-r")
    def test_the_remote_chosen_with_repo_is_the_one_whose_configuration_is_read(self):
        for k, v in (("remote.upstream.url", "x"), ("remote.upstream.push", "HEAD:main")):
            subprocess.run(["git", "config", k, v], cwd=self.feature, check=True)
        self.assertEqual(guard.decide("git push", self.feature), [])
        for c in ("git push --repo upstream", "git push --repo=upstream"): self.assertTrue(guard.decide(c, self.feature), c)
    def test_a_lease_must_be_an_argument_of_the_push_that_forces_or_deletes(self):
        lease = "--force-with-lease=topic:" + "a" * 40
        no_lease = guard.push_reasons(["--delete", "origin", "topic"], self.feature)
        self.assertTrue(any(c == guard.DENY and "among its own arguments" in t for c, t in no_lease), no_lease)
        with_lease = guard.push_reasons([lease, "--delete", "origin", "topic"], self.feature)
        self.assertTrue(with_lease and all(c != guard.DENY for c, _ in with_lease), with_lease)
        # a lease written only in a comment is not given to git: the push is held whatever verdict is on file
        self.assertTrue(guard.decide("git push --delete origin topic # " + lease, self.feature))
