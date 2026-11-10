"""An oracle for the guard's reading of `git push`: git itself. Not a test file (pytest does not collect it): loop/tests/test_guard.py runs a small slice
of it, and `python3 -I loop/tests/oracle_push.py --depth 2` runs the whole sweep.

Every shape (the words after `git push`) is judged by guard.push_reasons and, unless the guard refuses it outright, run by git against a temporary bare
repository. The fixture: the remote has main, topic and side at B. The clone's branch topic is at C, which is not a descendant of B, so an update of a remote
branch to C destroys B there; its branch ff is at D, a child of B, and tracks origin/main. The clone has just fetched, so its remote-tracking refs are at B and
a lease with no sha is as good as a plain force. <A> in a shape stands for a stale sha: a commit the clone has, which is not what the remote holds. No shape
carries a lease that is right, so a branch that is destroyed or deleted was protected by no lease.

Two properties, for a shape that gets the reasons R:
  P  no DENY in R   =>  git destroys no branch of the remote and deletes none (with a verdict the push would go on, and every lease in it is stale or weak)
  Q  R is empty     =>  and main is not written at all (the push goes on with nothing said)
A shape the guard refuses is not run: the properties hold for it whatever git does.

usage: python3 -I loop/tests/oracle_push.py [--guard FILE] [--depth 0|1|2] [--small] [--variant default|simple|upstream|current ...] [--shapes FILE.json ...] [--jobs N]
  --variant  default: the clone is on topic, which tracks nothing. The others: it is on ff, which tracks origin/main, and push.default is that value.
  --shapes   a JSON list of shapes, each a list of words or an object with "argv"; they are run in place of the built-in grammar.
  A shape with a path, a URL, --receive-pack, --exec or a --repo other than origin is left out: it could reach outside the fixture."""
import argparse, importlib, importlib.util, itertools, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time

GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0", "GIT_ALLOW_PROTOCOL": "file"}
BRANCHES = ("main", "topic", "side")
LEASES = (["--force-with-lease=topic:<A>"], ["--force-with-lease=side:<A>"], ["--force-with-lease=refs/heads/topic:<A>"])
WEAK = (["--force-with-lease"], ["--force-with-lease=topic"], ["--force-with-lease=side"], ["--force-with-lease=topic:origin/topic"], ["--force-with-l=topic:<A>"])
FORCES = (["-f"], ["--force"], ["-fo=x"], ["-uf"], ["--force-if-includes"], ["--no-force"], ["--no-force-with-lease"])
DELETES = (["-d"], ["--delete"], ["--dele"], ["-do", "x"])
VALUES = (["-o", "x"], ["-ox"], ["-uo", "x"], ["--push-option", "x"], ["--push-opt", "x"], ["--push-option=x"], ["--recurse-submodules", "no"], ["--recurse-sub", "no"],
          ["--recurse-submodules=no"], ["--repo", "origin"], ["--repo=origin"])
PLAIN = (["-u"], ["-q"], ["--atomic"], ["--tags"], ["--follow-tags"], ["--signed=no"])
ALL_SENT = (["--mirror"], ["--prune"], ["--all"])
TAILS = (["origin", "topic"], ["origin", "+topic"], ["origin", ":side"], ["origin", "side"], ["origin", "topic", ":side"], ["origin", "topic:side"], ["origin", "+topic:side"],
         ["origin", ":refs/heads/side"], ["origin", "refs/heads/topic"], ["origin", "topic:refs/heads/side"], ["origin", "<A>:side"], ["origin", "HEAD"], ["origin", "HEAD:side"],
         ["origin", "ff:topic"], ["origin", "ff:main"], ["origin", "ff:refs/heads/main"], ["origin"], [])
SMALL_TAILS = (["origin", "topic"], ["origin", ":side"], ["origin", "side"], ["origin", "topic", ":side"], ["origin", "ff:main"], ["origin"], [])
OKWORD = re.compile(r"[A-Za-z0-9_.:+=<>@^~*/-]*")


def grammar(depth=1, small=False):
    """The built-in shapes: every sequence of at most `depth` option tokens before each tail, and each single token after each tail (git reads an option wherever it stands)."""
    tokens = [t for g in ((LEASES, WEAK, FORCES, DELETES, VALUES) if small else (LEASES, WEAK, FORCES, DELETES, VALUES, PLAIN, ALL_SENT)) for t in g]
    tails = SMALL_TAILS if small else TAILS
    out = [[w for t in combo for w in t] + tail for n in range(depth + 1) for combo in itertools.product(tokens, repeat=n) for tail in tails]
    if depth: out += [tail + t for t in tokens for tail in tails if tail]
    return [list(s) for s in dict.fromkeys(tuple(s) for s in out)]


def safe(argv):
    """False for a shape that could reach outside the fixture: a path or a URL as a word or a value, a program to run on the other side, a --repo that is not origin."""
    if not isinstance(argv, list) or len(argv) > 12 or not all(isinstance(a, str) for a in argv): return False
    for i, a in enumerate(argv):
        name, eq, val = a.partition("=")
        if not OKWORD.fullmatch(a) or a.startswith((".", "/", "~")) or ".." in a or "://" in a or val.startswith((".", "/", "~")): return False
        if name.startswith("--") and len(name) >= 3 and any(t.startswith(name) for t in ("--receive-pack", "--exec", "--upload-pack")): return False
        if name.startswith("--rep") and "--repo".startswith(name) and (val if eq else (argv[i + 1] if i + 1 < len(argv) else "")) != "origin": return False
    return True


def git(cwd, *a, check=True, timeout=60):
    r = subprocess.run(["git", *a], cwd=cwd, env={**os.environ, **GIT_ENV}, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=timeout)
    if check and r.returncode: raise RuntimeError(f"git {' '.join(a)} in {cwd}: {r.stderr.strip()}")
    return r


class Fixture:
    """The temporary remote and clone the docstring describes. clean() puts them back when a push changed anything."""
    def __init__(self, variant="default"):
        self.top = t = pathlib.Path(tempfile.mkdtemp(prefix="oracle-push-")); self.bare, self.w, self.w2 = t / "remote.git", t / "w", t / "w2"
        rev = lambda where: git(where, "rev-parse", "HEAD").stdout.strip()
        git(t, "init", "-q", "--bare", "-b", "main", str(self.bare)); git(self.bare, "config", "receive.advertisePushOptions", "true")
        git(t, "clone", "-q", str(self.bare), str(self.w)); git(self.w, "symbolic-ref", "HEAD", "refs/heads/main")
        git(self.w, "commit", "-q", "--allow-empty", "-m", "A"); git(self.w, "push", "-q", "origin", "main", "main:topic", "main:side"); self.A = rev(self.w)
        git(t, "clone", "-q", str(self.bare), str(self.w2)); git(self.w2, "commit", "-q", "--allow-empty", "-m", "B"); self.B = rev(self.w2)
        git(self.w2, "push", "-q", "origin", "main", "main:topic", "main:side")
        git(self.w, "checkout", "-q", "-b", "topic"); git(self.w, "commit", "-q", "--allow-empty", "-m", "C")
        git(self.w, "fetch", "-q", "origin"); git(self.w, "checkout", "-q", "-b", "ff", "origin/main"); git(self.w, "commit", "-q", "--allow-empty", "-m", "D")
        if variant == "default": git(self.w, "checkout", "-q", "topic")
        else: git(self.w, "config", "push.default", variant)          # the clone stays on ff, which tracks origin/main
        self.config = (self.w / ".git" / "config").read_text(encoding="utf-8"); self.local = self._local(); self.dirty = False
    def _local(self): return git(self.w, "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads").stdout + git(self.w, "symbolic-ref", "HEAD").stdout
    def clean(self):
        if not self.dirty: return
        git(self.w2, "push", "-q", "-f", "origin", *[f"{self.B}:refs/heads/{n}" for n in BRANCHES])
        (self.w / ".git" / "config").write_text(self.config, encoding="utf-8")
        if self._local() != self.local: raise RuntimeError("a shape changed the clone's own branches: it reached outside the remote")
        git(self.w, "fetch", "-q", "--prune", "origin"); self.dirty = False
    def push(self, argv):
        """(git's exit code, {branch: kept | ff | destroyed | deleted}) after `git push ARGV` from the clone."""
        try: rc = git(self.w, "push", *[a.replace("<A>", self.A) for a in argv], check=False, timeout=20).returncode
        except subprocess.TimeoutExpired: rc = "timeout"
        seen = dict(l.split() for l in git(self.bare, "for-each-ref", "--format=%(refname:short) %(objectname)", *[f"refs/heads/{n}" for n in BRANCHES]).stdout.splitlines())
        st = {n: "deleted" if n not in seen else "kept" if seen[n] == self.B else
                 "ff" if git(self.bare, "merge-base", "--is-ancestor", self.B, seen[n], check=False).returncode == 0 else "destroyed" for n in BRANCHES}
        self.dirty = rc == "timeout" or any(v != "kept" for v in st.values()) or (self.w / ".git" / "config").read_text(encoding="utf-8") != self.config
        return rc, st
    def cleanup(self): shutil.rmtree(self.top, ignore_errors=True)


def judge(mod, fx, argv):
    """One shape: (the guard's reasons, what git did or None when the guard refused, the property broken or "")."""
    fx.clean()
    why = mod.push_reasons([a.replace("<A>", fx.A) for a in argv], str(fx.w))
    if any(c == mod.DENY for c, _ in why): return why, None, ""
    rc, st = fx.push(argv)
    gone = [n for n in BRANCHES if st[n] in ("destroyed", "deleted")]
    return why, {"rc": rc, **st}, "P" if gone else "Q" if not why and st["main"] != "kept" else ""


def sweep(mod, shapes, variant="default"):
    """Runs the shapes against the guard module `mod`; returns {"shapes", "refused", "run", "left_out", "broken": [{"argv", "property", "git", "reasons"}]}."""
    saved = {k: os.environ.get(k) for k in GIT_ENV}; os.environ.update(GIT_ENV)          # the guard's own git calls read the configuration the pushes read
    protected = getattr(mod, "PROTECTED", None)
    if not protected: mod.PROTECTED = frozenset({"main", "master"})
    out, fx = {"shapes": 0, "refused": 0, "run": 0, "left_out": 0, "broken": []}, Fixture(variant)
    try:
        for argv in shapes:
            if not safe(argv): out["left_out"] += 1; continue
            out["shapes"] += 1
            why, did, broken = judge(mod, fx, argv)
            out["refused" if did is None else "run"] += 1
            if broken: out["broken"].append({"argv": argv, "property": broken, "git": did, "reasons": [list(r) for r in why]})
    finally:
        fx.cleanup()
        if not protected: mod.PROTECTED = protected
        for k, v in saved.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v
    return out


def load(path):
    """The guard module at `path`: the package's loop/guard.py, or any file that defines push_reasons and DENY."""
    p = pathlib.Path(path).resolve()
    if p.name == "guard.py" and p.parent.name == "loop":
        sys.path.insert(0, str(p.parent.parent)); return importlib.import_module("loop.guard")
    spec = importlib.util.spec_from_file_location("guard_under_test", p); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def _work(job):
    path, shapes, variant = job
    return sweep(load(path), shapes, variant)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="oracle_push", description="run git itself against the guard's reading of a push")
    ap.add_argument("--guard", default=str(pathlib.Path(__file__).resolve().parents[1] / "guard.py"))
    ap.add_argument("--depth", type=int, default=1, choices=(0, 1, 2)); ap.add_argument("--small", action="store_true")
    ap.add_argument("--variant", action="append", choices=("default", "simple", "upstream", "current")); ap.add_argument("--shapes", action="append"); ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args(argv)
    if a.shapes:
        shapes = [s["argv"] if isinstance(s, dict) else s for f in a.shapes for s in json.loads(pathlib.Path(f).read_text(encoding="utf-8"))]
        shapes = [list(s) for s in dict.fromkeys(tuple(s) for s in shapes if isinstance(s, list) and all(isinstance(w, str) for w in s))]
    else: shapes = grammar(a.depth, a.small)
    bad = 0
    for variant in a.variant or ["default"]:
        t0 = time.time(); jobs = [(a.guard, shapes[n::a.jobs], variant) for n in range(a.jobs)]
        if a.jobs > 1:
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor(a.jobs) as ex: parts = list(ex.map(_work, jobs))
        else: parts = [_work(j) for j in jobs]
        total = {k: sum(p[k] for p in parts) for k in ("shapes", "refused", "run", "left_out")}; broken = [b for p in parts for b in p["broken"]]; bad += len(broken)
        print(f"variant {variant}: {total['shapes']} shapes, {total['refused']} refused by the guard, {total['run']} run by git, {total['left_out']} left out, "
              f"{len(broken)} broke a property ({time.time() - t0:.0f}s)")
        for b in broken[:60]: print(f"  {b['property']}  git push {' '.join(b['argv'])}   git: {b['git']}   guard: {b['reasons']}")
    return 1 if bad else 0


if __name__ == "__main__": sys.exit(main())
