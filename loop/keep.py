"""keep: what a later session needs survives the machine. Three parts behind one verb: backup (loop/keep_backup.sh, run at
every stop: the transcripts, the extra folders of loop.json and the untracked files go to a branch of the project's
repository), restore (a tree of tools and state is copied into a destination: a newer tool wins, state is never
overwritten) and replay (files a session wrote outside git are rebuilt from the transcripts that the backup keeps).

INVARIANT: a backup says ok only after its push succeeded; a restore never overwrites a state file; a rebuild writes nothing outside its --out.
FAILS WHEN: a backup's LAST-RUN says ok while the push failed, a restore overwrites a state file, or a rebuilt path lands outside --out (loop/tests/test_keep.py).

usage:
  python3 -I bin/loop keep backup [--wait]
  python3 -I bin/loop keep restore SRC DEST
  python3 -I bin/loop keep replay rebuild (--ref REF | --transcript FILE [FILE ...]) --out DIR --root PREFIX
  python3 -I bin/loop keep replay copies --ref REF NAME [NAME ...]

replay rebuild applies, in time order: every Write (sets the text), every Edit (replaces old_string once, or everywhere with
replace_all) and every full Read (a Read with no offset and no limit, under 2000 lines: the text the file had at that
moment, which also catches changes made by shell commands). A call whose result was an error is skipped. A call that two
transcripts both recorded (a backup keeps the longer copy of a transcript that a compaction shortened, as *.until-<time>)
is applied once; the summary counts the copies skipped in duplicate_events_skipped.
It writes DIR/<path under the root> and DIR/MANIFEST.tsv with the columns in MANIFEST_HEADER.
replay copies lists every file of that name anywhere on the ref (sandbox copies in a backed-up scratchpad), largest first.
The repository the refs are read from is the project's root (loop.config). --root has no default: the path a session wrote
its files under is that session's, not a setting of the project.

It stops with an error, before it writes anything, when the ref cannot be read or holds no transcript: an unreadable
backup must not read as an empty one.

What it cannot do. A file made or changed only by a shell command and never read in full afterwards is missing or stale
(edits_not_fitting above 0 is the sign). A Read cuts lines of 2000 characters or more (flagged in long_line_may_be_cut).
Each file is only as fresh as its last Write, fitting Edit or full Read. Nothing is written outside --out: a path that
would land outside it (through "..", or through a symlink already in DIR) is left out and listed in refused_outside_out.
A rebuilt file named MANIFEST.tsv at the top of the root is written as MANIFEST.tsv.rebuilt.
The rebuilt files can hold the principal's data: keep DIR private."""
import argparse, collections, json, os, pathlib, re, shutil, subprocess, sys
from loop import config

REPO = None                                   # set by main() from the project's configuration: where the refs are read
KEEP_BACKUP = pathlib.Path(__file__).with_name("keep_backup.sh")
MANIFEST_HEADER = ["path", "bytes", "latest_source", "writes", "full_reads", "edits_applied", "edits_not_fitting",
                   "long_line_may_be_cut", "last_change_utc"]
NUMBERED = re.compile(r"^\s*(\d+)(?:\t|→)(.*)$", re.S)
READ_LIMIT = 2000
TOOL_SUFFIXES = (".py", ".js", ".sh", ".txt")  # restore: these are tools (newer wins); every other file is state


def git(*a):
    """stdout of a git command in the project's repository; a command that fails stops the run."""
    r = subprocess.run(["git", "-C", str(REPO), *a], capture_output=True)
    if r.returncode:
        raise SystemExit(f"git {' '.join(a)} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout


def ref_groups(ref):
    """{transcript: its parts in order} for every transcript kept on the ref. A transcript is one file, or one *.parts
    directory: NAME.jsonl.parts, and NAME.until-<time>.parts, the copy kept of a transcript that came back shorter."""
    groups = collections.defaultdict(list)
    for n in git("ls-tree", "-r", "--name-only", ref, "transcripts/").decode().split("\n"):
        if n:
            head, sep, _ = n.partition(".parts/")
            groups[head + sep if sep else n].append(n)
    return {g: sorted(p) for g, p in groups.items()}


def blob_lines(ref, parts):
    """The lines of one transcript that is stored as blobs (whole, or cut into parts at arbitrary bytes)."""
    buf = b""
    for part in parts:
        p = subprocess.Popen(["git", "-C", str(REPO), "cat-file", "blob", f"{ref}:{part}"], stdout=subprocess.PIPE)
        while True:
            chunk = p.stdout.read(1 << 22)
            if not chunk:
                break
            buf += chunk
            if b"\n" in buf:
                *ls, buf = buf.split(b"\n")
                yield from ls
        if p.wait():
            raise SystemExit(f"git cat-file blob {ref}:{part} failed")
    if buf:
        yield buf


def file_lines(path):
    with open(path, "rb") as f:
        for line in f:
            yield line.rstrip(b"\n")


def snapshot(content):
    """(text, long_line) from a Read result in `cat -n` form, or (None, False) when it is not a whole file."""
    t = content if isinstance(content, str) else "\n".join(
        x.get("text", "") for x in (content or []) if isinstance(x, dict) and x.get("type") == "text")
    out, want = [], 1
    for ln in t.split("\n"):
        m = NUMBERED.match(ln)
        if not m or int(m.group(1)) != want:
            break
        out.append(m.group(2))
        want += 1
    if not out or len(out) >= READ_LIMIT:
        return None, False
    return "\n".join(out) + "\n", any(len(x) >= READ_LIMIT for x in out)


def collect(lines, root, events, errs, seq):
    """Add one transcript's Write, Edit and full-Read events under `root` to `events`; returns the next sequence number."""
    pending = {}
    for raw in lines:
        if b'"tool_use"' not in raw and b'"tool_result"' not in raw:
            continue
        try:
            o = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(o, dict):
            continue
        ts = (o.get("timestamp") or "")[:23]
        c = (o.get("message") or {}).get("content")
        if not isinstance(c, list):
            continue
        for b in c:
            if not isinstance(b, dict):
                continue
            kind = b.get("type")
            if kind == "tool_result":
                i = b.get("tool_use_id")
                errs[i] = bool(b.get("is_error"))
                if i in pending and not b.get("is_error"):
                    text, long_line = snapshot(b.get("content"))
                    seq += 1
                    if text is not None:
                        events.append((ts, seq, pending[i], "R", text, long_line, False, i))
            elif kind == "tool_use":
                name, inp = b.get("name"), b.get("input") or {}
                p = inp.get("file_path") or ""
                p = os.path.normpath(p) if p else p   # "/a/../x" must not pass the prefix test below
                seq += 1
                if not p.startswith(root):
                    continue
                if name == "Write":
                    events.append((ts, seq, p, "W", inp.get("content", ""), None, False, b.get("id")))
                elif name == "Edit":
                    events.append((ts, seq, p, "E", inp.get("old_string", ""), inp.get("new_string", ""),
                                   bool(inp.get("replace_all")), b.get("id")))
                elif name == "Read" and not inp.get("offset") and not inp.get("limit"):
                    pending[b.get("id")] = p
    return seq


def apply(events, errs):
    """(state, meta): the text of every rebuilt path, and per path the counts the manifest reports. A call that two
    transcripts both recorded (the same tool-use id) is applied once: an Edit whose new text holds its old text would
    otherwise fit twice and double the insertion with no sign. meta[path]["dup"] counts the copies skipped."""
    state, seen = {}, set()
    meta = collections.defaultdict(lambda: dict(w=0, r=0, e=0, fail=0, long=0, dup=0, last="", src=""))
    for ts, _, p, op, a, b, replace_all, i in sorted(events, key=lambda e: (e[0], e[1])):
        m = meta[p]
        if i and (i, op) in seen:
            m["dup"] += 1
            continue
        seen.add((i, op))
        if op != "R" and errs.get(i) is True:
            continue
        if op == "W":
            state[p] = a; m["w"] += 1; m["last"] = ts; m["src"] = "write"; m["long"] = 0   # a Write replaces the whole text
        elif op == "R":
            if state.get(p) != a:
                state[p] = a; m["last"] = ts; m["src"] = "read"; m["long"] = int(bool(b))
            m["r"] += 1
        elif p not in state or a not in state[p]:
            m["fail"] += 1
        else:
            state[p] = state[p].replace(a, b) if replace_all else state[p].replace(a, b, 1)
            m["e"] += 1; m["last"] = ts
            if not m["src"].endswith("+edit"):
                m["src"] += "+edit"
    return state, meta


def write_out(state, meta, out, root, refused=None):
    """Write every rebuilt file under `out`, then the manifest; returns the manifest rows. A path that would land outside
    `out` is not written and is appended to `refused`."""
    base = os.path.realpath(out)
    rows = []
    for p, text in state.items():
        rel = p[len(root):].lstrip("/")
        if rel == "MANIFEST.tsv":
            rel = "MANIFEST.tsv.rebuilt"   # this run's manifest takes the plain name
        dest = os.path.realpath(os.path.join(base, rel))   # realpath: neither ".." nor a symlink inside `out` leads outside it
        if not dest.startswith(base + os.sep):
            if refused is not None:
                refused.append(p)
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(text)
        m = meta[p]
        rows.append((rel, len(text.encode("utf-8")), m["src"], m["w"], m["r"], m["e"], m["fail"], m["long"], m["last"][:16]))
    rows.sort()
    with open(os.path.join(base, "MANIFEST.tsv"), "w", encoding="utf-8") as f:
        f.write("\t".join(MANIFEST_HEADER) + "\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    return rows


def rebuild(a):
    root = a.root if a.root.endswith("/") else a.root + "/"
    if a.transcript:
        sources = [file_lines(path) for path in a.transcript]
    else:
        groups = ref_groups(a.ref)
        if not groups:
            raise SystemExit(f"no transcript under transcripts/ on {a.ref}")
        sources = [blob_lines(a.ref, parts) for parts in groups.values()]
    events, errs, seq = [], {}, 0
    for lines in sources:
        seq = collect(lines, root, events, errs, seq)
    state, meta = apply(events, errs)
    os.makedirs(a.out, exist_ok=True)
    refused = []
    rows = write_out(state, meta, a.out, root, refused)
    lost = sorted(p[len(root):] for p in meta if p not in state)
    print(json.dumps(dict(transcripts=len(sources), events=len(events), files=len(rows), bytes=sum(r[1] for r in rows),
                          from_full_read=sum(1 for r in rows if r[2].startswith("read")),
                          edits_not_fitting=sum(1 for r in rows if r[6]), long_line_flags=sum(1 for r in rows if r[7]),
                          duplicate_events_skipped=sum(m["dup"] for m in meta.values()),
                          refused_outside_out=sorted(refused), edited_but_never_written=lost)))


def copies(a):
    for name in a.name:
        hits = []
        for line in git("ls-tree", "-r", "-l", a.ref).decode("utf-8", "replace").split("\n"):
            head, _, path = line.partition("\t")
            if path == name or path.endswith("/" + name):
                hits.append((int(head.split()[3]), path))
        for size, path in sorted(hits, reverse=True):
            print(f"{size}\t{path}")
        if not hits:
            print(f"0\t(no file named {name} on {a.ref})")


def _abs(cfg, p):
    """A configured path: "~" is expanded, a relative path is under the project's root."""
    q = pathlib.Path(os.path.expanduser(str(p)))
    return str(q if q.is_absolute() else cfg.root / q)


def session_id(transcript):
    """The name a backup gives a session: the first eight characters of its transcript's file name. None when none is named."""
    name = os.path.basename(str(transcript)) if isinstance(transcript, (str, os.PathLike)) else ""
    return (name[:-6] if name.endswith(".jsonl") else name)[:8] or None


def last_run(cfg, sid=None):
    """The first line of a backup's LAST-RUN file: "ok T", "running since T" or "FAILED T: step ...". Each session has its own
    backup worktree (state_dir/backup-wt-<sid>), so that a second session of a project does not fail on the first one's
    branch: with a sid, that session's last run; without, the newest of any session. "" when there is none. Read without
    creating the state directory, so that doctor and the prompt hook can call it."""
    try:
        d = cfg.path("state_dir")
        runs = [d / f"backup-wt-{sid}" / "LAST-RUN"] if sid else sorted(d.glob("backup-wt-*/LAST-RUN"), key=lambda p: p.stat().st_mtime)
        return runs[-1].read_text(encoding="utf-8").split("\n")[0] if runs else ""
    except OSError:
        return ""


def backup(a):
    """Run keep_backup.sh with the project's settings in its environment. The script exits 0 however the run went, so that
    a stop is never held by a backup; a waited run returns 1 when LAST-RUN says FAILED, and says why on standard error."""
    cfg = config.load()
    why = config.no_project(cfg, "keep backup")
    if why:
        print(why, file=sys.stderr)
        return 1
    b = cfg["backup"]
    if not str(b["remote"]).strip():
        print("keep backup: no remote is named (loop.json: backup.remote); nothing was kept. A backup holds the session's "
              "transcripts and the untracked files, so it goes only where the project says: name a private remote.", file=sys.stderr)
        return 1
    t = cfg.transcript()
    if t is None or not t.is_file():
        print('keep backup: no transcript is named (set LOOP_TRANSCRIPT: a hook passes the one its event names; with "sessions": '
              '"all" in loop.json every transcript on this machine is kept); nothing was kept.', file=sys.stderr)
        return 1
    env = {**os.environ, "LOOP_TRANSCRIPT": str(t), "LOOP_SESSIONS": str(cfg["sessions"]), "LOOP_ROOT": str(cfg.root), "LOOP_REMOTE": str(b["remote"]), "LOOP_PREFIX": str(b["prefix"]),
           "LOOP_EXTRA_DIRS": "\n".join(_abs(cfg, p) for p in b["extra_dirs"]),
           "LOOP_TRANSCRIPTS_DIR": str(cfg.transcripts_dir()), "LOOP_STATE_DIR": str(cfg.state())}
    try:
        rc = subprocess.run(["bash", str(KEEP_BACKUP), *(["--wait"] if a.wait else [])], env=env).returncode
    except OSError as e:
        print(f"keep backup: cannot run {KEEP_BACKUP.name}: {e}", file=sys.stderr)
        return 1
    last = last_run(cfg, session_id(t))
    if a.wait and rc == 0 and last.startswith("FAILED"):
        print(f"keep backup: {last}", file=sys.stderr)
        return 1
    return rc


def restore(a):
    """Copy the tree SRC into DEST. A tool (a file ending in TOOL_SUFFIXES) is copied when it is missing in DEST or older
    there; every other file is state and is copied only when it is missing. Prints {"copied": n, "kept": m} as one JSON line."""
    src, dest = pathlib.Path(a.src), pathlib.Path(a.dest)
    if not src.is_dir():
        print(f"keep restore: no tree at {src}; nothing was copied", file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    copied = kept = 0
    for f in sorted(p for p in src.rglob("*") if p.is_file() and ".git" not in p.relative_to(src).parts):
        d = dest / f.relative_to(src)
        if not d.exists() or (f.suffix in TOOL_SUFFIXES and f.stat().st_mtime > d.stat().st_mtime):
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, d)
            copied += 1
        else:
            kept += 1
    print(json.dumps({"copied": copied, "kept": kept}))
    return 0


def main(argv=None):
    global REPO
    ap = argparse.ArgumentParser(prog="loop keep", description="keep: backup, restore and replay of what a session needs")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backup", help="back up the transcripts, the extra folders and the untracked files to a backup branch")
    b.add_argument("--wait", action="store_true", help="hold until the backup has ended")
    s = sub.add_parser("restore", help="copy the tree SRC into DEST: a newer tool wins, state is never overwritten")
    s.add_argument("src")
    s.add_argument("dest")
    rp = sub.add_parser("replay", help="rebuild files from the transcripts, or list the copies of a name on a ref")
    ops = rp.add_subparsers(dest="op", required=True)
    r = ops.add_parser("rebuild", help="rebuild the files a session wrote outside git")
    src = r.add_mutually_exclusive_group(required=True)
    src.add_argument("--ref")
    src.add_argument("--transcript", nargs="+")
    r.add_argument("--out", required=True)
    r.add_argument("--root", required=True, help="the path prefix the session wrote its files under (no default)")
    c = ops.add_parser("copies", help="every file of that name on the ref, largest first")
    c.add_argument("--ref", required=True)
    c.add_argument("name", nargs="+")
    a = ap.parse_args(argv)
    if a.cmd == "backup":
        return backup(a)
    if a.cmd == "restore":
        return restore(a)
    REPO = config.load().root
    (rebuild if a.op == "rebuild" else copies)(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
