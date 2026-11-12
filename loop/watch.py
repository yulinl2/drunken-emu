"""The watched files, judged through their checks: a changed watched file gets a verdict, the verdict reaches the session after the
tool call that changed the file, and a stop is refused while the newest verdict of a watched file fails, could not be made, or is
dominated.

A watch entry in loop.json is {"name", "files": [glob, ...], "run": [word, ...]} and may add "inputs": [glob, ...]. `run` is one
command, run in the project root, in which the word {path} stands for the judged file. Its verdict follows the contract of the
checks: exit 0 is a pass, exit 3 is not evaluated (a layer could not run), any other exit is a fail. The last non-empty line of its
standard output may be one JSON object: "vector" (numbers, every axis lower is better), "layers" (layer name to status word) and
"gate" (where it disagrees with the exit code, the exit code counts). Everything else it prints is for a person.

The bytes of the files that `inputs` globs match (sorted by path; each as its path and the hash of its bytes) are part of the
candidate a verdict is for, so a changed input means no record for those bytes and the watched file is judged again.
A watched file or an input that changes while its check runs gets no verdict from that run. A glob that
matches no file is said by `eval` and `status`. A PASS says what its check did not run when an installed report reader
recognizes it; otherwise coverage beyond reported layers is unknown (or it reports no layers).

Records go to .loop/watch.jsonl, which is only appended to; a judged file is kept under .loop/cand/ by its hash. A line of the
ledger that is not a record (RECORD_KEYS) is skipped and said, and the bytes it was for are judged again. Among the passing
candidates of one check, path and command, one that another dominates (no worse on every axis, better on one) is a regression, and
a regression is not a pass. A post or a stop judges within its hook's time budget (loop/hook.py): what runs past it is not
evaluated, out of time.

INVARIANT: a changed watched file, or a changed input it names, gets a verdict from its check before the session can stop; the
verdict reaches the session's context after the tool call that changed the file; a stop is refused, up to stop_cap times, while
the newest verdict of a watched file fails, could not be made (out of time, lock held, a check that did not run) or is dominated;
a PASS says what its check did not run.
FAILS WHEN: a watched file's bytes or an input's changed and the next stop passes with no record for those bytes; a verdict is
reused for other bytes, inputs or another command; a ledger line that is not a record is read as one; a check that could not run
reads as a pass; a PASS does not say what did not run; a restore hint names a copy that is not the whole candidate (loop/tests/test_watch.py).

usage: python3 -I bin/loop watch eval [PATH ...]   judge now, every watched file or the PATHs (relative to the project
                                                   root): exit 0 pass, 1 fail or dominated, 3 not evaluated, 2 a PATH
                                                   that is not watched
       python3 -I bin/loop watch status            the newest record of each watched file; writes nothing
"""
import argparse, datetime, fnmatch, glob, hashlib, json, os, re, subprocess, sys, time

from loop import config
from loop.adapters import pass_note

LEDGER = "watch.jsonl"          # append-only, in the state folder
RECORD_KEYS = ("at", "id", "check", "path", "sha", "config", "gate", "vector", "layers", "tail", "trigger", "supersedes",
               "dominated_by", "snapshot")   # every key a record has (evaluate writes them all): a ledger line without them is no record
CAND = "cand"                   # the judged bytes, kept under their hash
SNAP_MAX = 4 << 20              # a larger file is judged but not copied, so it has no restore hint
TAIL_LINES, TAIL_CHARS = 20, 2000
LOCK_WAIT_S = 5                 # the longest `eval` waits for watch.lock, then says not evaluated (lock held) (no DEFAULTS key: a constant of the kit)
SKIPPED_SHOWN = 10              # how many skipped ledger lines one message names, by number
MAGIC = re.compile(r"[*?[]")
WORD = {"pass": "PASS", "fail": "FAIL", "not_evaluated": "NOT EVALUATED"}
GATE_OF_EXIT = {0: "pass", 3: "not_evaluated"}   # any other exit is a fail
OUT_OF_TIME = "not evaluated (out of time): the hook's time budget ran out before this file was judged"
OUT_OF_TIME_CHECK = "not evaluated (out of time): the hook's time budget ran out while the check ran"
NOTE_MISSING = "what did not run was not recorded"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _say(msg):
    print(msg, file=sys.stderr)


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


def cand_of(rec):
    """The candidate a record is for: the hash of its watched file's bytes, or for an entry with inputs, the hash `cand` that also
    holds the inputs. A record made before inputs existed has no `cand`, and its candidate is its bytes."""
    return rec.get("cand", rec["sha"])


def cand_sha(sha, inputs):
    """The candidate's hash: the watched file's hash (None when the file is gone) with each input's path and hash. With no inputs it is
    the file's own hash, so a record made before inputs existed still covers its candidate."""
    if not inputs:
        return sha
    return hashlib.sha256(json.dumps({"file": sha, "inputs": inputs}, sort_keys=True).encode("utf-8")).hexdigest()


def frontier(recs):
    """The passing candidates that no other passing candidate dominates. A candidate counts at its newest record: a
    re-evaluation supersedes an older verdict, so a PASS that a later FAIL replaced is no baseline (the older line stays)."""
    newest_of = {}
    for r in recs:                  # ledger order: the last record of each candidate wins
        newest_of[cand_of(r)] = r
    items = [r for r in newest_of.values() if r["gate"] == "pass"]
    return [r for r in items if not any(dominates(o["vector"], r["vector"]) for o in items if o is not r)]


def dominator(rec, ledger):
    """The record of a candidate that dominates rec now: same check, path and command, other candidate, passing at its newest
    record. Computed when a decision needs it, so a verdict that changed after rec was written counts."""
    pool = [r for r in ledger if (r["check"], r["path"], r["config"]) == (rec["check"], rec["path"], rec["config"])
            and cand_of(r) != cand_of(rec)]
    return next((r for r in frontier(pool) if dominates(r["vector"], rec["vector"])), None)


def _note_of(rec):
    """What a PASS record says it did not run; a record made before the note existed says that it was not recorded."""
    return rec.get("note") or NOTE_MISSING


def _gate_word(rec):
    """The gate in capitals. A PASS says what its check did not run (_note_of)."""
    return f"PASS ({_note_of(rec)})" if rec["gate"] == "pass" else WORD[rec["gate"]]


def _word(rec):
    """`_gate_word`, except that a pass another record dominates is a REGRESSION: the stop counts it as a failure."""
    return "REGRESSION" if rec["gate"] == "pass" and rec.get("dominated_by") else _gate_word(rec)


def current(cfg, rec):
    """rec with its dominance as of now (a pass only): a baseline may have been re-evaluated since rec was written."""
    if rec["gate"] != "pass":
        return rec
    dom = dominator(rec, read_ledger(cfg))
    return {**rec, "dominated_by": dom["id"] if dom else None}


def ledger_path(cfg):
    return cfg.path("state_dir") / LEDGER     # reading makes no folder: status writes nothing


def read_ledger(cfg):
    """The records of the ledger, in order. A line that is not a record (a torn write, a line of another kind, a JSON object without
    RECORD_KEYS) is skipped: its record is gone, so the bytes it was for have no record and are judged again. A run that reads the
    ledger says how many lines it skipped, once: the config object of the run remembers that it said so."""
    path = ledger_path(cfg)
    if not path.is_file():
        return []
    recs, skipped = [], []
    for n, line in enumerate(path.read_bytes().split(b"\n"), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line.decode("utf-8"))   # a cut multi-byte character is a ValueError too
        except ValueError:
            obj = None
        if isinstance(obj, dict) and all(k in obj for k in RECORD_KEYS):
            recs.append(obj)
        else:
            skipped.append(n)
    if skipped and not getattr(cfg, "said_skipped", False):
        cfg.said_skipped = True
        named = ", ".join(f"line {n}" for n in skipped[:SKIPPED_SHOWN]) + (", ..." if len(skipped) > SKIPPED_SHOWN else "")
        _say(f"watch ledger: {len(skipped)} unreadable line(s) skipped: {named}")
    return recs


def append(cfg, rec):
    """Appends the record as one line. A ledger that ends in a torn line (no newline) gets its line ended first, so that the record is a
    line of its own and not a second half of the torn one (which would make both unreadable)."""
    cfg.state()                               # the state folder, kept out of git status
    path, lead = ledger_path(cfg), ""
    if path.is_file() and path.stat().st_size:
        with open(path, "rb") as f:
            f.seek(-1, os.SEEK_END)
            lead = "" if f.read(1) == b"\n" else "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(lead + json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


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


def _glob_inputs(cfg, pat):
    """The files one inputs glob matches now. Never a file of the state folder: its files change with every judgement, so a glob that
    reached them (state_dir need not be a hidden folder) would judge every watched file again at every call."""
    state = os.path.realpath(str(cfg.path("state_dir"))) + os.sep
    return [p for p in glob.glob(os.path.join(str(cfg.root), pat), recursive=True)
            if os.path.isfile(p) and not os.path.realpath(p).startswith(state)]


def _inputs_files(cfg, entry):
    """The files the entry's inputs globs match now, by project-relative path (each once)."""
    found = {}
    for pat in entry.get("inputs", []):
        for p in _glob_inputs(cfg, pat):
            found[os.path.relpath(p, cfg.root)] = p
    return found


def inputs_of(cfg, entry):
    """The inputs of an entry now: [path, sha256 of the bytes] of every file its inputs globs match, sorted by path. Empty when the
    entry names no inputs, or when none of its globs matches a file."""
    found = _inputs_files(cfg, entry)
    return [[rel, sha256_file(found[rel])] for rel in sorted(found)]


def unmatched_inputs(cfg):
    """(entry name, glob) of each input glob that matches no file now."""
    return [(entry["name"], pat) for entry in cfg["watch"] for pat in entry.get("inputs", []) if not _glob_inputs(cfg, pat)]


def held(cfg, rec):
    """The copy a record names, when it exists and holds the watched file's bytes (their hash is the record's sha); else None."""
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


def _limit(deadline):
    """The longest one check may run now, and whether the hook's budget (not the time limit) is what would cut it."""
    from loop import hook   # hook imports this module
    if deadline is None:
        return hook.STEP_TIMEOUT_S, False
    left = deadline - time.monotonic()
    return (left, True) if left < hook.STEP_TIMEOUT_S else (hook.STEP_TIMEOUT_S, False)


def _judge(cfg, entry, path, deadline=None):
    """Runs the entry's command on one file: (gate, vector, layers, tail, note). A command that cannot start, that outlasts the time
    limit, or that outlasts what is left of the hook's budget (deadline, a time.monotonic() value; None: no budget) is not evaluated.
    A pass carries the note of what it did not run."""
    from loop import hook   # hook imports this module, so the time limit is read here
    limit, cut = _limit(deadline)
    if limit <= 0:
        return "not_evaluated", {}, {}, OUT_OF_TIME, None
    argv = [w.replace("{path}", path) for w in entry["run"]]
    try:
        r = subprocess.run(argv, cwd=str(cfg.root), env={**os.environ, "LOOP_PROJECT": str(cfg.root)}, stdin=subprocess.DEVNULL,
                           capture_output=True, encoding="utf-8", errors="replace", timeout=limit)
    except subprocess.TimeoutExpired:
        if cut:
            return "not_evaluated", {}, {}, OUT_OF_TIME_CHECK, None
        return "not_evaluated", {}, {}, f"no result within {hook.STEP_TIMEOUT_S} s", None
    except OSError as e:
        return "not_evaluated", {}, {}, f"could not start: {e}", None
    text = "\n".join(s.rstrip() for s in (r.stdout, r.stderr) if s and s.strip())
    tail = "\n".join(text.splitlines()[-TAIL_LINES:])[-TAIL_CHARS:]
    obj = _json_line(r.stdout)
    vector = {}
    if isinstance(obj.get("vector"), dict):
        vector = {k: v for k, v in obj["vector"].items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    layers = {str(k): str(v) for k, v in obj["layers"].items()} if isinstance(obj.get("layers"), dict) else {}
    gate = GATE_OF_EXIT.get(r.returncode, "fail")
    return gate, vector, layers, tail, (pass_note(entry["run"], layers, r.stdout) if gate == "pass" else None)


def _now(cfg, entry, path):
    """The candidate as it is now: (the watched file's hash, or None when it is gone; its inputs as [path, hash] pairs; its candidate
    hash; the bytes, or None when they are not kept because the file is over SNAP_MAX)."""
    full, data = cfg.root / path, None
    if full.is_file():
        data = full.read_bytes() if full.stat().st_size <= SNAP_MAX else None
        sha = hashlib.sha256(data).hexdigest() if data is not None else sha256_file(full)
    else:
        sha = None
    inputs = inputs_of(cfg, entry)
    return sha, inputs, cand_sha(sha, inputs), data


def _due(prev, cand, chash, trigger, force=False):
    """Whether a candidate is judged now: it has no record, or its newest record is for other bytes, other inputs or another command,
    or the trigger is a stop and that record is not evaluated. `force` judges it in any case."""
    if prev is None or force:
        return True
    return not (cand_of(prev) == cand and prev["config"] == chash and not (trigger == "stop" and prev["gate"] == "not_evaluated"))


def evaluate(cfg, entry, path, trigger, force=False, deadline=None):
    """Judges one file unless its newest record is for the same candidate and command: then None, and nothing new is said. At a stop,
    a newest record that is not evaluated is judged again. A file that the hook's budget has no time left for (deadline, a
    time.monotonic() value; None: no budget) gets a not_evaluated record that says so. Returns the new record."""
    ledger = read_ledger(cfg)
    same = [r for r in ledger if r["check"] == entry["name"] and r["path"] == path]
    prev = same[-1] if same else None
    sha, inputs, cand, data = _now(cfg, entry, path)
    chash = command_hash(entry["run"])
    if not _due(prev, cand, chash, trigger, force):
        return None
    full = cfg.root / path
    if sha is None:
        gate, vector, layers, tail, note = "not_evaluated", {}, {}, "", None
    else:
        gate, vector, layers, tail, note = _judge(cfg, entry, path, deadline)
        if (sha256_file(full) if full.is_file() else None) != sha:   # the bytes changed under the check: not this verdict
            gate, vector, layers, tail, note = "not_evaluated", {}, {}, "the file changed while its check ran; it is judged again", None
        elif inputs_of(cfg, entry) != inputs:   # an input changed under the check: not this verdict
            gate, vector, layers, tail, note = ("not_evaluated", {}, {},
                                                "an input changed while its check ran; it is judged again", None)
    rec = {"at": now(), "id": None, "check": entry["name"], "path": path, "sha": sha, "config": chash, "gate": gate,
           "vector": vector, "layers": layers, "tail": tail, "trigger": trigger,
           "supersedes": prev["id"] if prev else None, "dominated_by": None,
           "snapshot": _snapshot(cfg, path, data) if sha is not None else None}
    if "inputs" in entry:                    # an entry with inputs: its candidate names them, so a changed input is no old record
        rec["inputs"], rec["cand"] = inputs, cand
    if gate == "pass":
        rec["note"] = note
        dom = dominator(rec, ledger)
        rec["dominated_by"] = dom["id"] if dom else None
    rec["id"] = hashlib.sha256(f"{path}|{sha}|{chash}|{rec['at']}|{len(ledger)}|{trigger}".encode("utf-8")).hexdigest()[:8]
    append(cfg, rec)
    return rec


def _compare(prev, rec):
    line = f"  previous @{(prev['sha'] or 'absent')[:8]}: {_gate_word(prev)} (record {prev['id']})"
    if prev["vector"] and rec["vector"]:
        keys = sorted(set(prev["vector"]) & set(rec["vector"]))
        moved = [f"{k} {fmt(prev['vector'][k])}->{fmt(rec['vector'][k])}" for k in keys if prev["vector"][k] != rec["vector"][k]]
        how = ("improved" if dominates(rec["vector"], prev["vector"]) else
               "worse" if dominates(prev["vector"], rec["vector"]) else "mixed" if moved else "unchanged")
        line += f"; this is {how}" + (f" ({', '.join(moved)})" if moved else "")
    return line


def _inputs_now(cfg, check):
    """The inputs of the named check's entry as they are on disk now, in the form a record keeps them ([] for an entry without inputs)."""
    entry = next((e for e in cfg["watch"] if e["name"] == check), None)
    return inputs_of(cfg, entry) if entry else []


def block(cfg, rec, refusals=True):
    """What the session is told about one record, as plain lines: the check and the file, the gate in capitals (a PASS with what it did
    not run), the layers that ran and those that did not, the inputs judged with it, the vector, the output of a fail or a not
    evaluated, the record that dominates a dominated pass (and its copy, if that exists), the previous verdict of this file under this
    command, and the stop refusals used against the cap (not in a block made for a stop: _decide counts that refusal after the block
    exists, and says "refusal n of cap" itself)."""
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
    if "inputs" in rec:
        out.append("  inputs judged with it: " + (", ".join(p for p, _h in rec["inputs"]) or "none (no file matches its inputs)"))
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
        if dom.get("inputs", []) != _inputs_now(cfg, rec["check"]):   # a copy of the file restores the candidate only with its inputs
            out.append("  Its inputs differ from the ones on disk now, so copying its file back would not restore that candidate; "
                       "no one-line restore is offered.")
        elif held(cfg, dom):
            out.append(f"  Its copy: {dom['snapshot']}. Restore it: cp {dom['snapshot']} {rec['path']}")
    return "\n".join(out)


def _lock(cfg, wait_s):
    """watch.lock for a with-block: held when it comes free within wait_s seconds; else the block gets False (hook._lock_within)."""
    from loop import hook   # hook imports this module
    return hook._lock_within(cfg, "watch.lock", wait_s)


def post(cfg, deadline=None):
    """The blocks the post hook says: every watched file judged now (trigger post) within the hook's budget; a block only where a new
    record was made. When another run holds watch.lock, this call says so and judges nothing: it does not wait for the lock."""
    out = []
    with _lock(cfg, 0) as got:
        if not got:
            _say("loop hook post: another run is judging the watched files (watch.lock is held); this tool call judges none of them")
            return out
        for entry in cfg["watch"]:
            for path in candidates(cfg, entry):
                rec = evaluate(cfg, entry, path, "post", deadline=deadline)
                if rec:
                    out.append(block(cfg, rec))
    return out


def _needs_judgement(cfg, entry, path, trigger):
    """Whether evaluate would judge this file now, which needs the lock (the same test as evaluate, and no record is written)."""
    same = [r for r in read_ledger(cfg) if r["check"] == entry["name"] and r["path"] == path]
    _sha, _inputs, cand, _data = _now(cfg, entry, path)
    return _due(same[-1] if same else None, cand, command_hash(entry["run"]), trigger)


def stop(cfg, deadline=None):
    """What a stop is told: the watched files judged now (trigger stop) within the hook's budget, each newest record with its dominance
    as of now, sorted into failed (a dominated pass counts), did_not_run and passed, with the block of each as it was said. The stop
    waits for watch.lock inside its budget. Without the lock it refuses a file that needs a judgement (did_not_run, lock held) and
    takes the newest record of the others as they are."""
    res = {"failed": [], "did_not_run": [], "passed": [], "said": []}
    wait = LOCK_WAIT_S if deadline is None else max(0.0, deadline - time.monotonic())
    with _lock(cfg, wait) as got:
        for entry in cfg["watch"]:
            for path in candidates(cfg, entry):
                name = f"watch {entry['name']} {path}"
                if got:
                    evaluate(cfg, entry, path, "stop", deadline=deadline)
                elif _needs_judgement(cfg, entry, path, "stop"):
                    res["did_not_run"].append(name)
                    res["said"].append((name, "not evaluated (lock held): another run holds watch.lock, and the stop waited for it "
                                              "within its budget"))
                    continue
                rec = current(cfg, newest(cfg, entry, path))
                if rec["gate"] == "pass" and not rec["dominated_by"]:
                    res["passed"].append(f"{name} ({_note_of(rec)})")
                elif rec["gate"] == "not_evaluated":
                    res["did_not_run"].append(name)
                else:
                    res["failed"].append(name)
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
    for name, pat in unmatched_inputs(cfg):
        print(f"watch {name}: input glob matches nothing: {pat}")
    if not picked:
        print("watch eval: no watched file to judge")
        return 0
    recs = []
    with _lock(cfg, LOCK_WAIT_S) as got:
        if not got:
            _say("watch eval: not evaluated (lock held): another run is judging; nothing was judged")
            return 3
        for entry, path in picked:
            recs.append(current(cfg, evaluate(cfg, entry, path, "manual", force=True)))
    print("\n\n".join(block(cfg, rec) for rec in recs))
    return _exit(recs)


def _status(cfg):
    for name, pat in unmatched_inputs(cfg):
        print(f"watch {name}: input glob matches nothing: {pat}")
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
