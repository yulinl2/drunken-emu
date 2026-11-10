"""Bank what the principal says, once, verbatim, with its time; search the bank and the words files for what was said; list
what the principal typed that is still waiting in a transcript's queue.

The principal's messages come from the session transcript: what was typed at a prompt, the answers to a question dialog, and
what was typed while a turn was running (a queued message), which the host delivers at the end of the turn (a user row) or
between two tool calls (a queued_command attachment). Five subcommands:
  bank     appends each new message of the principal to the bank, an append-only file of JSON lines (the "bank" key)
  raw      lists what the principal typed, once, from a transcript file or from the git refs of the backup branches
  find     searches the bank and the words files (the "words" globs) for the given words, case-insensitively
  pending  lists the queued messages still waiting in a transcript: typed while a turn runs, not yet delivered to the model
  quotes   checks each quoted text of a report against the bank and the words files: FOUND, LOOSE, ELSEWHERE or MISSING (loop/quotes.py)

INVARIANT: every message of the principal in the transcript is in the bank once, verbatim, with the time it was typed (a queued one also with the time it was delivered and the way: end of turn or between tool calls), and no other text is; one rule, delivers(), decides what a row delivers, for the bank and for pending alike (its text is one waiting message, or its text blocks are, or its text is cut exactly into waiting messages joined by one newline each); pending lists each queued message that no later row delivers, once, in file order, and no other message.
FAILS WHEN: a typed message is in the transcript and not in the bank, or in it twice; a message queued and delivered between two tool calls is missing from the bank, or banked twice; a queued message is banked with the time of its delivery as its time; a tool result or a notice of the harness is banked, or the queued text a notice delivered; a missing transcript, bank or ref is reported as nothing new; a queued message that no later row delivers is missing from pending, or a delivered one is listed; a row that only contains a waiting message among other text delivers it, a cut that uses one message twice delivers, and a queued slash command is counted as not delivered yet (loop/tests/test_record.py, loop/tests/test_record_ways.py, loop/tests/test_rec_delivery.py)

usage: python3 -I bin/loop record bank [--src FILE]
       python3 -I bin/loop record raw [--all | SOURCE ...] [--grep REGEX] [--full] [--width N]
       python3 -I bin/loop record find [--all] [--max N] WORD [WORD ...]
       python3 -I bin/loop record pending [--src FILE]
       python3 -I bin/loop record quotes FILE [--also FILE ...] [--min 12] [--out F]
"""
import contextlib
import argparse
import collections
import glob
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

from loop import config
try:
    import fcntl
except ImportError:   # no file locks on this platform: the bank is then written without one
    fcntl = None

MAX_CHARS = 20000        # a longer message is banked cut to this many characters, with "truncated": true
SKILL_BODY_CHARS = 3000  # a skill body the harness injected, longer than this, is not the principal's words
LONG_REPEAT = 200        # a scheduled delivery repeating a banked text this long is a cron fire or a wake, not typing
QUOTED = re.compile(r'["\u201c\u300c](.+?)["\u201d\u300d]')   # in a words file, the principal's words are the quoted parts

# Text that starts with one of these is not the principal's: notices of the tool itself, hook output, compaction summaries,
# interrupt markers, the harness's goal check-ins. A prefix that names one project's own jobs is not here: it goes in loop.json
# as "not_principal_prefixes". This is the one list: bank, pending and raw read it.
NOT_PRINCIPAL = (
    "<task-notification>", "Stop hook feedback", "[SYSTEM NOTIFICATION", "UserPromptSubmit hook", "PostToolUse", "PreToolUse",
    "<system-reminder>", "This session is being continued", "Called the Read tool", "Result of calling",
    "Tool loaded.", "<artifact-content-authored-by-others", "<local-command-stdout>", "<local-command-caveat>",
    "# /loop", "The following skills were", "Base directory for this skill", "(Re-invocation of",
    "This session's worker process was restarted", "Your response above was stopped by a safety classi",
    "A session-scoped Stop hook is now active", "Another Claude session sent a message", "[Request interrupted by user",
    "Goal check-in",
)
# What the raw listing skips beyond the one list: a second named tuple, added to it (never a copy of it).
RAW_EXTRA = ("Caveat:", "[Request interrupted", "[SYSTEM")
HANDOFF = (" [inside a /compact command: may be the assistant's own handoff line; "
           "find the words elsewhere before calling it the principal's rule]")


class RecordError(Exception):
    """A missing or unreadable input: the verb reports it with a reason and appends nothing."""


def _extra_prefixes(cfg):
    """The prefixes the project adds (loop.json "not_principal_prefixes"): a text that starts with one is not the principal's."""
    extra = cfg.get("not_principal_prefixes") or []
    if isinstance(extra, str):
        extra = [extra]
    return tuple(str(x) for x in extra if str(x))


def typed_text(obj, prefixes):
    """The principal's typed text of a user record, or None."""
    msg = obj.get("message")
    if obj.get("type") != "user" or obj.get("isCompactSummary") or not isinstance(msg, dict) or msg.get("role") != "user":
        return None
    content = msg.get("content")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return None
        text = "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    else:
        return None
    text = text.strip()
    if not text or text.startswith(prefixes):
        return None
    if obj.get("isMeta") and (text.startswith("[Image: original ") or (text.startswith("#") and len(text) > SKILL_BODY_CHARS)):
        return None   # the harness describing an image the assistant read, or a skill body it injected: not the principal's words
    return text


def dialog_text(obj, ask_ids):
    """The principal's answers to a question dialog: the tool result of an AskUserQuestion call, matched by tool_use_id; or None."""
    msg = obj.get("message")
    if obj.get("type") != "user" or obj.get("isCompactSummary") or not isinstance(msg, dict) or not isinstance(msg.get("content"), list):
        return None
    out = []
    for b in msg["content"]:
        if isinstance(b, dict) and b.get("type") == "tool_result" and isinstance(b.get("tool_use_id"), str) and b["tool_use_id"] in ask_ids:
            c = b.get("content")
            out.append(c if isinstance(c, str) else "\n".join(x.get("text", "") for x in (c if isinstance(c, list) else []) if isinstance(x, dict)))
    return "\n".join(out).strip() or None


def queued_text(obj, prefixes):
    """The text of a message typed while a turn was running (a queue record), or None. The prefixes are the harness notices
    (NOT_PRINCIPAL) and the project's own: a message that begins with one is not the principal's. Other text is kept, HTML
    included, as typed_text keeps it."""
    if obj.get("type") != "queue-operation" or obj.get("operation") != "enqueue" or not isinstance(obj.get("content"), str):
        return None
    text = obj["content"].strip()
    if not text or text.startswith(prefixes):
        return None
    return text


def _prompt_text(att):
    """The text of a queued_command attachment: its prompt when that is a string; else the "text" of each item of its prompt,
    a list, joined by a newline (typed_text joins the text blocks of a message the same way); None when there is none."""
    prompt = att.get("prompt")
    if isinstance(prompt, str):
        text = prompt
    elif isinstance(prompt, list):
        text = "\n".join(x["text"] for x in prompt if isinstance(x, dict) and isinstance(x.get("text"), str))
    else:
        return None
    return text.strip() or None


def _blocks(obj):
    """The text blocks of a user row, stripped, in order (a string content is one block); an empty block is not one."""
    msg = obj.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(content, str):
        items = [content]
    elif isinstance(content, list):
        items = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    else:
        items = []
    return [t.strip() for t in items if isinstance(t, str) and t.strip()]


def delivered_text(obj, prefixes):
    """(kind, text) of a queued_command attachment. "midturn": a message the principal queued, delivered between two tool calls.
    "host": the host speaking, which is not banked, and neither is the queued text it delivers: a commandMode other than a
    prompt, or a text that starts with one of the prefixes. (None, None): any other row, or an attachment with no text."""
    att = obj.get("attachment")
    if obj.get("type") != "attachment" or not isinstance(att, dict) or att.get("type") != "queued_command":
        return None, None
    text = _prompt_text(att)
    if text is None:
        return None, None
    if att.get("commandMode") not in (None, "prompt") or text.startswith(prefixes):
        return "host", text
    return "midturn", text


def principal_prefixes(cfg):
    """The prefixes that mark a text as not the principal's: the built-in notices, and the ones loop.json adds."""
    return NOT_PRINCIPAL + _extra_prefixes(cfg)


def _row(raw):
    """The JSON object of one line of a transcript (bytes or text); None for a line that is not one, an unparsable line included."""
    try:
        obj = json.loads(raw)
    except ValueError:
        return None
    return obj if isinstance(obj, dict) else None


def delivery_of(obj):
    """(text, blocks) of a row that can deliver a queued message, or None: the one reading of a row that pending and the bank share.
    A user row that is neither a sidechain row nor a compaction summary: its text is its text blocks joined by one newline, stripped,
    and its blocks are its non-empty text blocks, stripped (a match inside a tool_result block does not count). A queued_command
    attachment: its prompt text, with no blocks. Any other row delivers nothing."""
    if obj.get("type") == "user":
        if obj.get("isSidechain") or obj.get("isCompactSummary"):
            return None
        msg = obj.get("message")
        content = msg.get("content") if isinstance(msg, dict) else None
        if isinstance(content, str):
            return content.strip(), _blocks(obj)
        if isinstance(content, list):
            items = [b.get("text") for b in content if isinstance(b, dict) and b.get("type") == "text"]
            return "\n".join(t for t in items if isinstance(t, str)).strip(), _blocks(obj)
        return None
    att = obj.get("attachment")
    if obj.get("type") == "attachment" and isinstance(att, dict) and att.get("type") == "queued_command":
        text = _prompt_text(att)
        return (text, None) if text else None
    return None


def delivers(texts, text, blocks=None):
    """The indices, into texts (the waiting messages, oldest first), of the messages that one row delivers: the one rule that pending
    and the bank both apply. text is the row's text, stripped; blocks are its text blocks when it has several, None for an attachment.
    In this order: (a) the text is exactly one waiting message: that one, the oldest of equal texts; (b) the row has two or more blocks
    and each block is a waiting message, equal texts counted as often as they wait: each of them; (c) the text is cut exactly into two
    or more waiting messages joined by one newline each, every message used once: the first cut found when the messages are tried
    oldest first, each of them; (d) anything else delivers nothing, so a waiting message that is only part of other text stays
    waiting."""
    if not text or not texts:
        return []
    for i, w in enumerate(texts):
        if w == text:
            return [i]
    if blocks is not None and len(blocks) >= 2:
        picked = _each_block(texts, blocks)
        if picked is not None:
            return picked
    return _cut(texts, text) or []


def _each_block(texts, blocks):
    """The index of the oldest waiting message equal to each block, the indices distinct; None when a block is no waiting message."""
    used, picked = set(), []
    for b in blocks:
        i = next((j for j, w in enumerate(texts) if w == b and j not in used), None)
        if i is None:
            return None
        used.add(i)
        picked.append(i)
    return picked


def _cut(texts, text):
    """The first cut of text into two or more waiting messages joined by one newline each, every message used once, the messages tried
    oldest first: a depth-first search that remembers each dead end (the state is the place in the text and the texts still unused, so
    a dead end is not searched again). The indices of the messages in the order of the text; None when there is no cut."""
    dead = set()

    def go(pos, unused, chosen):
        for k, i in enumerate(unused):
            w = texts[i]
            if not text.startswith(w, pos):
                continue
            end = pos + len(w)
            if end == len(text):
                if chosen:                      # the one before it makes two or more
                    return chosen + [i]
                continue
            if text[end] != "\n":
                continue
            rest = unused[:k] + unused[k + 1:]
            key = (end + 1, tuple(sorted(texts[j] for j in rest)))
            if key in dead:
                continue
            found = go(end + 1, rest, chosen + [i])
            if found is not None:
                return found
            dead.add(key)
        return None

    return go(0, tuple(range(len(texts))), [])


def _is_command(text):
    """A slash command (a "/" then a letter) is run by the engine, not read by the model: it is never a waiting message."""
    return len(text) > 1 and text[0] == "/" and text[1].isalpha()


def _step(waiting, obj, n, prefixes):
    """Applies the row obj, the n-th line of its transcript, to the list of waiting messages: a row that delivers some of them (see
    delivers) takes those out; a queue row that is the principal's and not a command joins the list. Rows come in file order, so a
    delivery takes out only the messages queued before it."""
    d = delivery_of(obj)
    if d is not None and waiting:
        gone = set(delivers([w["text"] for w in waiting], *d))
        waiting[:] = [w for i, w in enumerate(waiting) if i not in gone]
    text = queued_text(obj, prefixes)
    if text is not None and not _is_command(text):
        at = obj.get("timestamp")
        waiting.append({"line": n, "at": at if isinstance(at, str) else None, "text": text})


def pending(path, prefixes=NOT_PRINCIPAL):
    """The principal's typed messages still waiting in the queue of a transcript, in file order, as [{"line", "at", "text"}]: line is
    1-based, at the row's timestamp (None when it has none), text the stripped message. A queued message waits until a later row
    delivers it. An unparsable line is skipped; a missing or unreadable file raises OSError."""
    waiting = []
    with open(path, "rb") as fh:
        for n, raw in enumerate(fh, 1):
            obj = _row(raw)
            if obj is not None:
                _step(waiting, obj, n, prefixes)
    return waiting


def _read_state(path):
    """The state file as a dict: {} when there is none, or it is empty. RecordError when it cannot be read or is not a JSON object."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeDecodeError) as e:
        raise RecordError(f"the state file {path} cannot be read ({e})") from None
    if not text.strip():
        return {}
    try:
        d = json.loads(text)
    except ValueError:
        raise RecordError(f"the state file {path} is not JSON") from None
    if not isinstance(d, dict):
        raise RecordError(f"the state file {path} is not a JSON object")
    return d


def _valid_state(st):
    """Whether the keys that pending_since keeps have the types it writes."""
    def count(v):
        return isinstance(v, int) and not isinstance(v, bool) and v >= 0
    waiting = st.get("waiting")
    return (count(st.get("size")) and count(st.get("offset")) and count(st.get("lines")) and isinstance(st.get("open_tail"), bool)
            and isinstance(waiting, list) and all(
                isinstance(w, dict) and count(w.get("line")) and isinstance(w.get("text"), str)
                and (w.get("at") is None or isinstance(w.get("at"), str)) for w in waiting))


def _write_state(path, d):
    """Replaces the state file in one step, through a file of the same folder: a reader sees the old file or the new one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d))
    os.replace(tmp, str(path))


def pending_since(state, src, prefixes=NOT_PRINCIPAL):
    """(waiting, bytes read): what pending returns for the transcript src, read incrementally through the state file, which keeps
    the byte offset read so far, the line count, the messages still waiting and the size seen at the last call. A call reads the
    bytes appended since the offset, and none when the size is unchanged. A file that became shorter than the offset is read again
    from its start, and so is a state that names another transcript. A last line that is not whole yet is not consumed: it is read
    again, whole. RecordError when the state file cannot be read or holds no read position, or the transcript cannot be read."""
    state, src = pathlib.Path(state), os.path.abspath(os.fspath(src))
    try:
        raw = _read_state(state)
        mine = raw if raw.get("src") == src else {}
        if mine and not _valid_state(mine):
            raise RecordError(f"the state file {state} holds no valid read position")
        size = os.path.getsize(src)
    except OSError as e:
        raise RecordError(f"{src} cannot be read ({e.strerror or e})") from None
    offset = mine.get("offset", 0)
    if offset > size:                                    # the file became shorter: it is read again from its start
        mine, offset = {}, 0
    if mine and mine["size"] == size:                    # unchanged since the last call: nothing is read
        return list(mine["waiting"]), 0
    waiting, lines, open_tail = list(mine.get("waiting", [])), mine.get("lines", 0), mine.get("open_tail", False)
    nread = 0
    try:
        with open(src, "rb") as fh:
            fh.seek(offset)
            while True:
                line = fh.readline()
                if not line:
                    break
                whole = line.endswith(b"\n")
                if open_tail and line == b"\n":          # the newline of a row that is already counted: it starts no line
                    open_tail, offset, nread = False, offset + 1, nread + 1
                    continue
                open_tail = False
                obj = _row(line)
                nread += len(line)
                if not whole and obj is None:            # a last line that is not whole yet: not consumed, read again next time
                    break
                lines += 1
                if obj is not None:
                    _step(waiting, obj, lines, prefixes)
                offset += len(line)
                if not whole:                            # a whole row whose newline is not written yet
                    open_tail = True
                    break
    except OSError as e:
        raise RecordError(f"{src} cannot be read ({e.strerror or e})") from None
    try:
        _write_state(state, {"src": src, "size": size, "offset": offset, "lines": lines, "open_tail": open_tail, "waiting": waiting})
    except OSError as e:
        raise RecordError(f"the state file {state} cannot be written ({e.strerror or e})") from None
    return waiting, nread


def scan(path, prefixes):
    """The events of a transcript, in file order: the principal's messages, of a kind: typed (a user row), dialog (an answer to a
    question dialog), queued (an enqueue row: typed while a turn was running), midturn (a queued_command attachment: a queued
    message delivered between two tool calls) or host (a queued_command attachment that is the host speaking; see delivered_text).
    A row that delivers queued messages and is none of these is a row event: it is not banked. Each event that can deliver carries
    its delivery (delivery_of) under "deliver"."""
    ask_ids, events = set(), []
    with open(path, "rb") as fh:   # bytes, a line at a time; a partial last line is skipped and a later run picks it up
        for n, line in enumerate(fh, 1):
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if not isinstance(obj, dict):
                continue
            if obj.get("type") == "assistant":
                msg = obj.get("message")
                blocks = msg.get("content") if isinstance(msg, dict) else None
                for b in (blocks if isinstance(blocks, list) else []):
                    if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "AskUserQuestion":
                        ask_ids.add(b.get("id"))
                continue
            kind, text = "typed", typed_text(obj, prefixes)
            if text is None:
                kind, text = "dialog", dialog_text(obj, ask_ids)
            if text is None:
                kind, text = "queued", queued_text(obj, prefixes)
            if text is None:
                kind, text = delivered_text(obj, prefixes)
            d = delivery_of(obj)
            if text is None:
                if not d or not d[0]:
                    continue
                kind, text = "row", d[0]          # a row that delivers and says nothing of the principal's: never banked
            ev = {"kind": kind, "key": obj.get("uuid") or f"{pathlib.Path(path).stem}:line:{n}", "line": n, "timestamp": obj.get("timestamp"),
                  "text": text, "meta": bool(obj.get("isMeta")),
                  "scheduled": obj.get("turnOrigin") == "scheduled" or bool(obj.get("wakeupSource")), "deliver": d}
            events.append(ev)
    return events


def load_bank(path):
    """The keys, the (second, text) pairs and the long texts already in the bank. RecordError names a line that is not a record."""
    seen, stamps, long_texts = set(), set(), set()
    if not path.is_file():
        return seen, stamps, long_texts
    with path.open(encoding="utf-8") as fh:
        for n, raw in enumerate(fh, 1):
            if not raw.strip():
                continue
            try:
                r = json.loads(raw)
            except ValueError:
                r = None
            if not isinstance(r, dict):
                raise RecordError(f"the bank {path} has a line {n} that is not a record")
            text = r.get("text") or ""
            seen.add(r.get("key"))
            stamps.add(((r.get("timestamp") or "")[:19], text))
            if len(text) >= LONG_REPEAT:
                long_texts.add(text)
    return seen, stamps, long_texts


def plan(events, seen, stamps, long_texts):
    """The records to bank, in file order. A queued message is one utterance: banked once, under the key of its enqueue row, with
    the time it was typed; when a row delivers it (delivers: the same rule that pending applies), also the time of the delivery and
    the way: at the end of a turn (a user row, banked or not, whose text, blocks or cut delivers it) or between two tool calls (a
    queued_command attachment). The row that delivers a message is not banked itself. A notice of the host delivers too, and what
    it delivers is not banked. A delivery that no enqueue row precedes is banked under its own key and time. A repeat within the
    same second, or a scheduled repeat, is skipped. A key that the bank holds stands, and so does the key of the row that delivered
    the message: nothing is banked twice."""
    waiting = []      # the queued events not delivered yet, oldest first
    took = {}         # line of a queued event -> (the row that delivered it, its way)
    host, carrier, mid = set(), set(), set()   # lines: queued events a notice delivered; rows that delivered; attachments that delivered
    for ev in events:
        if ev["kind"] == "queued":
            waiting.append(ev)
            continue
        if ev["deliver"] is None or not waiting:
            continue
        hit = delivers([w["text"] for w in waiting], *ev["deliver"])
        if not hit:
            continue
        k, gone = ev["kind"], set(hit)
        for i in hit:
            if k == "host":
                host.add(waiting[i]["line"])
            else:
                took[waiting[i]["line"]] = (ev, "mid-turn" if k == "midturn" else "end-of-turn")
        if k == "midturn":
            mid.add(ev["line"])
        elif k != "host":
            carrier.add(ev["line"])
        waiting = [w for i, w in enumerate(waiting) if i not in gone]
    new = []
    for ev in events:
        k, line = ev["kind"], ev["line"]
        if k in ("host", "row") or line in host or line in carrier or line in mid:
            continue
        if k == "queued":                                  # its row is the delivering one, when one delivered it
            row, way = took.get(line, (None, None))
            kind, when, delivered_at = "queued", ev["timestamp"], (row["timestamp"] if row else None)
        elif k == "midturn":                               # a delivery with no enqueue row before it: its own row and time
            row, way = None, "mid-turn"
            kind, when, delivered_at = "queued", ev["timestamp"], ev["timestamp"]
        else:                                              # typed at a prompt, or an answer to a question dialog
            row, way = None, None
            kind, when, delivered_at = k, ev["timestamp"], None
        if ev["key"] in seen or (row is not None and row["key"] in seen):
            continue
        src, text = (row if row is not None else ev), ev["text"]
        stamp = ((when or "")[:19], text[:MAX_CHARS])
        if stamp in stamps or (src["scheduled"] and len(text) >= LONG_REPEAT and text[:MAX_CHARS] in long_texts):
            continue
        stamps.add(stamp)
        if len(text) >= LONG_REPEAT:
            long_texts.add(text[:MAX_CHARS])
        new.append({"key": ev["key"], "line": line, "kind": kind, "timestamp": when, "chars": len(text),
                    "truncated": len(text) > MAX_CHARS, "meta": src["meta"], "delivered_at": delivered_at,
                    "delivered_via": way, "text": text[:MAX_CHARS]})
    return new


def _jsonl(obj):
    """One JSON object as one line of text. A raw line or paragraph separator would split the row for splitlines() readers, so
    it is written as an escape."""
    return json.dumps(obj, ensure_ascii=False).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029").replace("\x85", "\\u0085")


def append(path, items):
    """Append the new records, one JSON object per line. The bank is never rewritten."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for item in items:
            f.write(_jsonl(item) + "\n")


@contextlib.contextmanager
def _one_writer(cfg):
    """The bank is read, planned against and appended to under one lock, so that two runs that overlap (a stop hook and a
    run by hand, two sessions of a project that stop together) cannot both append the same message. The lock file is in the
    state directory, which is never committed."""
    with open(cfg.state("bank.lock"), "w") as fh:
        if fcntl is not None:
            fcntl.flock(fh, fcntl.LOCK_EX)
        yield


WAYS = (("typed", "typed at a prompt"), ("dialog", "answers to a question"),
        ("end-of-turn", "queued and delivered at the end of a turn"), ("mid-turn", "queued and delivered in the middle of a turn"),
        ("waiting", "queued and not delivered yet"), ("command", "queued commands (the engine runs them)"))


def _way(r):
    """The way a banked row counts under: its kind; for a queued row, the way it was delivered, else a slash command (the engine runs
    it, and no row delivers it) or a message still waiting."""
    if r["kind"] != "queued":
        return r["kind"]
    return r.get("delivered_via") or ("command" if _is_command(r["text"]) else "waiting")


def ways(rows):
    """How many of the rows each way took, every way named, so that a zero is seen: typed at a prompt, an answer to a question, a
    queued message delivered at the end of a turn or between two tool calls, one not delivered yet, and a queued command."""
    c = collections.Counter(_way(r) for r in rows)
    return ", ".join(f"{label} {c[key]}" for key, label in WAYS)


def cmd_bank(args, cfg):
    why = config.no_project(cfg, "record bank")
    if why:
        print(why, file=sys.stderr)
        return 1
    src = pathlib.Path(args.src) if args.src else cfg.transcript()
    if src is None:
        print('record bank: no transcript is named (pass --src, or set LOOP_TRANSCRIPT: a hook passes the one its event names; '
              'with "sessions": "all" in loop.json the newest on this machine is taken); nothing banked', file=sys.stderr)
        return 1
    if not src.is_file() or src.stat().st_size == 0:
        print(f"record bank: {src} is not a transcript with content; nothing banked", file=sys.stderr)
        return 1
    bank = cfg.path("bank")
    try:
        with _one_writer(cfg):
            seen, stamps, long_texts = load_bank(bank)
            new = plan(scan(src, principal_prefixes(cfg)), seen, stamps, long_texts)
            if new:
                append(bank, new)
    except (RecordError, OSError, ValueError) as e:
        print(f"record bank: {e}", file=sys.stderr)
        return 1
    if not new:
        print(f"nothing new ({ways([])}); bank holds {len(seen)} messages")
        return 0
    print(f"banked {len(new)} new messages of the principal (lines {new[0]['line']} to {new[-1]['line']}): {ways(new)}; "
          f"bank holds {len(seen) + len(new)}")
    return 0


def _git(root, *args):
    """The stdout of a git command in the project, as text; RecordError as in _git_bytes."""
    return _git_bytes(root, *args).decode("utf-8", "replace")


def _git_bytes(root, *args):
    """The stdout of a git command in the project; RecordError when git is missing or the command fails (no such ref, no repository)."""
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    except OSError as e:
        raise RecordError(f"git is not available ({e})") from None
    if r.returncode != 0:
        raise RecordError(f"git {args[0]} failed (no such ref, or not a repository): {r.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return r.stdout


def backup_refs(cfg):
    """Every ref under <remote>/<prefix> from the "backup" key: the branches the keep verb writes."""
    b = cfg["backup"]
    prefix = str(b.get("prefix", "backup/")).rstrip("/")
    return _git(cfg.root, "for-each-ref", "--format=%(refname:short)", f"refs/remotes/{b.get('remote', 'origin')}/{prefix}").split()


def ref_lines(root, ref):
    """The lines of the transcripts a git ref holds (its transcripts/ files, not the sub-agents'); RecordError when the ref is
    not there. A backup cuts a transcript into parts at arbitrary bytes (NAME.parts/part-NNN), so the parts of one transcript
    are read as one stream: a record, or a character, that a part boundary cuts is whole again. One part is held at a time."""
    names = _git(root, "ls-tree", "-r", "--name-only", ref).split("\n")
    groups = collections.defaultdict(list)
    for n in names:
        if n.startswith("transcripts/") and "agent-" not in n and "subagent" not in n and (n.endswith(".jsonl") or "/part-" in n):
            head, sep, _ = n.partition(".parts/")
            groups[head + sep if sep else n].append(n)
    for g in sorted(groups):
        rest = b""
        for n in sorted(groups[g]):
            *whole, rest = (rest + _git_bytes(root, "show", f"{ref}:{n}")).split(b"\n")
            for line in whole:
                yield line.decode("utf-8", "replace")
        if rest:
            yield rest.decode("utf-8", "replace")


def typed_messages(lines, skip):
    """[(timestamp, text)] in time order: what the principal typed, once. A /command line is dropped when its arguments are listed."""
    out, seen = [], set()
    for line in lines:
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if not isinstance(o, dict):
            continue
        ts, texts = (o.get("timestamp") or "")[:19], []
        msg = o.get("message")
        if o.get("type") == "queue-operation" and o.get("operation") == "enqueue" and isinstance(o.get("content"), str):
            texts.append(o["content"])
        elif o.get("type") == "user" and not (o.get("isSidechain") or o.get("isMeta") or o.get("isCompactSummary")):
            m = msg.get("content") if isinstance(msg, dict) else None
            items = [m] if isinstance(m, str) else [c for c in (m if isinstance(m, list) else []) if isinstance(c, dict) and c.get("type") == "text"]
            texts.extend(b if isinstance(b, str) else b.get("text", "") for b in items)
        for t in texts:
            t = t.strip()
            mm = re.search(r"<command-args>(.*?)</command-args>", t, re.S)
            if mm:
                t = mm.group(1).strip()
            elif not t or t.startswith("<") or t.startswith(skip):
                continue
            if t and t not in seen:
                seen.add(t)
                out.append((ts, t))
    typed = {t for _, t in out}

    def echo(t):   # "/goal <args>" next to the args themselves
        m = re.match(r"/[\w-]+\s+(.*)", t, re.S)
        return bool(m) and m.group(1).strip() in typed

    return sorted((x for x in out if not echo(x[1])), key=lambda x: x[0])


def cmd_raw(args, cfg):
    skip = principal_prefixes(cfg) + RAW_EXTRA
    try:
        pat = re.compile(args.grep, re.I) if args.grep else None
    except re.error as e:
        print(f"record raw: --grep is not a regular expression ({e})", file=sys.stderr)
        return 2
    srcs, failed = list(args.sources), False
    if args.all or not srcs:
        live = cfg.transcript()
        srcs = [str(live)] if live else []
        try:
            srcs += backup_refs(cfg)
        except RecordError as e:
            print(f"record raw: {e}", file=sys.stderr)
            failed = True
        if not srcs:
            print("record raw: no transcript and no backup ref to list; nothing listed", file=sys.stderr)
            return 1
    for s in srcs:
        try:
            if os.path.isfile(s):
                with open(s, encoding="utf-8", errors="replace") as fh:
                    msgs = typed_messages(fh, skip)
            else:
                msgs = typed_messages(ref_lines(cfg.root, s), skip)
        except (RecordError, OSError) as e:
            print(f"record raw: {s}: {e}", file=sys.stderr)
            failed = True
            continue
        shown = [x for x in msgs if not pat or pat.search(x[1])]
        print(f"##### {s}: {len(msgs)} messages" + (f", {msgs[0][0][:10]} to {msgs[-1][0][:10]}" if msgs else "")
              + (f"; {len(shown)} match" if pat else ""))
        for ts, t in shown:
            print(f"{ts[:16]} | " + (t if args.full else t[:args.width]).replace("\n", " / "))
    return 1 if failed else 0


def snippets(text, pats, every, width=240):
    """(line number, text) of the lines that match: any pattern, or all of them when every is set; cut to width characters around the match."""
    for ln, line in enumerate(text.split("\n"), 1):
        hits = [p.search(line) for p in pats]
        if (all(hits) if every else any(hits)):
            m = next(h for h in hits if h)
            a = max(0, m.start() - width // 2)
            yield ln, re.sub(r"\s+", " ", line[a:a + width]).strip()


def demoted(rec, prefixes):
    """A bank record the search does not read: a notice of the tool, or a long skill body the bank kept before its 'meta' field."""
    t = rec.get("text") or ""
    return t.startswith(prefixes) or (t.startswith("#") and rec.get("chars", len(t)) > SKILL_BODY_CHARS and "meta" not in rec)


def words_files(root, pattern):
    """The files a words glob names: relative globs are under the project root."""
    p = os.path.expanduser(str(pattern))
    if os.path.isabs(p):
        names = glob.glob(p, recursive=True)
    else:
        names = [os.path.join(str(root), x) for x in glob.glob(p, root_dir=str(root), recursive=True)]
    return [pathlib.Path(x) for x in sorted(names) if os.path.isfile(x)]


def quoted_parts(line):
    """The quoted parts of a line of a words file, as (start, end, text) with their offsets into the line. The principal's words
    are the quoted parts; the rest of the line (notes of the assistant, in the words files) is not read. `search` and gate's
    `verify` both read a words file through this function."""
    return [(m.start(1), m.end(1), m.group(1)) for m in QUOTED.finditer(line)]


def search(cfg, words, every=False, limit=60):
    """(hits, total, notes). A hit is (source, when, where, snippet): a line of the bank, or the quoted words of a words file.
    The notes name what could not be read, so that a search which found nothing is not taken as a pass over what it did not read."""
    pats = [re.compile(re.escape(w), re.I) for w in words]
    prefixes = principal_prefixes(cfg)
    out, seen, notes = [], set(), []

    def add(src, when, where, snip):
        if snip not in seen:
            seen.add(snip)
            out.append((src, when, where, snip))

    bank = cfg.path("bank")
    if bank.is_file():
        with bank.open(encoding="utf-8") as fh:
            for n, raw in enumerate(fh, 1):
                if not raw.strip():
                    continue
                try:
                    rec = json.loads(raw)
                except ValueError:
                    notes.append(f"bank line {n} is not JSON; not searched")
                    continue
                if not isinstance(rec, dict) or demoted(rec, prefixes):
                    continue
                text = rec.get("text") or ""
                where = "line %s%s" % (rec.get("line", "?"), HANDOFF if "<command-name>/compact" in text else "")
                for _, s in snippets(text, pats, every):
                    add("bank", (rec.get("timestamp") or "")[:16], where, s)
    else:
        notes.append(f"no bank at {bank}; only the words files were searched")
    globs = cfg["words"]
    for pattern in ([globs] if isinstance(globs, str) else globs):
        files = words_files(cfg.root, pattern)
        if not files:
            notes.append(f"the words glob {pattern!r} matches no file")
        for path in files:
            rel = os.path.relpath(path, cfg.root)
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
            except OSError as e:
                notes.append(f"{rel} cannot be read ({e})")
                continue
            for ln, line in enumerate(lines, 1):
                quoted = " ".join(t for _, _, t in quoted_parts(line))   # the quoted parts only: the rest of a words line may be notes
                if quoted:
                    hits = [p.search(quoted) for p in pats]
                    if (all(hits) if every else any(hits)):
                        add("words", "", f"{rel} line {ln}", re.sub(r"\s+", " ", quoted)[:240])
    return out[:limit], len(out), notes


def cmd_find(args, cfg):
    hits, total, notes = search(cfg, args.words, args.all, args.max)
    for src, when, where, snip in hits:
        print("[%s %s %s] %s" % (src, when, where, snip))
    print("%d hit(s)%s" % (total, "" if total <= args.max else " (first %d shown)" % args.max))
    for note in notes:
        print(f"record find: {note}", file=sys.stderr)
    return 1 if notes else 0


def cmd_pending(args, cfg):
    src = pathlib.Path(args.src) if args.src else cfg.transcript()
    if src is None:
        print('record pending: no transcript is named (pass --src, or set LOOP_TRANSCRIPT: a hook passes the one its event names; '
              'with "sessions": "all" in loop.json the newest on this machine is taken); nothing read', file=sys.stderr)
        return 1
    try:
        waiting = pending(src, principal_prefixes(cfg))
    except OSError as e:
        print(f"record pending: {src} cannot be read ({e.strerror or e})", file=sys.stderr)
        return 1
    for w in waiting:
        print(_jsonl(w))
    return 0


def cmd_quotes(args, cfg):
    from loop import quotes   # quotes.py reads gate.py, which reads this module: it is imported when the verb runs
    return quotes.run(cfg, args.file, args.also, args.min, args.out)


def main(argv=None):
    p = argparse.ArgumentParser(prog="loop record", description="Bank what the principal says, once, verbatim, with its time; search it.")
    sub = p.add_subparsers(dest="cmd", required=True, metavar="{bank,raw,find,pending,quotes}")
    b = sub.add_parser("bank", help="append the new messages of the principal to the bank")
    b.add_argument("--src", metavar="FILE", help="the transcript (default: the live one)")
    r = sub.add_parser("raw", help="list what the principal typed, once, from a transcript or the backup refs")
    r.add_argument("--all", action="store_true", help="the live transcript and every backup ref (the default with no SOURCE)")
    r.add_argument("sources", nargs="*", metavar="SOURCE", help="a transcript file, or a git ref that holds transcripts")
    r.add_argument("--grep", metavar="REGEX", help="only the messages that match (case-insensitive)")
    r.add_argument("--full", action="store_true", help="whole messages")
    r.add_argument("--width", type=int, default=150, help="characters per message (default 150)")
    f = sub.add_parser("find", help="search the bank and the words files")
    f.add_argument("--all", action="store_true", help="every word must occur in the same line")
    f.add_argument("--max", type=int, default=60, metavar="N", help="at most N hits are shown (default 60)")
    f.add_argument("words", nargs="+", metavar="WORD")
    d = sub.add_parser("pending", help="list the principal's messages still waiting in a transcript's queue, one JSON line each")
    d.add_argument("--src", metavar="FILE", help="the transcript (default: the live one)")
    q = sub.add_parser("quotes", help="check each quoted text of a report against the bank and the words files: FOUND, LOOSE, ELSEWHERE or MISSING")
    q.add_argument("file", metavar="FILE", help="the report whose quoted texts are checked")
    q.add_argument("--also", action="append", default=[], metavar="FILE", help="another file a quote may be found in (ELSEWHERE, never FOUND); repeat for more")
    q.add_argument("--min", type=int, default=12, metavar="N", help="skip the quotes shorter than N characters (default 12)")
    q.add_argument("--out", metavar="F", help="also write the table to F")
    args = p.parse_args(argv)
    cfg = config.load()
    return {"bank": cmd_bank, "raw": cmd_raw, "find": cmd_find, "pending": cmd_pending, "quotes": cmd_quotes}[args.cmd](args, cfg)
