"""The tick: one due check runs per call, its result is logged, and a check that stopped running is named.

The scheduler is a multi-level feedback queue of doubly linked lists, one list per level. A check that is MISSED moves to the
front of level 0, due now. A check KEPT twice in a row drops one level, so its interval doubles. A check overdue by more than
OVERDUE_TIMES of its own base interval runs first, the most overdue first, so that a busy check cannot starve the others.
A move is O(1) pointer work; choosing the next check scans the lists, which is cheap for the few checks a project has.
ClauseList is a doubly linked list of text pieces that re-cuts in O(1) pointer work; the scheduler's tests keep it.

INVARIANT: each tick runs at most one check, the one the policy picks; a check that failed is picked again at the next tick;
liveness names every check that never ran or whose last run is older than OVERDUE_TIMES times its every_s.
FAILS WHEN: a check overdue beyond its limit is passed over for one that is not; a failed check is not run at the next tick;
a missing, unreadable or malformed input reports ok; or liveness reports ok while a check is starved.

usage: python3 -I bin/loop tick run        one tick: run the due check, append one line to the tick log, print one JSON line
       python3 -I bin/loop tick liveness   print {"ok": bool, "starved": [...]}; exit 1 when a check is starved
"""
import argparse
import calendar
import json
import math
import os
import subprocess
import sys
import time
try:
    import fcntl
except ImportError:   # no file locks on this platform: ticks are then not kept apart
    fcntl = None

from loop import cli, config

KIT_LOOP = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "bin", "loop")   # the kit's own entry: a project names the kit, it does not carry a copy
LEVELS = 2              # levels of the queue: two keep the slowest interval at twice every_s, inside liveness's three times
KEEP = 2                # runs kept in a row that drop a check one level, so that its interval doubles
OVERDUE_TIMES = 3       # overdue by more than this many base intervals: the check runs first, the most overdue first
CHECK_TIMEOUT_S = 600   # a check that runs longer is stopped and counts as failed
STATE_FILE = "tick-state.json"
LOG_FILE = "tick-log.jsonl"
KIT_VERBS = set(cli.VERBS) | {"doctor"}     # a check whose argv[0] is one of these runs through the kit's own entry


class Node:
    __slots__ = ('val', 'prev', 'next', 'lst')
    def __init__(self, val): self.val = val; self.prev = self.next = None; self.lst = None

class DList:
    def __init__(self): self.h = Node(None); self.t = Node(None); self.h.next = self.t; self.t.prev = self.h; self.n = 0
    def _ins(self, a, node): b = a.next; a.next = node; node.prev = a; node.next = b; b.prev = node; node.lst = self; self.n += 1; return node
    def push_front(self, v): return self._ins(self.h, Node(v))
    def push_back(self, v): return self._ins(self.t.prev, Node(v))
    def insert_after(self, a, v): return self._ins(a, Node(v))
    def remove(self, node): node.prev.next = node.next; node.next.prev = node.prev; node.prev = node.next = None; node.lst = None; self.n -= 1; return node.val
    def move_to_front(self, node): v = self.remove(node); return self.push_front(v)
    def front(self): return self.h.next if self.n else None
    def __iter__(self):
        x = self.h.next
        while x is not self.t: yield x.val; x = x.next
    def nodes(self):
        x = self.h.next
        while x is not self.t: yield x; x = x.next
    def check(self):                                                              # invariant: both directions agree and the count is right
        f = [x for x in self.nodes()]; b = []; x = self.t.prev
        while x is not self.h: b.append(x); x = x.prev
        return f == b[::-1] and len(f) == self.n

class MLFQ:
    """Levels of entries, each a list in order. Each entry has its own base interval (add(..., base=)); level lv waits base * 2**lv."""
    def __init__(self, base=4, levels=5, keep=2, boost=None):
        self.base, self.keep = base, keep; self.L = [DList() for _ in range(levels)]; self.at = {}
        self.boost = boost      # None: an entry overdue by more than OVERDUE_TIMES of its own base runs first; a number: that many units
    def interval(self, lv, base=None): return (self.base if base is None else base) * 2 ** lv
    def _put(self, id, lv, now, due=None, streak=0, base=None):
        base = self.base if base is None else base
        due = now + self.interval(lv, base) if due is None else due
        self.at[id] = dict(lv=lv, streak=streak, due=due, base=base, node=self.L[lv].push_back(id))
    def add(self, id, now, base=None):
        base = self.base if base is None else base
        self.at[id] = dict(lv=0, streak=0, due=now, base=base, node=self.L[0].push_front(id))
    def next_due(self, now):
        # anti-starvation first: a level that always has something due would starve every lower one, so any entry overdue by
        # more than its limit runs first, the most overdue first
        worst = None
        for l in self.L:
            for n in l.nodes():
                e = self.at[n.val]; late = now - e['due']
                limit = OVERDUE_TIMES * e['base'] if self.boost is None else self.boost
                if late > limit and (worst is None or late > worst[0]): worst = (late, n.val)
        if worst is not None: return worst[1]
        for l in self.L:                      # hottest level first; within it, the first entry in list order that is due
            for n in l.nodes():
                if self.at[n.val]['due'] <= now: return n.val
        return None
    def kept(self, id, now):
        a = self.at.pop(id); self.L[a['lv']].remove(a['node']); s = a['streak'] + 1; lv = a['lv']
        if s >= self.keep and lv < len(self.L) - 1: lv += 1; s = 0
        self._put(id, lv, now, streak=s, base=a['base'])
    def missed(self, id, now):
        a = self.at.pop(id); self.L[a['lv']].remove(a['node'])
        self.at[id] = dict(lv=0, streak=0, due=now, base=a['base'], node=self.L[0].push_front(id))

class ClauseList(DList):
    def split(self, node, k):
        s = node.val; node.val = s[:k]; return self.insert_after(node, s[k:])
    def merge(self, node):
        nx = node.next
        if nx is self.t: return node
        node.val = node.val + nx.val; self.remove(nx); return node


def _now():
    """The clock: LOOP_NOW (seconds since the epoch) when set, else the system clock. Tests set LOOP_NOW and never sleep."""
    given = os.environ.get("LOOP_NOW", "").strip()
    if not given:
        return time.time()
    v = float(given)
    if not 0 <= v < 1e11:
        raise ValueError(f"{given!r} is not a time in seconds since the epoch")
    return v


def _at(now):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(now))


def _fail(cmd, detail, names=()):
    """A failure line in the shape of the command, and exit code 1: a missing input never reads as a pass."""
    out = {"ran": None, "ok": False, "detail": detail} if cmd == "run" else {"ok": False, "starved": list(names), "detail": detail}
    print(json.dumps(out))
    return 1


def _checks(cfg):
    """The configured checks, validated. A malformed one raises ValueError with the reason."""
    raw = cfg["checks"]
    if not isinstance(raw, list):
        raise ValueError("must be a list")
    out, names = [], set()
    for i, c in enumerate(raw):
        name = c.get("name") if isinstance(c, dict) else None
        if not isinstance(name, str) or not name:
            raise ValueError(f"check {i} has no name")
        if name in names:
            raise ValueError(f"check {name!r} is given twice")
        run, every = c.get("run"), c.get("every_s")
        if not isinstance(run, list) or not run or not all(isinstance(a, str) for a in run):
            raise ValueError(f"check {name!r}: run must be a non-empty list of strings")
        if run[0] == "tick":
            raise ValueError(f"check {name!r}: a check may not run tick itself")
        if isinstance(every, bool) or not isinstance(every, (int, float)) or not 0 < every < math.inf:
            raise ValueError(f"check {name!r}: every_s must be a positive number")
        names.add(name)
        out.append({"name": name, "run": list(run), "every_s": every})
    return out


def _run_check(cfg, argv):
    """Run one check in the project root; returns (ok, detail). A check that cannot start, or times out, is a failed check."""
    cmd = [sys.executable, "-I", KIT_LOOP, *argv] if argv[0] in KIT_VERBS else list(argv)
    try:
        r = subprocess.run(cmd, cwd=str(cfg.root), capture_output=True, encoding="utf-8", errors="replace", timeout=CHECK_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as e:
        return False, f"error: {type(e).__name__}: {e}"
    lines = r.stdout.strip().splitlines() or r.stderr.strip().splitlines()
    tail = lines[-1][:300] if lines else ""
    return r.returncode == 0, f"exit {r.returncode}" + (f": {tail}" if tail else "")


def _load(path, checks, now):
    """The scheduler, restored from the state file. A check the file does not hold starts due now; the first configured check runs first."""
    m = MLFQ(base=1, levels=LEVELS, keep=KEEP)
    every = {c["name"]: c["every_s"] for c in checks}
    if path.is_file():
        for lv, items in enumerate(json.loads(path.read_text(encoding="utf-8"))["levels"]):
            for name, due, streak in items:
                if name in every and name not in m.at:
                    m._put(name, min(lv, LEVELS - 1), now, due=due, streak=streak, base=every[name])
    for c in reversed(checks):
        if c["name"] not in m.at:
            m.add(c["name"], now, base=c["every_s"])
    return m


def _save(path, m):
    levels = [[[n.val, m.at[n.val]["due"], m.at[n.val]["streak"]] for n in l.nodes()] for l in m.L]
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps({"levels": levels}, indent=1), encoding="utf-8")
    os.replace(tmp, path)               # the state is replaced whole: a crash leaves the old state or the new one


def _earliest(m):
    best = None
    for l in m.L:
        for n in l.nodes():
            due = m.at[n.val]["due"]
            if best is None or due < best[1]:
                best = (n.val, due)
    return best


def _run(cfg, checks, now):
    """One tick, under a lock from the read of the state to its write: two ticks at once would both pick the same check and
    one would lose the other's state. A tick that finds another one running does nothing and says so. The exit code is the
    result of the check that ran: 1 when it failed, so that a tick used as a step or a blocker of a stop is read as its check."""
    with open(cfg.state("tick.lock"), "w") as held:
        if fcntl is not None:
            try:
                fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                print(json.dumps({"ran": None, "ok": True, "detail": "another tick is running; nothing was run", "at": _at(now)}))
                return 0
        return _tick(cfg, checks, now)


def _tick(cfg, checks, now):
    by_name = {c["name"]: c for c in checks}
    try:
        state, log = cfg.state(STATE_FILE), cfg.state(LOG_FILE)
        m = _load(state, checks, now)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as e:
        return _fail("run", f"tick state unreadable: {type(e).__name__}: {e}")
    t0 = time.monotonic()
    name = m.next_due(now)
    if name is None:
        ok, detail, secs = True, "no check due", 0.0
    else:
        ok, detail = _run_check(cfg, by_name[name]["run"])
        (m.kept if ok else m.missed)(name, now)
        secs = round(time.monotonic() - t0, 1)
    nxt, due = _earliest(m)
    out = {"ran": name, "ok": ok, "detail": detail, "secs": secs, "next": nxt, "wait_s": max(0, due - now), "at": _at(now)}
    try:
        _save(state, m)
        with open(log, "a", encoding="utf-8") as f:
            f.write(json.dumps(out) + "\n")
    except OSError as e:
        return _fail("run", f"tick state or log not written: {e}")
    print(json.dumps(out))
    return 0 if ok else 1


def _liveness(cfg, checks, now):
    names = [c["name"] for c in checks]
    log = cfg.path("state_dir") / LOG_FILE          # the file cfg.state(LOG_FILE) names, read without creating a directory
    try:
        text = log.read_text(encoding="utf-8") if log.is_file() else ""
    except (OSError, ValueError) as e:
        return _fail("liveness", f"{LOG_FILE} unreadable: {e}", names)
    last = {}
    for line in text.splitlines():
        try:
            rec = json.loads(line)
            ts = calendar.timegm(time.strptime(rec["at"], "%Y-%m-%d %H:%M:%S"))
        except (ValueError, KeyError, TypeError):
            continue                                # a line that is not a run record cannot show a run
        if rec.get("ran") in names:
            last[rec["ran"]] = max(last.get(rec["ran"], ts), ts)
    starved = [c["name"] for c in checks
               if c["name"] not in last or now - last[c["name"]] > OVERDUE_TIMES * c["every_s"]]
    print(json.dumps({"ok": not starved, "starved": starved}))
    return 1 if starved else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(prog="python3 -I bin/loop tick",
                                     description="run the one due check per tick; name a check that stopped running")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run", help="one tick: run the due check, log it, print one JSON line")
    sub.add_parser("liveness", help="print {ok, starved}; exit 1 when a check never ran or its last run is too old")
    try:
        cmd = parser.parse_args(argv).cmd
    except SystemExit as e:                         # argparse has printed the usage; its code is returned, not raised
        return e.code if isinstance(e.code, int) else 2
    try:
        now = _now()
    except ValueError as e:
        return _fail(cmd, f"LOOP_NOW: {e}")
    try:
        cfg = config.load()
    except SystemExit as e:                         # config refuses an unknown key, with the reason in its message
        return _fail(cmd, str(e.code))
    except (OSError, ValueError) as e:
        return _fail(cmd, f"loop.json: {e}")
    try:
        checks = _checks(cfg)
    except ValueError as e:
        return _fail(cmd, f"loop.json checks: {e}")
    if not checks:
        return _fail(cmd, "no checks in loop.json")
    return _run(cfg, checks, now) if cmd == "run" else _liveness(cfg, checks, now)
