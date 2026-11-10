"""The revisit registry: the questions, doubts and concerns a project registers, which of them are due for a look, and what a
look recorded. Standard library only; ASCII output; the folder, the project tree and the words files come from loop.json.

An item sits in one lane. Active (state open or provisional) is due on the wait ladder 2, 6, 24, 72, 168 hours; slow (state
answered or superseded) on 168, 336, 720 hours; parked (waiting for a gate) only when poked. A look that finds an item unchanged
waits longer. A look that finds it changed brings it back to the first rung, and makes each parent that is an item due now.
Nothing is deleted: an item that is no longer needed is superseded with cited evidence, or parked with its gate named in the note.

INVARIANT: an item is never removed; a write appends its event line under a lock before the registry is replaced, and the
registry it replaces is kept as registry.json.bak; a write whose registry replacement fails leaves a not-applied line after its
event line, unless the system cuts that append short as well; a corrupt or invalid registry, or a corrupt events line, is refused with nothing written; a superseded item names
evidence; a parked item is never due.
FAILS WHEN: an item vanishes after a write; a write changes the registry with no event line before it; a failed registry
replacement leaves an event line with no not-applied line after it; a corrupt file is written over; a superseded item is
accepted with no evidence; a parked item comes up in the due batch; a changed item does not make its parent that is an item
due.
Not covered: an append to events.jsonl that the system cuts short (a full disk, a size limit) leaves a torn last line. history
and every write then exit 1 and name the line, census and due still answer, and no verb repairs the file: the torn line is
removed by hand.

usage (the folder is loop.json's "revisit", default loop-state/revisit; a parent that is not an item is looked up in the tree at
"tree"; `packet` reads the files of "words" when it is given no --files):
  python3 -I bin/loop revisit census
  python3 -I bin/loop revisit due [--n N] [--json]
  python3 -I bin/loop revisit tick
  python3 -I bin/loop revisit validate
  python3 -I bin/loop revisit register --json FILE|- [--update] [--by WHO]
  python3 -I bin/loop revisit done REF --result changed|unchanged --state STATE --note TEXT [--evidence REF ...] [--superseded-by REF ...] [--by WHO]
  python3 -I bin/loop revisit poke REF [--reason TEXT] [--by WHO]
  python3 -I bin/loop revisit history REF
  python3 -I bin/loop revisit packet REF [--files GLOB ...]
Every verb takes --now YYYY-MM-DDTHH:MM:SSZ (the clock; default: the UTC now). Exit codes: 0 ok; 1 usage, validation, or a
missing or corrupt file; 2 refused by a rule (an unknown ref, an empty note, a duplicate without --update, a superseded item
without evidence, a state change with unchanged).

One batch, in this order. (1) `due --n 6`: when nothing is due, that is the whole batch. (2) For each item, write the beliefs
first (`history REF` shows its earlier notes), then `packet REF` (its record, its tree node, and the lines that name it: what
exists now), then judge unchanged or changed, and the state. (3) `done` with one note that holds three statuses on one line:
cognitive (what is believed, assumed and doubted, and what would change it); tools (none, designed, built, tested, running,
demoted); record (where it is written, and whether the chain from its root to its answer holds). (4) A changed item's parents
come due at once, by the tool; a change to the tree is a proposal for the tree's own gates. (5) End with one line: the items
looked at, what changed, and the next due time.

Never: delete an item; drop one silently; supersede without cited evidence; write to a protected branch or to a file this tool
does not own; address the principal except through the record; take a question of means to the principal before an advisor has
answered it.
"""
import argparse
import copy
import fcntl
import glob
import json
import os
import pathlib
import re
import sys
import tempfile
from datetime import datetime, timedelta, timezone

from loop import config

LADDER = {"active": [2, 6, 24, 72, 168], "slow": [168, 336, 720], "parked": []}  # hours between two looks, by rung
STATE_LANE = {"open": "active", "provisional": "active", "answered": "slow", "superseded": "slow", "parked": "parked"}
STATES = tuple(STATE_LANE)
LANES = ("active", "slow", "parked")
KINDS = ("question", "doubt", "concern")
RESULTS = ("changed", "unchanged")
TOOL_STATES = ("none", "designed", "built", "tested", "running", "demoted")
PRIORITY_HOURS = {1: 0, 2: 6, 3: 168}  # the first wait of a new item, by its priority
UPDATABLE = ("text", "source", "asked", "root", "node", "parents", "kind", "priority")
ITEM_KEYS = ("ref", "text", "kind", "source", "asked", "root", "node", "parents", "priority", "state", "lane",
             "superseded_by", "cognitive", "tools", "record", "evidence", "revisit")
REVISIT_KEYS = ("last", "next", "step", "count", "by", "reason")
ISO_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
ISO_FMT = "%Y-%m-%dT%H:%M:%SZ"
REGISTRY, EVENTS = "registry.json", "events.jsonl"
DEFAULT_BY = "assistant"
PACKET_LINES = 200  # the most matching lines `packet` prints; the count of all of them is always printed


class Fail(Exception):
    """Stops a verb: code 1 for usage, validation, or a missing or corrupt file; code 2 for a refusal by a rule."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class Parser(argparse.ArgumentParser):
    """Usage errors exit 1: argparse's own code 2 would read as a refusal by a rule."""

    def error(self, message):
        raise Fail(1, "usage: " + message)


def ascii_text(text):
    return str(text).encode("ascii", "backslashreplace").decode("ascii")


def emit(line):
    sys.stdout.write(ascii_text(line) + "\n")


def complain(line):
    sys.stderr.write(ascii_text(line) + "\n")


def one_line(text, width):
    return str(text).replace("\r", " ").replace("\n", " ")[:width]


def none_or(value):
    return "none" if value is None else value


def parse_iso(value):
    """A timestamp YYYY-MM-DDTHH:MM:SSZ as an aware UTC datetime; ValueError otherwise."""
    if not isinstance(value, str) or not ISO_RE.fullmatch(value):
        raise ValueError("not an ISO timestamp")
    return datetime.strptime(value, ISO_FMT).replace(tzinfo=timezone.utc)


def fmt_iso(moment):
    return moment.strftime(ISO_FMT)


def iso_required(value):
    try:
        parse_iso(value)
    except ValueError:
        return False
    return True


def iso_ok(value):
    return value is None or iso_required(value)


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def str_or_none(value):
    return value is None or isinstance(value, str)


def lane_for(state):
    return STATE_LANE.get(state) if isinstance(state, str) else None


def clock(text):
    """--now overrides the UTC clock; without it the current UTC time is used."""
    if text is None:
        return datetime.now(timezone.utc).replace(microsecond=0)
    try:
        return parse_iso(text)
    except ValueError:
        raise Fail(1, "--now must be YYYY-MM-DDTHH:MM:SSZ")


def check_item(key, item):
    """The consistency rules for one item; returns the messages, empty when the item is valid."""
    if not isinstance(item, dict):
        return ["%s: item must be an object" % key]
    missing = [name for name in ITEM_KEYS if name not in item]
    if missing:
        return ["%s: missing fields %s" % (key, ", ".join(missing))]
    errors = []

    def need(ok, message):
        if not ok:
            errors.append("%s: %s" % (key, message))

    need(item["ref"] == key, "ref must equal the key")
    need(isinstance(item["text"], str) and 1 <= len(item["text"]) <= 600, "text must be 1 to 600 characters")
    need(item["kind"] in KINDS, "kind must be question, doubt or concern")
    src = item["source"]
    need(isinstance(src, dict) and (src.get("line") is None or is_int(src.get("line")))
         and all(str_or_none(src.get(f)) for f in ("path", "addendum", "quote")),
         "source needs an int or null line and string or null path, addendum and quote")
    asked = item["asked"]
    need(isinstance(asked, dict) and str_or_none(asked.get("by")) and iso_ok(asked.get("at")),
         "asked needs a string or null by and an ISO or null at")
    root = item["root"]
    need(isinstance(root, list) and all(
        isinstance(r, dict) and str_or_none(r.get("quote")) and iso_ok(r.get("at")) for r in root),
         "root must be a list of objects with an ISO or null at")
    need(str_or_none(item["node"]), "node must be a string or null")
    parents = item["parents"]
    need(isinstance(parents, list) and all(isinstance(p, str) for p in parents), "parents must be a list of refs")
    need(is_int(item["priority"]) and item["priority"] in (1, 2, 3), "priority must be 1, 2 or 3")
    state, lane = item["state"], item["lane"]
    need(state in STATES, "state must be one of " + ", ".join(STATES))
    need(lane in LANES, "lane must be active, slow or parked")
    expected = lane_for(state)
    if expected is not None:
        need(lane == expected, "lane %s does not match state %s (%s needs lane %s)" % (lane, state, state, expected))
    sup = item["superseded_by"]
    need(isinstance(sup, list) and all(isinstance(s, str) for s in sup), "superseded_by must be a list of refs")
    cognitive = item["cognitive"]
    need(isinstance(cognitive, list) and all(
        isinstance(c, dict) and iso_required(c.get("at")) and isinstance(c.get("by"), str)
        and isinstance(c.get("summary"), str) and isinstance(c.get("result"), str)
        for c in cognitive), "cognitive entries need at (ISO), by, summary and result")
    tools = item["tools"]
    need(isinstance(tools, dict) and tools.get("state") in TOOL_STATES and str_or_none(tools.get("gap")),
         "tools needs a state of none, designed, built, tested, running or demoted, and a gap that is a string or null")
    record = item["record"]
    need(isinstance(record, dict) and isinstance(record.get("where"), list)
         and all(isinstance(w, str) for w in record["where"])
         and (record.get("chain_ok") is None or isinstance(record.get("chain_ok"), bool)),
         "record needs a where list and chain_ok true, false or null")
    evidence = item["evidence"]
    need(isinstance(evidence, list) and all(
        isinstance(e, dict) and isinstance(e.get("ref"), str) and isinstance(e.get("kind"), str)
        and iso_required(e.get("added")) for e in evidence),
         "evidence entries need ref, kind and added (ISO)")
    rv = item["revisit"]
    rv_ok = (isinstance(rv, dict) and all(k in rv for k in REVISIT_KEYS)
             and iso_ok(rv["last"]) and iso_ok(rv["next"])
             and is_int(rv["step"]) and rv["step"] >= 0
             and is_int(rv["count"]) and rv["count"] >= 0
             and str_or_none(rv["by"]) and str_or_none(rv["reason"]))
    need(rv_ok, "revisit needs last, next, step, count, by and reason with the right types")
    if rv_ok:
        if lane in LANES and lane != "parked":
            need(rv["step"] < len(LADDER[lane]), "revisit.step is outside the %s ladder" % lane)
        need(state != "parked" or rv["next"] is None, "a parked item needs revisit.next null")
    need(state != "superseded" or bool(sup) or bool(evidence), "superseded needs superseded_by or evidence")
    return errors


def tree_nodes(cfg):
    """(nodes, status, detail): the nodes of the project's tree, keyed by id. A node is an object with an id, found under the
    roots and their children. status is "ok"; "missing" (no file, so no parent outside the items is confirmed); or "corrupt"
    (the file cannot be read: an error wherever a parent outside the items needs it)."""
    path = cfg.path("tree")
    if not path.is_file():
        return {}, "missing", "no tree at %s" % path
    try:
        tree = json.loads(path.read_text(encoding="utf-8"))
        roots = tree["roots"]
        if not isinstance(roots, list):
            raise ValueError("roots is not a list")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {}, "corrupt", "%s: %s" % (path, exc)
    nodes, stack = {}, list(roots)
    while stack:
        found = stack.pop()
        if not isinstance(found, dict):
            continue
        if isinstance(found.get("id"), str):
            nodes.setdefault(found["id"], found)
        kids = found.get("children")
        if isinstance(kids, list):
            stack.extend(kids)
    return nodes, "ok", ""


def check_registry(data, cfg):
    """The consistency rules over the whole registry: (level, message) pairs, level ERROR or WARN. A parent that is not an item
    is looked up in the project's tree. Without a tree it is only warned, since no decision depends on it (a change is
    propagated to items only); a tree that cannot be read is an error, because a parent outside the items cannot be checked."""
    problems = []
    if data.get("version") != 1:
        problems.append(("ERROR", "version must be 1"))
    if not iso_required(data.get("updated")):
        problems.append(("ERROR", "updated must be an ISO timestamp"))
    items = data["items"]
    for key, item in items.items():
        problems.extend(("ERROR", message) for message in check_item(key, item))
    outside = []
    for key, item in items.items():
        parents = item.get("parents") if isinstance(item, dict) else None
        for parent in (parents if isinstance(parents, list) else []):
            if isinstance(parent, str) and parent not in items:
                outside.append((key, parent))
    if outside:
        nodes, status, detail = tree_nodes(cfg)
        if status == "corrupt":
            problems.append(("ERROR", "tree is not readable (%s); parents outside the items cannot be checked" % detail))
        else:
            for key, parent in outside:
                if parent not in nodes:
                    problems.append(("WARN", "%s: parent %s is not in items" % (key, parent)))
    return problems


def gate(data, cfg):
    """The rules must hold before a read that depends on the data, and before every write."""
    errors = [message for level, message in check_registry(data, cfg) if level == "ERROR"]
    if errors:
        raise Fail(1, "registry invalid (%d errors), run validate: %s" % (len(errors), errors[0]))


def registry_paths(cfg):
    """The folder, the registry, the events file and the backup of the registry, under the configured folder."""
    folder = cfg.path("revisit")
    return folder, folder / REGISTRY, folder / EVENTS, folder / (REGISTRY + ".bak")


def load_registry(path):
    """A missing or corrupt registry is exit 1, and nothing is written."""
    if not path.exists():
        raise Fail(1, "registry missing: %s" % path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Fail(1, "corrupt registry: %s" % exc)
    if not isinstance(data, dict) or not isinstance(data.get("items"), dict):
        raise Fail(1, "corrupt registry: expected an object with an items object")
    return data


def read_events(path):
    """Every line of the events file must be a JSON object, or the file is corrupt (exit 1)."""
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, ValueError) as exc:
        raise Fail(1, "corrupt events file: %s" % exc)
    events = []
    for number, line in enumerate(lines, 1):
        try:
            event = json.loads(line)
        except ValueError:
            event = None
        if not isinstance(event, dict):
            raise Fail(1, "corrupt events file: line %d is not a JSON object" % number)
        events.append(event)
    return events


def encode_json(data):
    return (json.dumps(data, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def write_atomic(path, payload):
    """A temporary file in the same folder, fsynced, then renamed over the path: a failure leaves the old file or the new one."""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".revisit-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def empty_registry(now):
    return {"version": 1, "updated": fmt_iso(now), "items": {}}


def due_list(items, now):
    """Not parked, revisit.next set and at or before now: (ref, item, when)."""
    due = []
    for ref, item in items.items():
        nxt = item["revisit"]["next"]
        if item["lane"] == "parked" or nxt is None:
            continue
        when = parse_iso(nxt)
        if when <= now:
            due.append((ref, item, when))
    return due


def next_due(items, now):
    """The earliest next look after now among the items that are not parked, or none."""
    later = []
    for item in items.values():
        nxt = item["revisit"]["next"]
        if item["lane"] != "parked" and nxt is not None and parse_iso(nxt) > now:
            later.append(parse_iso(nxt))
    return fmt_iso(min(later)) if later else "none"


def due_order(entry):
    """Never looked at first, then priority, then the due time, then ref."""
    ref, item, when = entry
    return (item["revisit"]["last"] is not None, item["priority"], when, ref)


def due_sorted(items, now):
    return sorted(due_list(items, now), key=due_order)


def cmd_census(data, now):
    items = data["items"]
    lanes = dict.fromkeys(LANES, 0)
    states = dict.fromkeys(STATES, 0)
    never = 0
    for item in items.values():
        lanes[item["lane"]] += 1
        states[item["state"]] += 1
        if item["revisit"]["last"] is None:
            never += 1
    emit("items: %d" % len(items))
    emit("lane active/slow/parked: %d/%d/%d" % tuple(lanes[name] for name in LANES))
    emit("state open/provisional/answered/superseded/parked: %s" % "/".join(str(states[name]) for name in STATES))
    emit("due now: %d" % len(due_list(items, now)))
    emit("never revisited: %d" % never)
    emit("next due: %s" % next_due(items, now))
    return 0


def cmd_due(data, now, limit, as_json):
    items = data["items"]
    due = due_sorted(items, now)
    shown = due[:limit]
    if as_json:
        emit(json.dumps([item for _, item, _ in shown], indent=2, ensure_ascii=True))
        return 0
    emit("revisit: %d due of %d (showing %d); next due at %s" % (len(due), len(items), len(shown), next_due(items, now)))
    for ref, item, when in shown:
        revisit = item["revisit"]
        emit(" | ".join([ref, item["lane"], item["state"], str(revisit["step"]), "due since " + fmt_iso(when),
                         revisit["reason"] or "time", one_line(item["text"], 110)]))
    return 0


def cmd_tick(data, now):
    items = data["items"]
    due = due_list(items, now)
    later = next_due(items, now)
    if due:
        ref, _, when = min(due, key=lambda entry: (entry[2], entry[0]))
        emit("revisit: %d due (oldest %s since %s); next due %s; items %d" % (len(due), ref, fmt_iso(when), later, len(items)))
    else:
        emit("revisit: 0 due; next due %s; items %d" % (later, len(items)))
    return 0


def cmd_validate(data, cfg):
    problems = check_registry(data, cfg)
    errors = sum(1 for level, _ in problems if level == "ERROR")
    for level, message in problems:
        emit("%s %s" % (level, message))
    emit("valid: %s (%d errors, %d warnings)" % ("yes" if errors == 0 else "no", errors, len(problems) - errors))
    return 1 if errors else 0


def dump_compact(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def cmd_history(data, events, ref):
    if ref not in data["items"]:
        raise Fail(2, "unknown ref %s" % ref)
    for event in read_events(events):
        payload = event.get("data")
        refs = payload.get("refs") if isinstance(payload, dict) else None
        if event.get("ref") == ref or (isinstance(refs, list) and ref in refs):
            emit("%s %s %s %s" % (event.get("ts"), event.get("op"), event.get("by"), dump_compact(payload)[:80]))
    return 0


def name_pattern(ref):
    """The ref as a whole word: not a part of a longer ref, a number or a path."""
    return re.compile(r"(?<![A-Za-z0-9.\-])" + re.escape(ref) + r"(?![A-Za-z0-9])")


def snippet(line, rx, width=95):
    match = rx.search(line)
    if match is None:
        return one_line(line, 2 * width)
    start, end = max(0, match.start() - width), min(len(line), match.end() + width)
    return ("..." if start else "") + one_line(line[start:end], 4 * width) + ("..." if end < len(line) else "")


def relative(path, root):
    try:
        return str(pathlib.Path(path).relative_to(root))
    except ValueError:
        return str(path)


def words_globs(cfg):
    words = cfg["words"]
    return [words] if isinstance(words, str) else [str(word) for word in words]


def cmd_packet(cfg, data, ref, files):
    """The record of one item, its node in the tree, and the lines of the given files that name it. It prints what it reads
    and judges nothing."""
    items = data["items"]
    if ref not in items:
        raise Fail(2, "unknown ref %s" % ref)
    item = items[ref]
    src, rv = item["source"], item["revisit"]
    emit("%s | %s | %s/%s | priority %d" % (ref, item["kind"], item["state"], item["lane"], item["priority"]))
    emit("  text: " + one_line(item["text"], 320))
    emit("  source: %s, line %s; quote: %s" % (none_or(src.get("path")), none_or(src.get("line")),
                                              one_line(none_or(src.get("quote")), 160)))
    emit("  revisit: last %s, step %d, count %d, next %s, reason %s"
         % (none_or(rv["last"]), rv["step"], rv["count"], none_or(rv["next"]), none_or(rv["reason"])))
    emit("  parents: " + (", ".join(item["parents"]) or "none"))
    nodes, _, detail = tree_nodes(cfg)
    node = item["node"]
    if node is None:
        emit("  tree: no node")
    elif node in nodes:
        found = nodes[node]
        kids = found.get("children") if isinstance(found.get("children"), list) else []
        ids = [kid["id"] for kid in kids if isinstance(kid, dict) and isinstance(kid.get("id"), str)]
        emit("  tree: %s [%s] %s; children: %s" % (node, found.get("status", "none"),
                                                one_line(found.get("title", ""), 110), ", ".join(ids) or "none"))
    else:
        emit("  tree: %s not found (%s)" % (node, detail or "not in the tree"))
    globs = files or words_globs(cfg)
    if not globs:
        emit("  files: none read (give --files GLOB, or name the words files in loop.json)")
        return 0
    rx = name_pattern(ref)
    hits, seen = [], set()
    for pattern in globs:
        for path in sorted(glob.glob(os.path.join(str(cfg.root), pattern), recursive=True)):
            if path in seen or not os.path.isfile(path):
                continue
            seen.add(path)
            try:
                lines = pathlib.Path(path).read_text(encoding="utf-8", errors="replace").split("\n")
            except OSError:
                continue
            rel = relative(path, cfg.root)
            hits.extend((rel, number, line) for number, line in enumerate(lines, 1) if rx.search(line))
    emit("  files: %d line(s) name %s in %s" % (len(hits), ref, ", ".join(globs)))
    for rel, number, line in hits[:PACKET_LINES]:
        emit("    %s:%d | %s" % (rel, number, snippet(line, rx)))
    if len(hits) > PACKET_LINES:
        emit("    ... %d more line(s) not shown" % (len(hits) - PACKET_LINES))
    return 0


def read_input(source):
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise Fail(1, "cannot read the input JSON: %s" % exc)


def list_field(record, name):
    value = record.get(name, [])
    if not isinstance(value, list):
        raise Fail(2, "%s must be a list" % name)
    return value


def new_item(ref, record, now):
    """The defaults of an item that is not registered yet."""
    item = dict(record)
    item["ref"] = ref
    state = item.setdefault("state", "open")
    item.setdefault("priority", 2)
    item.setdefault("lane", lane_for(state))
    item.setdefault("source", {"path": None, "line": None, "addendum": None, "quote": None})
    item.setdefault("asked", {"by": None, "at": None})
    item.setdefault("root", [])
    item.setdefault("node", None)
    item.setdefault("parents", [])
    item.setdefault("superseded_by", [])
    item.setdefault("cognitive", [])
    item.setdefault("tools", {"state": "none", "gap": None})
    item.setdefault("record", {"where": [], "chain_ok": None})
    item.setdefault("evidence", [])
    if "revisit" not in item:
        hours = PRIORITY_HOURS.get(item["priority"]) if is_int(item["priority"]) else None
        when = None if state == "parked" or hours is None else now + timedelta(hours=hours)
        item["revisit"] = {"last": None, "next": fmt_iso(when) if when else None,
                           "step": 0, "count": 0, "by": None, "reason": None}
    return item


def update_item(old, record):
    """Replaces the updatable fields, appends the cognitive and evidence entries, and keeps the state, the lane and the
    revisit record."""
    item = copy.deepcopy(old)
    for name in UPDATABLE:
        if name in record:
            item[name] = copy.deepcopy(record[name])
    item["cognitive"] = old["cognitive"] + list_field(record, "cognitive")
    item["evidence"] = old["evidence"] + list_field(record, "evidence")
    return item


def mutate_register(data, args, now):
    """All or nothing: returns (registry, event data, output lines, event label)."""
    raw = read_input(args.json)
    records = raw.get("items") if isinstance(raw, dict) else raw
    if not isinstance(records, list):
        raise Fail(1, "the input must be a list or an object with an items list")
    items = data["items"]
    refs, seen = [], set()
    registered = updated = 0
    for record in records:
        ref = record.get("ref") if isinstance(record, dict) else None
        if not isinstance(ref, str) or not ref:
            raise Fail(2, "invalid item: ref must be a non-empty string")
        if ref in seen:
            raise Fail(2, "duplicate ref in the input: %s" % ref)
        seen.add(ref)
        refs.append(ref)
        if ref in items:
            if not args.update:
                raise Fail(2, "duplicate ref %s (use --update)" % ref)
            candidate = update_item(items[ref], record)
            updated += 1
        else:
            candidate = new_item(ref, record, now)
            registered += 1
        problems = check_item(ref, candidate)
        if problems:
            raise Fail(2, "invalid item: " + problems[0])
        items[ref] = candidate
    event = {"refs": refs, "registered": registered, "updated": updated}
    return data, event, ["registered %d, updated %d" % (registered, updated)], ",".join(refs)


def mutate_done(data, ref, args, now, by):
    """One look: the lane follows the state, the wait follows the ladder, and a changed look makes its parents that are items
    due now. Every refusal is raised before anything changes. Returns (registry, event data, output lines, event label)."""
    items = data["items"]
    if ref not in items:
        raise Fail(2, "unknown ref %s" % ref)
    note = args.note or ""
    if not note.strip():
        raise Fail(2, "the note must be non-empty")
    item = items[ref]
    state, result = args.state, args.result
    if state == "superseded" and not args.superseded_by and not args.evidence:
        raise Fail(2, "superseded needs --superseded-by or --evidence")
    if args.superseded_by and state != "superseded":
        raise Fail(2, "--superseded-by needs --state superseded")
    if state != item["state"] and result == "unchanged":
        raise Fail(2, "a state change needs --result changed")
    stamp = fmt_iso(now)
    old_lane = item["lane"]
    item["state"] = state
    lane = item["lane"] = STATE_LANE[state]
    for other in args.superseded_by or []:
        if other not in item["superseded_by"]:
            item["superseded_by"].append(other)
    for other in args.evidence or []:
        item["evidence"].append({"ref": other, "kind": "revisit", "added": stamp})
    item["cognitive"].append({"at": stamp, "by": by, "summary": note, "result": result})
    revisit = item["revisit"]
    if lane == "parked":
        step, when = 0, None
    else:
        if lane != old_lane or result == "changed":
            step = 0
        else:
            step = min(revisit["step"] + 1, len(LADDER[lane]) - 1)
        when = now + timedelta(hours=LADDER[lane][step])
    revisit.update({"last": stamp, "next": fmt_iso(when) if when else None, "step": step,
                    "count": revisit["count"] + 1, "by": by, "reason": None})
    propagated = []
    if result == "changed":
        for parent in dict.fromkeys(item["parents"]):
            target = items.get(parent)
            if target is None or target["lane"] == "parked":
                continue
            current = target["revisit"]["next"]
            target["revisit"]["next"] = fmt_iso(now if current is None else min(parse_iso(current), now))
            target["revisit"]["reason"] = "child %s changed" % ref
            propagated.append(parent)
    when_text = fmt_iso(when) if when else "none"
    lines = ["done %s: state %s lane %s step %d next %s" % (ref, state, lane, step, when_text)]
    if propagated:
        lines.append("propagated: " + ",".join(propagated))
    event = {"result": result, "state": state, "note": note, "step": step, "next": when_text,
             "evidence": args.evidence or [], "superseded_by": args.superseded_by or [], "propagated": propagated}
    return data, event, lines, ref


def mutate_poke(data, ref, args, now):
    """Wakes an item now; a parked item becomes open, active and at the first rung."""
    items = data["items"]
    if ref not in items:
        raise Fail(2, "unknown ref %s" % ref)
    item = items[ref]
    revisit = item["revisit"]
    if item["state"] == "parked":
        item["state"], item["lane"], revisit["step"] = "open", "active", 0
    revisit["next"] = fmt_iso(now)
    revisit["reason"] = args.reason or "poke"
    line = "poked %s: state %s lane %s step %d next %s" % (ref, item["state"], item["lane"], revisit["step"], revisit["next"])
    return data, {"reason": revisit["reason"]}, [line], ref


def record_not_applied(log, stamp, label, by, event, error):
    """Appends the not-applied line for a write whose event line is already in the file: the same ref, the time stamp of that
    line, and the error. Returns what happened, for the message of exit 1; a failure to append is named there, so it reaches
    stderr."""
    payload = {"of": stamp, "error": one_line(error, 200)}
    if isinstance(event.get("refs"), list):
        payload["refs"] = event["refs"]
    line = json.dumps({"ts": stamp, "op": "not-applied", "ref": label, "by": by, "data": payload})
    try:
        log.write(line + "\n")
        log.flush()
        os.fsync(log.fileno())
    except OSError as exc:
        return ("the not-applied line could not be appended either (%s): the events file may end with a line for a write "
                "that did not land" % exc)
    return "a not-applied line for %s was appended" % label


def write_op(cfg, now, op, by, mutate, creating=False):
    """A write, in this order: lock the events file; load the registry and check it; check the change; append one event line;
    keep the registry it replaces as registry.json.bak; replace the registry through a temporary file. Every refusal is raised
    before anything is written; a failure after the event line appends a not-applied line naming it, and exits 1."""
    folder, registry, events, backup = registry_paths(cfg)
    folder.mkdir(parents=True, exist_ok=True)
    with open(events, "a+", encoding="utf-8") as log:
        fcntl.flock(log.fileno(), fcntl.LOCK_EX)
        if registry.exists():
            data = load_registry(registry)
        elif creating:
            data = empty_registry(now)
        else:
            raise Fail(1, "registry missing: %s" % registry)
        read_events(events)
        gate(data, cfg)
        after, event, lines, label = mutate(copy.deepcopy(data))
        gate(after, cfg)
        line = json.dumps({"ts": fmt_iso(now), "op": op, "ref": label, "by": by, "data": event})
        log.seek(0, os.SEEK_END)
        log.write(line + "\n")
        try:
            log.flush()
            os.fsync(log.fileno())
            after["updated"] = fmt_iso(now)
            previous = registry.read_bytes() if registry.exists() else encode_json(empty_registry(now))
            write_atomic(backup, previous)
            write_atomic(registry, encode_json(after))
        except OSError as exc:
            status = record_not_applied(log, fmt_iso(now), label, by, event, exc)
            raise Fail(1, "registry not replaced (%s); %s" % (exc, status))
    for text in lines:
        emit(text)
    return 0


def due(cfg, now=None):
    """The due items of the project's registry as (ref, item, when), in the order of a look. Reads only. A missing, corrupt or
    invalid registry raises Fail (its code is 1), so a caller catches Fail and reads the code and the message."""
    moment = now or datetime.now(timezone.utc).replace(microsecond=0)
    _, registry, _, _ = registry_paths(cfg)
    data = load_registry(registry)
    gate(data, cfg)
    return due_sorted(data["items"], moment)


def build_parser():
    common = Parser(add_help=False, allow_abbrev=False)
    common.add_argument("--now", help="the clock, YYYY-MM-DDTHH:MM:SSZ (default: the UTC now)")
    parser = Parser(prog="python3 -I bin/loop revisit", allow_abbrev=False,
                    description="the registry of questions, doubts and concerns: what is due for a look, and what a look recorded")
    verbs = parser.add_subparsers(dest="cmd", metavar="VERB", required=True)
    verbs.add_parser("census", parents=[common], help="counts by lane and state")
    due_p = verbs.add_parser("due", parents=[common], help="the due batch")
    due_p.add_argument("--n", type=int, default=6, help="at most N items (default 6)")
    due_p.add_argument("--json", action="store_true", help="an array of the full items")
    verbs.add_parser("tick", parents=[common], help="one line: the check that `tick run` runs")
    verbs.add_parser("validate", parents=[common], help="the consistency checks")
    reg = verbs.add_parser("register", parents=[common], help="add items from a JSON file, or update them")
    reg.add_argument("--json", required=True, metavar="FILE", help="a list of items or an object with an items list; - is stdin")
    reg.add_argument("--update", action="store_true", help="update the items already registered")
    reg.add_argument("--by", help="who acts (default assistant)")
    done = verbs.add_parser("done", parents=[common], help="record a look at one item")
    done.add_argument("ref", metavar="REF")
    done.add_argument("--result", required=True, choices=RESULTS)
    done.add_argument("--state", required=True, choices=STATES)
    done.add_argument("--note", help="the note, with the three statuses on one line (required, non-empty)")
    done.add_argument("--evidence", nargs="+", action="extend", metavar="REF")
    done.add_argument("--superseded-by", nargs="+", action="extend", dest="superseded_by", metavar="REF")
    done.add_argument("--by", help="who acts (default assistant)")
    poke = verbs.add_parser("poke", parents=[common], help="wake one item now")
    poke.add_argument("ref", metavar="REF")
    poke.add_argument("--reason", help="the reason (default: poke)")
    poke.add_argument("--by", help="who acts (default assistant)")
    hist = verbs.add_parser("history", parents=[common], help="the events for one item")
    hist.add_argument("ref", metavar="REF")
    pack = verbs.add_parser("packet", parents=[common], help="what exists for one item; reads only")
    pack.add_argument("ref", metavar="REF")
    pack.add_argument("--files", nargs="+", metavar="GLOB",
                      help="files whose lines are searched (default: the words files of loop.json)")
    return parser


def run(argv):
    args = build_parser().parse_args(argv)
    try:
        cfg = config.load()
    except SystemExit as exc:  # loop.json has a key that is not known: the reason is in the message
        raise Fail(1, str(exc.code))
    refusal = config.no_project(cfg, "revisit")
    if refusal:
        raise Fail(1, refusal)
    if args.cmd == "due" and args.n < 0:
        raise Fail(1, "usage: --n must be 0 or more")
    now = clock(args.now)
    by = getattr(args, "by", None) or DEFAULT_BY
    if args.cmd == "register":
        return write_op(cfg, now, "register", by, lambda data: mutate_register(data, args, now), creating=True)
    if args.cmd == "done":
        return write_op(cfg, now, "done", by, lambda data: mutate_done(data, args.ref, args, now, by))
    if args.cmd == "poke":
        return write_op(cfg, now, "poke", by, lambda data: mutate_poke(data, args.ref, args, now))
    _, registry, events, _ = registry_paths(cfg)
    data = load_registry(registry)
    if args.cmd == "validate":
        return cmd_validate(data, cfg)
    gate(data, cfg)
    if args.cmd == "census":
        return cmd_census(data, now)
    if args.cmd == "due":
        return cmd_due(data, now, args.n, args.json)
    if args.cmd == "tick":
        return cmd_tick(data, now)
    if args.cmd == "history":
        return cmd_history(data, events, args.ref)
    return cmd_packet(cfg, data, args.ref, args.files)


def main(argv=None):
    try:
        return run(sys.argv[1:] if argv is None else argv)
    except Fail as exc:
        complain(exc.message)
        return exc.code
    except OSError as exc:
        complain("revisit: the registry could not be read or written: %s" % exc)
        return 1
