"""Where one project keeps what the loop reads and writes: loop.json at the project's root, every key optional.

INVARIANT: no module of this package holds a path, a name or a number that belongs to one project; each asks load().
FAILS WHEN: a file under loop/ names a project or a machine's absolute path, or loop.json has a key nobody reads
(loop/tests/test_selfcheck.py).

usage, from a module:  cfg = load(); cfg.path("bank"); cfg["reread_every"]; cfg.root; cfg.state("counter.json"); cfg.transcript()
The project root is, in this order: the environment variable LOOP_PROJECT; the nearest directory at or above the working
directory that holds loop.json; the top of the git work tree; the working directory."""
import json, os, pathlib, subprocess

KIT = pathlib.Path(__file__).resolve().parents[1]
DEFAULTS = {
    "principal_method": "PRINCIPAL-METHOD.md",    # the principal's own text: printed at every prompt and every reread_every tool calls
    "reread_every": 5,
    "bank": "loop-state/bank.jsonl",              # append-only, in git: one record per utterance of the principal
    "words": [],                                  # globs of more files that hold the principal's words (for `record find`)
    "not_principal_prefixes": [],                 # a text that starts with one of these is not the principal's (added to the built-in list)
    "tree": "loop-state/tree.json",               # goals and questions; a node whose status starts with "wait" needs a root chain
    "chain_debt": "loop-state/chain-debt.json",   # the waits that had no chain when the gate was first run
    "clause_bank_dir": "loop-state/bank",         # the bank cut into clauses, which chain links cite
    "verdicts": "loop-state/verdicts.jsonl",      # an advisor's verdicts, recorded before a guarded act
    "protected_branches": ["main"],
    "backup": {"remote": "origin", "prefix": "backup/", "extra_dirs": []},
    "transcripts_dir": "~/.claude/projects",      # where the session transcripts are; LOOP_PROJECTS_DIR overrides it
    "state_dir": ".loop",                         # runtime state (counters, logs): never committed
    "checks": [],                                 # what `tick` runs: [{"name": ..., "run": [VERB, ...], "every_s": ...}]
    "stop_runs": [["keep", "backup"], ["record", "bank"]],   # what the stop hook runs every time; a failure is reported, never blocks
    "stop_blocks_on": [],                         # commands whose failure refuses the stop, at most stop_cap times in a row
    "stop_cap": 3,
}


class Config(dict):
    def __init__(self, root, values, file):
        super().__init__(values)
        self.root, self.file = pathlib.Path(root), file

    def path(self, key):
        """The absolute path of a path-valued key; a relative value is under the project root."""
        p = pathlib.Path(os.path.expanduser(str(self[key])))
        return p if p.is_absolute() else self.root / p

    def state(self, name=""):
        """A file under the runtime state directory. The directory is created and kept out of git status in this clone."""
        d = self.path("state_dir")
        d.mkdir(parents=True, exist_ok=True)
        _exclude(self.root, d)
        return d / name if name else d

    def transcripts_dir(self):
        return pathlib.Path(os.path.expanduser(os.environ.get("LOOP_PROJECTS_DIR") or str(self["transcripts_dir"])))

    def transcript(self):
        """The live session's transcript: LOOP_TRANSCRIPT, else the newest */*.jsonl under transcripts_dir(), else None."""
        given = os.environ.get("LOOP_TRANSCRIPT")
        if given:
            return pathlib.Path(given)
        found = [p for p in self.transcripts_dir().glob("*/*.jsonl") if p.is_file()]
        return max(found, key=lambda p: p.stat().st_mtime) if found else None


def _exclude(root, d):
    """Keep a runtime directory out of `git status` without touching a tracked file (.git/info/exclude is local to the clone)."""
    try:
        rel = d.resolve().relative_to(root.resolve())
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-path", "info/exclude"], capture_output=True, text=True)
        if r.returncode != 0:
            return
        ex = pathlib.Path(r.stdout.strip())
        ex = ex if ex.is_absolute() else root / ex
        line = "/" + str(rel) + "/"
        text = ex.read_text(encoding="utf-8") if ex.exists() else ""
        if line not in text.splitlines():
            ex.parent.mkdir(parents=True, exist_ok=True)
            with ex.open("a", encoding="utf-8") as f:
                f.write(("\n" if text and not text.endswith("\n") else "") + line + "\n")
    except (ValueError, OSError):
        return


def project_root(start=None):
    env = os.environ.get("LOOP_PROJECT")
    if env:
        return pathlib.Path(env).resolve()
    here = pathlib.Path(start or os.getcwd()).resolve()
    for d in (here, *here.parents):
        if (d / "loop.json").is_file():
            return d
    r = subprocess.run(["git", "-C", str(here), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return pathlib.Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else here


def load(start=None):
    """The project's configuration over the defaults. A key that is not in DEFAULTS is refused: a typo must not pass in silence."""
    root = project_root(start)
    f = root / "loop.json"
    values = json.loads(json.dumps(DEFAULTS))
    if f.is_file():
        given = json.loads(f.read_text(encoding="utf-8"))
        unknown = sorted(set(given) - set(DEFAULTS))
        if unknown:
            raise SystemExit(f"loop.json: unknown key(s) {unknown}; the known keys are {sorted(DEFAULTS)}")
        for k, v in given.items():
            values[k] = {**values[k], **v} if isinstance(values[k], dict) and isinstance(v, dict) else v
    return Config(root, values, f if f.is_file() else None)
