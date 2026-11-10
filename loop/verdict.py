"""guard verdict: records the verdict the guard reads, as one line of the verdict file, so that a guarded act has a row to name.
Four forms: `hold` and `go` for a merge, or a push, of one head; `command` for one whole Bash command line; `withdraw` for a row the file already holds. The checks and the append run under one lock on the project folder, so two writers cannot both pass the duplicate check. A refusal writes nothing and exits 2.

INVARIANT: a row is appended only after every check passes, under one lock held from the check to the append, and no verb runs without that lock (no fcntl); a go row's answer file is on disk, is not blank and, for a merge, names its head as a whole run of hexadecimal characters (a hold row needs no answer); a hold is refused while a go row for its head counts; one verdict is recorded once per head (merge) or per command string; a withdrawal names a row the file holds; a merge row with --pr has a repository; head, base and tree are 40 lower-case hex; the repository is read from the origin remote's address, never written as a literal; the file written is the one loop.json names under "verdicts".
FAILS WHEN: a row is appended after a refusal or without its checks; a verb runs without the lock; two writers both record one head or one command; a refused call leaves a file or a folder behind; a go row is written with no answer file, with a blank one, or with one that does not name its head; a hold is recorded while a go row for its head counts; a --pr row has no repository (loop/tests/test_verdict.py).
Not covered: rows written by hand. The verb compares heads as they are written and the guard reads them in lower case, so a hand-written go row whose head is in upper case counts for the guard and is not seen by the once-per-head and hold checks.

usage: python3 -I bin/loop guard verdict hold|go --head SHA40 --base SHA40 --branch NAME --by TEXT --answer PATH --note TEXT [--pr N --repo OWNER/NAME --slug TEXT --tree SHA40 --tests TEXT --undo TEXT --dry-run]
       python3 -I bin/loop guard verdict command --command TEXT --by TEXT --answer PATH --note TEXT [--repo OWNER/NAME --slug TEXT --undo TEXT --dry-run]
       python3 -I bin/loop guard verdict withdraw ID [--note TEXT --dry-run]
A relative --answer is read under the project root, and a go row needs that file on disk. --pr needs a repository, from --repo or from the origin remote's address. --dry-run runs every check and prints the row; it writes nothing.
Exit 0: the row is written, or a dry run passes. Exit 2: a check refuses it, the arguments are wrong, the lock is not available here (no fcntl module: every verb refuses, a dry run included), or the verdict file cannot be read or written.
The id is v-<UTC yyyymmddThhmm>Z-<slug>-<head8>, with -pending for a hold; a command row's id ends in the first 8 hex of the sha-256 of its string. The default undo texts are HOLD_UNDO and GO_UNDO below."""
import argparse, contextlib, datetime, hashlib, json, os, pathlib, re, subprocess, sys
from loop import config

try:
    import fcntl
except ImportError:   # no file locks on this platform: main refuses every verb (loop/hook.py has the same guard)
    fcntl = None

HOLD_UNDO = "nothing is merged, so nothing to undo; remote branches stay until a verdict row says otherwise (deleting a remote branch needs an advisor's verdict first)"
GO_UNDO = 'Before the push: withdraw by appending one line {"verdict": "withdrawn", "of": ID}; after the push: one revert commit with its own verdict, never a force-push'
SHA = re.compile(r"[0-9a-f]{40}")
REPO = re.compile(r"[a-z0-9_.-]+/[a-z0-9_.-]+")


class Refused(Exception):
    """A check refused the row: nothing is written, and the message says which check and why."""


def _now(now=None):
    return now if now is not None else datetime.datetime.now(datetime.timezone.utc)


def _sha(name, value):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise Refused(f"{name} is not 40 lower-case hex: {value!r}")


def _slug(branch, given, default):
    """The slug of an id: the given one, else the branch's own name without its date and round. Lower-case letters, digits and hyphens only."""
    if given is None and branch is not None:
        given = re.sub(r"-r\d+$", "", re.sub(r"-\d{4}-\d{2}-\d{2}", "", branch.split("/")[-1]))
    return re.sub(r"[^a-z0-9]+", "-", (given or "").lower()).strip("-") or default


def repo_of_remote(url):
    """OWNER/NAME (lower case) of a remote's address when its path has exactly two parts; None for a local path or any other shape."""
    u = (url or "").strip().rstrip("/")
    if "://" in u:
        path = u.split("://", 1)[1]
        path = path.split("/", 1)[1] if "/" in path else ""
    elif ":" in u and "/" not in u.split(":", 1)[0]:
        path = u.split(":", 1)[1]
    else:
        return None
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.split("/")
    if len(parts) != 2:
        return None
    repo = f"{parts[0]}/{parts[1]}".lower()
    return repo if REPO.fullmatch(repo) else None


def origin_repo(root):
    """OWNER/NAME of the origin remote of the project's repository, or None when there is no such remote or it names none."""
    try:
        r = subprocess.run(["git", "-C", str(root), "config", "--get", "remote.origin.url"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return repo_of_remote(r.stdout) if r.returncode == 0 else None


def _answer_check(root, answer, head=None):
    """A go row's answer must be a file on disk; a merge row's answer must also name its head. A relative path is under the project root."""
    p = pathlib.Path(answer)
    try:
        text = (p if p.is_absolute() else pathlib.Path(root) / p).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        raise Refused(f"the answer file {answer} is missing or unreadable (a relative path is read under the project root); a go row needs the advisor's answer on disk")
    if not text.strip():
        raise Refused(f"the answer file {answer} is empty; a go row needs the advisor's answer on disk")
    if head is not None and not re.search(rf"(?<![0-9a-f]){head}(?![0-9a-f])", text, re.I):
        raise Refused(f"the answer file {answer} does not name the head {head}")


def merge_row(verb, *, head, base, branch, by, answer, note, rows, root, now=None, pr=None, repo=None,
              slug=None, tree=None, tests=None, undo=None):
    """The row of a hold or a go verdict for a merge, or a push, of `head`. `rows` are the rows the verdict file holds now.
    Refused when head, base or tree is not 40 lower-case hex; when the file holds a row of this verdict for this head; when a go
    row's answer does not name the head; and when --pr has no repository."""
    _sha("head", head)
    _sha("base", base)
    if tree is not None:
        _sha("tree", tree)
    if any(r.get("kind") == "merge" and r.get("head") == head and r.get("verdict") == verb for r in rows):
        raise Refused(f"a {verb} row for {head[:8]} exists: a verdict is recorded once per head")
    if verb == "hold":
        gone = {r.get("of") for r in rows if r.get("verdict") == "withdrawn" and isinstance(r.get("of"), str)}
        live = [r["id"] for r in rows if r.get("kind") == "merge" and r.get("head") == head and r.get("verdict") == "go"
                and isinstance(r.get("id"), str) and r["id"] not in gone]
        if live:
            raise Refused(f"the go row {live[0]} for {head[:8]} counts, and a hold does not take it back: withdraw it with: guard verdict withdraw {live[0]}")
    if verb == "go":
        _answer_check(root, answer, head)
    repo = repo.lower() if repo else None
    if pr is not None and not repo:
        raise Refused("--pr needs a repository: give --repo OWNER/NAME, or name one with the origin remote")
    t = _now(now)
    stamp, idstamp = t.strftime("%Y-%m-%dT%H:%M:%SZ"), t.strftime("%Y%m%dT%H%MZ")
    row = {"id": f"v-{idstamp}-{_slug(branch, slug, 'x')}-{head[:8]}" + ("-pending" if verb == "hold" else ""), "at": stamp, "by": by, "answer": answer}
    if repo:
        row["repo"] = repo
    row["kind"] = "merge"
    if pr is not None:
        row["pr"] = pr
    row.update(branch=branch, head=head, base=base)
    if tree:
        row["tree"] = tree
    if tests:
        row["tests"] = tests
    row.update(verdict=verb, note=note, undo=undo or (HOLD_UNDO if verb == "hold" else GO_UNDO))
    return row


def command_row(*, command, by, answer, note, rows, root, now=None, repo=None, slug=None, undo=None):
    """The row of a go verdict for one whole command line, which the guard allows as that exact string (stripped).
    Refused when the file holds a go row for the same string, or when the answer file is missing."""
    if any(r.get("kind") == "command" and r.get("verdict") == "go" and str(r.get("command", "")).strip() == command.strip() for r in rows):
        raise Refused("a go row for this command exists: a verdict is recorded once per command string")
    _answer_check(root, answer)
    repo = repo.lower() if repo else None
    t = _now(now)
    stamp, idstamp = t.strftime("%Y-%m-%dT%H:%M:%SZ"), t.strftime("%Y%m%dT%H%MZ")
    digest = hashlib.sha256(command.encode("utf-8")).hexdigest()[:8]
    row = {"id": f"v-{idstamp}-{_slug(None, slug, 'command')}-{digest}", "at": stamp, "by": by, "answer": answer}
    if repo:
        row["repo"] = repo
    row.update(kind="command", command=command, verdict="go", note=note, undo=undo or GO_UNDO)
    return row


def withdrawal(target, *, rows, note="", now=None):
    """The line that withdraws the row with id `target`; refused when the file holds no row with that id."""
    if not any(r.get("id") == target for r in rows):
        raise Refused(f"no verdict row has the id {target}: nothing to withdraw")
    t = _now(now)
    return {"verdict": "withdrawn", "of": target, "at": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "note": note}


def parse_rows(text):
    """The rows of a verdict file's text: each line that is a JSON object. A broken line is skipped, as the guard skips it."""
    rows = []
    for line in text.splitlines():
        if line.strip():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict):
                rows.append(r)
    return rows


def _text(value):
    if not value.strip():
        raise argparse.ArgumentTypeError("must not be empty")
    return value


def _repo(value):
    v = value.strip().lower()
    if not REPO.fullmatch(v):
        raise argparse.ArgumentTypeError("must be OWNER/NAME")
    return v


def _positive(value):
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a whole number")
    if n < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return n


def _parser():
    ap = argparse.ArgumentParser(prog="loop guard verdict", description="record a verdict the guard reads, or withdraw one")
    sub = ap.add_subparsers(dest="verb", required=True)
    for verb, what in (("hold", "a hold: nothing is merged yet (the row ends in -pending)"), ("go", "a go: the advisor's verdict for one head")):
        p = sub.add_parser(verb, help=what)
        p.add_argument("--head", required=True, help="the 40-hex head the verdict covers")
        p.add_argument("--base", required=True, help="the 40-hex base of that head")
        p.add_argument("--branch", required=True, type=_text, help="the branch that holds the head")
        p.add_argument("--by", required=True, type=_text, help="who gave the verdict")
        p.add_argument("--answer", required=True, type=_text, help="the answer file of the verdict (a go row needs it on disk, naming the head)")
        p.add_argument("--note", required=True, help="a note for the record")
        p.add_argument("--pr", type=_positive, help="the pull request number, for a merge through a pull request")
        p.add_argument("--repo", type=_repo, help="OWNER/NAME; by default the origin remote's")
        p.add_argument("--slug", type=_text, help="the slug in the id; by default the branch's own name")
        p.add_argument("--tree", help="the 40-hex tree of the head")
        p.add_argument("--tests", help="what the tests showed")
        p.add_argument("--undo", type=_text, help="the undo text (by default the one for this verdict)")
        p.add_argument("--dry-run", action="store_true", help="run every check and print the row; write nothing")
    c = sub.add_parser("command", help="a go for one whole command line, as run")
    c.add_argument("--command", required=True, type=_text, help="the whole Bash command line, exactly as run")
    c.add_argument("--by", required=True, type=_text, help="who gave the verdict")
    c.add_argument("--answer", required=True, type=_text, help="the answer file of the verdict (it must be on disk)")
    c.add_argument("--note", required=True, help="a note for the record")
    c.add_argument("--repo", type=_repo, help="OWNER/NAME; by default the origin remote's")
    c.add_argument("--slug", type=_text, help="the slug in the id (default: command)")
    c.add_argument("--undo", type=_text, help="the undo text (by default the go text)")
    c.add_argument("--dry-run", action="store_true", help="run every check and print the row; write nothing")
    w = sub.add_parser("withdraw", help="withdraw a row by its id")
    w.add_argument("id", type=_text, help="the id of the row, as the verb printed it")
    w.add_argument("--note", default="", help="why")
    w.add_argument("--dry-run", action="store_true", help="run every check and print the line; write nothing")
    return ap


@contextlib.contextmanager
def _locked(root):
    """An exclusive lock on the project folder, held from the check of a row to its append. The folder is the lock, so a refused row creates nothing."""
    fd = os.open(str(root), os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def _read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _append(path, text, line):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(("" if not text or text.endswith("\n") else "\n") + line + "\n")


def main(argv=None):
    """The verb: records a hold, a go or a command row, or withdraws one. Returns the exit code."""
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        a = _parser().parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2
    if fcntl is None:      # without the lock two writers could both pass the check: every verb refuses, a dry run included
        print("guard verdict: REFUSED: the lock is not available here (no fcntl module on this platform). Nothing was written.", file=sys.stderr)
        return 2
    try:
        cfg = config.load()
    except (Exception, SystemExit) as e:
        print(f"guard verdict: REFUSED: loop.json cannot be read ({type(e).__name__}: {e}). Nothing was written.", file=sys.stderr)
        return 2
    msg = config.no_project(cfg, "guard verdict")
    if msg:
        print(msg, file=sys.stderr)
        return 2
    path = cfg.path("verdicts")
    try:
        with _locked(cfg.root):
            text = _read(path)
            rows = parse_rows(text)
            if a.verb == "withdraw":
                row = withdrawal(a.id, rows=rows, note=a.note)
            elif a.verb == "command":
                row = command_row(command=a.command, by=a.by, answer=a.answer, note=a.note, rows=rows, root=cfg.root,
                                  repo=a.repo or origin_repo(cfg.root), slug=a.slug, undo=a.undo)
            else:
                row = merge_row(a.verb, head=a.head, base=a.base, branch=a.branch, by=a.by, answer=a.answer, note=a.note,
                                rows=rows, root=cfg.root, pr=a.pr, repo=a.repo or origin_repo(cfg.root), slug=a.slug,
                                tree=a.tree, tests=a.tests, undo=a.undo)
            line = json.dumps(row)      # ASCII only: a raw line separator inside a field would split the row, as splitlines() reads it
            if not a.dry_run:
                _append(path, text, line)
    except Refused as e:
        print(f"guard verdict: REFUSED: {e}. Nothing was written.", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as e:
        print(f"guard verdict: the verdict file {path} cannot be read or written ({type(e).__name__}: {e}); nothing was written", file=sys.stderr)
        return 2
    print(line)
    if a.dry_run:
        print("dry run: nothing written")
    elif a.verb == "withdraw":
        print(f"appended the withdrawal of {row['of']}")
    else:
        print(f"appended {row['id']}")
    return 0
