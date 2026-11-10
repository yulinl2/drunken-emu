"""The watched files, judged through their checks: a changed file gets a verdict, the verdict reaches the session after the
tool call that changed the file, and a stop is refused while the newest verdict of a watched file fails, could not be
made, or is dominated.

A watch entry in loop.json is {"name", "files": [glob, ...], "run": [word, ...]}. `run` is one command, run in the
project root, in which the word {path} stands for the judged file. Its verdict follows the contract of the checks: exit 0
is a pass, exit 3 is not evaluated (a layer could not run), any other exit is a fail. The last non-empty line of its
standard output may be one JSON object: "vector" (numbers, every axis lower is better), "layers" (layer name to status
word) and "gate" (where it disagrees with the exit code, the exit code counts). Everything else it prints is for a person.

Records go to .loop/watch.jsonl, which is only appended to; a judged file is kept under .loop/cand/ by its hash. Among the
passing candidates of one check, path and command, one that another dominates (no worse on every axis, better on one) is
a regression, and a regression is not a pass.

INVARIANT: a changed watched file gets a verdict from its check before the session can stop; the verdict reaches the
session's context after the tool call that changed the file; a stop is refused, up to stop_cap times, while the newest
verdict of a watched file fails, could not be made, or is dominated.
FAILS WHEN: a watched file's bytes changed and the next stop passes with no record for those bytes; a verdict is reused
for other bytes or another command; a check that could not run reads as a pass (loop/tests/test_watch.py).

usage: python3 -I bin/loop watch eval [PATH ...]   judge now, every watched file or the PATHs (relative to the project
                                                   root): exit 0 pass, 1 fail or dominated, 3 not evaluated, 2 a PATH
                                                   that is not watched
       python3 -I bin/loop watch status            the newest record of each watched file; writes nothing
"""
import argparse, datetime, fnmatch, glob, hashlib, json, os, re, subprocess, sys

from loop import config

LEDGER = "watch.jsonl"          # append-only, in the state folder
CAND = "cand"                   # the judged bytes, kept under their hash
SNAP_MAX = 4 << 20              # a larger file is judged but not copied, so it has no restore hint
TAIL_LINES, TAIL_CHARS = 20, 2000
LOCK_WAIT_S = 5                 # the longest a judging waits for watch.lock, then judges without it (no DEFAULTS key: a constant of the kit)
MAGIC = re.compile(r"[*?[]")
WORD = {"pass": "PASS", "fail": "FAIL", "not_evaluated": "NOT EVALUATED"}
GATE_OF_EXIT = {0: "pass", 3: "not_evaluated"}   # any other exit is a fail


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def fmt(v):
    return f"{v:g}" if isinstance(v, (int, float)) else str(v)


def fmtvec(v):
    return " ".join(f"{k}={fmt(x)}" for k, x in sorted(v.items())) or "(no axis scored)"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


def command_hash(run):
    """The hash of the JSON of `run`: what a verdict was computed under."""
    return hashlib.sha256(json.dumps(run, ensure_ascii=False).encode("utf-8")).hexdigest()


def dominates(a, b):
    """a is no worse than b on every shared axis and better on one (every axis lower-is-better)."""
    keys = set(a) & set(b)
    return bool(keys) and all(a[k] <= b[k] for k in keys) and any(a[k] < b[k] for k in keys)


def frontier(recs):
    """The passing candidates that no other passing candidate dominates. A candidate counts at its newest record: a
    re-evaluation supersedes an older verdict, so a PASS that a later FAIL replaced is no baseline (the older line stays)."""
    newest_of = {}
    for r in recs:                  # ledger order: the last record of each bytes wins
        newest_of[r["sha"]] = r
    items = [r for r in newest_of.values() if r["gate"] == "pass"]
    return [r for r in items if not any(dominates(o["vector"], r["vector"]) for o in items if o is not r)]


def dominator(rec, ledger):
    """The record of a candidate that dominates rec now: same check, path and command, other bytes, passing at its newest
    record. Computed when a decision needs it, so a verdict that changed after rec was written counts."""
    pool = [r for r in ledger if (r["check"], r["path"], r["config"]) == (rec["check"], rec["path"], rec["config"])
            and r["sha"] != rec["sha"]]
    return next((r for r in frontier(pool) if dominates(r["vector"], rec["vector"])), None)


def _word(rec):
    """The gate in capitals. A pass that another record dominates is a REGRESSION: the stop counts it as a failure."""
    return "REGRESSION" if rec["gate"] == "pass" and rec.get("dominated_by") else WORD[rec["gate"]]


def current(cfg, rec):
    """rec with its dominance as of now (a pass only): a baseline may have been re-evaluated since rec was written."""
    if rec["gate"] != "pass":
        return rec
    dom = dominator(rec, read_ledger(cfg))
    return {**rec, "dominated_by": dom["id"] if dom else None}


def ledger_path(cfg):
    return cfg.path("state_dir") / LEDGER     # reading makes no folder: status writes nothing


def read_ledger(cfg):
    path = ledger_path(cfg)
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append(cfg, rec):
    cfg.state()                               # the state folder, kept out of git status
    with open(ledger_path(cfg), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


def newest(cfg, entry, path):
    return next((r for r in reversed(read_ledger(cfg)) if r["check"] == entry["name"] and r["path"] == path), None)


def _covers(path, files):
    """Whether the entry's files name this path: an exact name, or a glob (with ** also read as zero folders)."""
    for pat in files:
        if MAGIC.search(pat):
            if fnmatch.fnmatchcase(path, pat) or fnmatch.fnmatchcase(path, pat.replace("**/", "")):
                return True
        elif path == os.path.normpath(pat):
            return True
    return False


def candidates(cfg, entry):
    """The project-relative paths one entry judges now: the files its patterns find, an exact name whether or not the file
    exists, and each path it judged before that is gone now and still named (a deleted or renamed file is no pass)."""
    found = set()
    for pat in entry["files"]:
        if MAGIC.search(pat):
            found |= {os.path.relpath(p, cfg.root) for p in glob.glob(os.path.join(str(cfg.root), pat), recursive=True)
                      if os.path.isfile(p)}
        else:
            found.add(os.path.normpath(pat))
    gone = {r["path"] for r in read_ledger(cfg) if r["check"] == entry["name"] and not (cfg.root / r["path"]).is_file()}
    return sorted(found | {p for p in gone if _covers(p, entry["files"])})


def held(cfg, rec):
    """The copy a record names, when it exists and holds the whole candidate (its bytes hash to the record's sha); else None."""
    snap = rec.get("snapshot")
    if not snap or not rec.get("sha") or not (cfg.root / snap).is_file():
        return None
    return snap if sha256_file(cfg.root / snap) == rec["sha"] else None


def _snapshot(cfg, path, data):
    """The judged bytes, copied once to .loop/cand/ under the first 12 hex digits of their hash; None when they were not read."""
    if data is None:
        return None
    cand = cfg.state() / CAND
    cand.mkdir(exist_ok=True)
    dest = cand / (hashlib.sha256(data).hexdigest()[:12] + os.path.splitext(path)[1])
    if not dest.exists():
        dest.write_bytes(data)
    return os.path.relpath(dest, cfg.root)


def _json_line(text):
    """The last non-empty line of a check's standard output, when it is one JSON object; else {}."""
    lines = [x for x in text.splitlines() if x.strip()]
    try:
        obj = json.loads(lines[-1]) if lines else {}
    except ValueError:
        return {}
    return obj if isinstance(obj, dict) else {}


def _judge(cfg, entry, path):
    """Runs the entry's command on one file: (gate, vector, layers, tail). A command that cannot start, or that outlasts the
    time limit, is not evaluated."""
    from loop import hook   # hook imports this module, so the time limit is read here
    argv = [w.replace("{path}", path) for w in entry["run"]]
    try:
        r = subprocess.run(argv, cwd=str(cfg.root), env={**os.environ, "LOOP_PROJECT": str(cfg.root)}, stdin=subprocess.DEVNULL,
                           capture_output=True, encoding="utf-8", errors="replace", timeout=hook.STEP_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return "not_evaluated", {}, {}, f"no result within {hook.STEP_TIMEOUT_S} s"
    except OSError as e:
        return "not_evaluated", {}, {}, f"could not start: {e}"
    text = "\n".join(s.rstrip() for s in (r.stdout, r.stderr) if s and s.strip())
    tail = "\n".join(text.splitlines()[-TAIL_LINES:])[-TAIL_CHARS:]
    obj = _json_line(r.stdout)
    vector = {}
    if isinstance(obj.get("vector"), dict):
        vector = {k: v for k, v in obj["vector"].items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    layers = {str(k): str(v) for k, v in obj["layers"].items()} if isinstance(obj.get("layers"), dict) else {}
    return GATE_OF_EXIT.get(r.returncode, "fail"), vector, layers, tail


def evaluate(cfg, entry, path, trigger, force=False):
    """Judges one file unless its newest record has the same two hashes (the bytes and the command): then None, and nothing
    new is said. At a stop, a newest record that is not evaluated is judged again. Returns the new record."""
    ledger = read_ledger(cfg)
    same = [r for r in ledger if r["check"] == entry["name"] and r["path"] == path]
    prev = same[-1] if same else None
    full, data = cfg.root / path, None
    if full.is_file():
        data = full.read_bytes() if full.stat().st_size <= SNAP_MAX else None
        sha = hashlib.sha256(data).hexdigest() if data is not None else sha256_file(full)
    else:
        sha = None
    chash = command_hash(entry["run"])
    if (prev and not force and prev["sha"] == sha and prev["config"] == chash
            and not (trigger == "stop" and prev["gate"] == "not_evaluated")):
        return None
    if sha is None:
        gate, vector, layers, tail = "not_evaluated", {}, {}, ""
    else:
        gate, vector, layers, tail = _judge(cfg, entry, path)
        if (sha256_file(full) if full.is_file() else None) != sha:   # the bytes changed under the check: not this verdict
            gate, vector, layers, tail = "not_evaluated", {}, {}, "the file changed while its check ran; it is judged again"
    rec = {"at": now(), "id": None, "check": entry["name"], "path": path, "sha": sha, "config": chash, "gate": gate,
           "vector": vector, "layers": layers, "tail": tail, "trigger": trigger,
           "supersedes": prev["id"] if prev else None, "dominated_by": None,
           "snapshot": _snapshot(cfg, path, data) if sha is not None else None}
    if gate == "pass":
        dom = dominator(rec, ledger)
        rec["dominated_by"] = dom["id"] if dom else None
    rec["id"] = hashlib.sha256(f"{path}|{sha}|{chash}|{rec['at']}|{len(ledger)}|{trigger}".encode("utf-8")).hexdigest()[:8]
    append(cfg, rec)
    return rec


def _compare(prev, rec):
    line = f"  previous @{(prev['sha'] or 'absent')[:8]}: {WORD[prev['gate']]} (record {prev['id']})"
    if prev["vector"] and rec["vector"]:
        keys = sorted(set(prev["vector"]) & set(rec["vector"]))
        moved = [f"{k} {fmt(prev['vector'][k])}->{fmt(rec['vector'][k])}" for k in keys if prev["vector"][k] != rec["vector"][k]]
        how = ("improved" if dominates(rec["vector"], prev["vector"]) else
               "worse" if dominates(prev["vector"], rec["vector"]) else "mixed" if moved else "unchanged")
        line += f"; this is {how}" + (f" ({', '.join(moved)})" if moved else "")
    return line


def block(cfg, rec, refusals=True):
    """What the session is told about one record, as plain lines: the check and the file, the gate in capitals, the layers
    that ran and those that did not, the vector, the output of a fail or a not evaluated, the record that dominates a
    dominated pass (and its copy, if that exists), the previous verdict of this file under this command, and the stop
    refusals used against the cap (not in a block made for a stop: _decide counts that refusal after the block exists, and
    says "refusal n of cap" itself)."""
    from loop import hook   # hook imports this module
    ledger = read_ledger(cfg)
    same = [r for r in ledger if (r["check"], r["path"], r["config"]) == (rec["check"], rec["path"], rec["config"])]
    pos = [r["id"] for r in same].index(rec["id"])
    used = f"; stop refusals used {hook._stop_state(cfg.state('stop-refusals.json'))['refused']}/{cfg['stop_cap']}" if refusals else ""
    sha = rec["sha"][:8] if rec["sha"] else "absent"
    out = [f"watch {rec['check']} {rec['path']} @{sha}: {_word(rec)} (record {rec['id']}, {rec['trigger']}; "
           f"evaluation {pos + 1} of this file under this command{used})"]
    ran = [f"{k} {v}" for k, v in rec["layers"].items() if v != "not_evaluated"]
    out.append("  layers run: " + ("; ".join(ran) if ran else "none reported"))
    skipped = [k for k, v in rec["layers"].items() if v == "not_evaluated"]
    if skipped:
        out.append("  layers not run: " + ", ".join(skipped))
    if rec["vector"]:
        out.append("  vector (lower is better): " + fmtvec(rec["vector"]))
    if pos:
        out.append(_compare(same[pos - 1], rec))
    if rec["gate"] != "pass" and rec["tail"]:
        out += ["  output, last lines:"] + ["    " + line for line in rec["tail"].splitlines()]
    if rec["sha"] is None:
        copy = next((r for r in reversed(ledger) if (r["check"], r["path"]) == (rec["check"], rec["path"]) and held(cfg, r)), None)
        hint = f" Restore the last evaluated copy: cp {copy['snapshot']} {rec['path']}." if copy else ""
        out.append("  the file is gone (deleted or renamed), and a missing file is not a pass." + hint)
    if rec["gate"] == "pass" and rec["dominated_by"]:
        dom = next(r for r in ledger if r["id"] == rec["dominated_by"])
        out.append(f"  REGRESSION: record {dom['id']} ({fmtvec(dom['vector'])}) is no worse on every axis and better on one.")
        if held(cfg, dom):
            out.append(f"  Its copy: {dom['snapshot']}. Restore it: cp {dom['snapshot']} {rec['path']}")
    return "\n".join(out)


def _lock(cfg):
    from loop import hook   # hook imports this module
    return hook._locked(cfg, "watch.lock", LOCK_WAIT_S)


def post(cfg):
    """The blocks the post hook says: every watched file judged now (trigger post); a block only where a new record was made."""
    out = []
    with _lock(cfg):
        for entry in cfg["watch"]:
            for path in candidates(cfg, entry):
                rec = evaluate(cfg, entry, path, "post")
                if rec:
                    out.append(block(cfg, rec))
    return out


def stop(cfg):
    """What a stop is told: the watched files judged now (trigger stop), each newest record with its dominance as of now,
    sorted into failed (a dominated pass counts), did_not_run and passed, with the block of each as it was said."""
    res = {"failed": [], "did_not_run": [], "passed": [], "said": []}
    with _lock(cfg):
        for entry in cfg["watch"]:
            for path in candidates(cfg, entry):
                evaluate(cfg, entry, path, "stop")
                rec = current(cfg, newest(cfg, entry, path))
                name = f"watch {entry['name']} {path}"
                if rec["gate"] == "pass" and not rec["dominated_by"]:
                    bucket = "passed"
                elif rec["gate"] == "not_evaluated":
                    bucket = "did_not_run"
                else:
                    bucket = "failed"
                res[bucket].append(name)
                res["said"].append((name, block(cfg, rec, refusals=False)))
    return res


def _targets(cfg):
    return [(entry, path) for entry in cfg["watch"] for path in candidates(cfg, entry)]


def _exit(recs):
    if any(r["gate"] == "fail" or r["dominated_by"] for r in recs):
        return 1
    return 3 if any(r["gate"] == "not_evaluated" for r in recs) else 0


def _eval(cfg, names):
    wanted = [os.path.normpath(os.path.relpath(os.path.join(str(cfg.root), n), str(cfg.root))) for n in names]
    targets = _targets(cfg)
    watched = {p for _, p in targets}
    unknown = [n for n, w in zip(names, wanted) if w not in watched]
    if unknown:
        print("watch eval: not watched: " + ", ".join(unknown), file=sys.stderr)
        return 2
    picked = [(entry, path) for entry, path in targets if not wanted or path in wanted]
    if not picked:
        print("watch eval: no watched file to judge")
        return 0
    recs = []
    with _lock(cfg):
        for entry, path in picked:
            recs.append(current(cfg, evaluate(cfg, entry, path, "manual", force=True)))
    print("\n\n".join(block(cfg, rec) for rec in recs))
    return _exit(recs)


def _status(cfg):
    for entry in cfg["watch"]:
        for path in candidates(cfg, entry):
            rec = newest(cfg, entry, path)
            if rec is None:
                print(f"watch {entry['name']} {path}: no record yet")
                continue
            rec = current(cfg, rec)
            sha = rec["sha"][:8] if rec["sha"] else "absent"
            dom = f"; dominated by record {rec['dominated_by']}" if rec["dominated_by"] else ""
            print(f"watch {entry['name']} {path}: {_word(rec)} @{sha} (record {rec['id']}, {rec['trigger']}; "
                  f"{fmtvec(rec['vector'])}){dom}")
    return 0


def main(argv=None):
    """`bin/loop watch eval [PATH ...]` and `bin/loop watch status`: returns the exit code."""
    argv = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(prog="loop watch", description="judge the watched files through their checks")
    sub = p.add_subparsers(dest="cmd", required=True, metavar="SUBCOMMAND")
    e = sub.add_parser("eval", help="judge the watched files now (or the PATHs given) and print the verdicts")
    e.add_argument("paths", nargs="*", metavar="PATH")
    sub.add_parser("status", help="the newest record of each watched file; writes nothing")
    try:
        args = p.parse_args(argv)
    except SystemExit as ex:
        return int(ex.code or 0)
    cfg = config.load()
    if not cfg["watch"]:
        print("watch: nothing is watched (loop.json names no watch entry)")
        return 0
    return _status(cfg) if args.cmd == "status" else _eval(cfg, args.paths)
