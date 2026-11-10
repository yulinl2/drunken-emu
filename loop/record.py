"""Bank what the principal says, once, verbatim, with its time; search the bank and the words files for what was said.

The principal's messages come from the session transcript: what was typed, the answers to a question dialog, and what was
typed while a turn was running (a queued message). Three subcommands:
  bank  appends each new message of the principal to the bank, an append-only file of JSON lines (the "bank" key)
  raw   lists what the principal typed, once, from a transcript file or from the git refs of the backup branches
  find  searches the bank and the words files (the "words" globs) for the given words, case-insensitively

INVARIANT: every message of the principal in the transcript is in the bank once, verbatim, with its time, and no other text is.
FAILS WHEN: a typed message is in the transcript and not in the bank, or in it twice; a tool result or a notice of the harness is banked; a missing transcript, bank or ref is reported as nothing new (loop/tests/test_record.py)

usage: python3 -I bin/loop record bank [--src FILE]
       python3 -I bin/loop record raw [--all | SOURCE ...] [--grep REGEX] [--full] [--width N]
       python3 -I bin/loop record find [--all] [--max N] WORD [WORD ...]
"""
import argparse
import collections
import glob
import json
import os
import pathlib
import re
import subprocess
import sys

from loop import config

MAX_CHARS = 20000        # a longer message is banked cut to this many characters, with "truncated": true
SKILL_BODY_CHARS = 3000  # a skill body the harness injected, longer than this, is not the principal's words
LONG_REPEAT = 200        # a scheduled delivery repeating a banked text this long is a cron fire or a wake, not typing
QUOTED = re.compile(r'["\u201c\u300c](.+?)["\u201d\u300d]')   # in a words file, the principal's words are the quoted parts

# Text that starts with one of these is not the principal's: notices of the tool itself, hook output, compaction summaries,
# interrupt markers. A prefix that names one project's own jobs is not here: it goes in loop.json as "not_principal_prefixes".
NOT_PRINCIPAL = (
    "<task-notification>", "Stop hook feedback", "[SYSTEM NOTIFICATION", "UserPromptSubmit hook", "PostToolUse", "PreToolUse",
    "<system-reminder>", "This session is being continued", "Called the Read tool", "Result of calling",
    "Tool loaded.", "<artifact-content-authored-by-others", "<local-command-stdout>", "<local-command-caveat>",
    "# /loop", "The following skills were", "Base directory for this skill", "(Re-invocation of",
    "This session's worker process was restarted", "Your response above was stopped by a safety classi",
    "A session-scoped Stop hook is now active", "Another Claude session sent a message", "[Request interrupted by user",
)
# The raw listing drops these as well (its own list, kept as it was).
RAW_SKIP = ("This session is being continued", "Caveat:", "Goal check-in", "[Request interrupted", "[SYSTEM", "UserPromptSubmit hook")
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
    """The text of a message typed while a turn was running (a queue record, read as the raw listing reads it), or None."""
    if obj.get("type") != "queue-operation" or obj.get("operation") != "enqueue" or not isinstance(obj.get("content"), str):
        return None
    text = obj["content"].strip()
    if not text or text.startswith("<") or text.startswith(prefixes):
        return None
    return text


def scan(path, prefixes):
    """The principal's messages of a transcript, in file order: kind typed, dialog or queued (typed while a turn was running)."""
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
                continue
            events.append({"kind": kind, "key": obj.get("uuid") or f"line:{n}", "line": n, "timestamp": obj.get("timestamp"),
                           "text": text, "meta": bool(obj.get("isMeta")),
                           "scheduled": obj.get("turnOrigin") == "scheduled" or bool(obj.get("wakeupSource"))})
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
    """The events to bank, in file order. A queued message that the transcript later delivers as a message is one message:
    the delivered record is banked and the queued one is not. A queued record that an earlier run banked stands, and its
    delivery is not banked again (the bank is append-only). A repeat within the same second, or a scheduled repeat, is skipped."""
    pending = collections.defaultdict(collections.deque)   # text -> keys of queued records still waiting, oldest first
    consumed, delivered_by = set(), {}
    for ev in events:
        if ev["kind"] == "queued":
            pending[ev["text"]].append(ev["key"])
        elif ev["kind"] == "typed" and pending[ev["text"]]:
            q = pending[ev["text"]].popleft()
            consumed.add(q)
            delivered_by[ev["key"]] = q
    new = []
    for ev in events:
        key, text = ev["key"], ev["text"]
        if key in seen or key in consumed:
            continue
        q = delivered_by.get(key)
        if q is not None and q in seen:
            continue
        stamp = ((ev["timestamp"] or "")[:19], text[:MAX_CHARS])
        if stamp in stamps or (ev["scheduled"] and len(text) >= LONG_REPEAT and text[:MAX_CHARS] in long_texts):
            continue
        stamps.add(stamp)
        if len(text) >= LONG_REPEAT:
            long_texts.add(text[:MAX_CHARS])
        new.append({"key": key, "line": ev["line"], "kind": ev["kind"], "timestamp": ev["timestamp"], "chars": len(text),
                    "truncated": len(text) > MAX_CHARS, "meta": ev["meta"], "text": text[:MAX_CHARS]})
    return new


def append(path, items):
    """Append the new records, one JSON object per line. The bank is never rewritten."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for item in items:
            # a raw line or paragraph separator would split the row for splitlines() readers, so it is written as an escape
            f.write(json.dumps(item, ensure_ascii=False).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
                    .replace("\x85", "\\u0085") + "\n")


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
        seen, stamps, long_texts = load_bank(bank)
        new = plan(scan(src, NOT_PRINCIPAL + _extra_prefixes(cfg)), seen, stamps, long_texts)
        if new:
            append(bank, new)
    except (RecordError, OSError, ValueError) as e:
        print(f"record bank: {e}", file=sys.stderr)
        return 1
    if not new:
        print(f"nothing new; bank holds {len(seen)} messages")
        return 0
    print(f"banked {len(new)} new messages of the principal (lines {new[0]['line']} to {new[-1]['line']}); bank holds {len(seen) + len(new)}")
    return 0


def _git(root, *args):
    """The stdout of a git command in the project; RecordError when git is missing or the command fails (no such ref, no repository)."""
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    except OSError as e:
        raise RecordError(f"git is not available ({e})") from None
    if r.returncode != 0:
        raise RecordError(f"git {args[0]} failed (no such ref, or not a repository): {r.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return r.stdout.decode("utf-8", "replace")


def backup_refs(cfg):
    """Every ref under <remote>/<prefix> from the "backup" key: the branches the keep verb writes."""
    b = cfg["backup"]
    prefix = str(b.get("prefix", "backup/")).rstrip("/")
    return _git(cfg.root, "for-each-ref", "--format=%(refname:short)", f"refs/remotes/{b.get('remote', 'origin')}/{prefix}").split()


def ref_lines(root, ref):
    """The lines of the transcripts a git ref holds (its transcripts/ files, not the sub-agents'); RecordError when the ref is not there."""
    names = _git(root, "ls-tree", "-r", "--name-only", ref).split("\n")
    for n in sorted(x for x in names if x.startswith("transcripts/") and "agent-" not in x and "subagent" not in x
                    and (x.endswith(".jsonl") or "/part-" in x)):
        yield from _git(root, "show", f"{ref}:{n}").split("\n")


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
    skip = RAW_SKIP + _extra_prefixes(cfg)
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


def search(cfg, words, every=False, limit=60):
    """(hits, total, notes). A hit is (source, when, where, snippet): a line of the bank, or the quoted words of a words file.
    The notes name what could not be read, so that a search which found nothing is not taken as a pass over what it did not read."""
    pats = [re.compile(re.escape(w), re.I) for w in words]
    prefixes = NOT_PRINCIPAL + _extra_prefixes(cfg)
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
                quoted = " ".join(QUOTED.findall(line))   # the quoted parts only: the other lines of a words file may be notes
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


def main(argv=None):
    p = argparse.ArgumentParser(prog="loop record", description="Bank what the principal says, once, verbatim, with its time; search it.")
    sub = p.add_subparsers(dest="cmd", required=True, metavar="{bank,raw,find}")
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
    args = p.parse_args(argv)
    cfg = config.load()
    return {"bank": cmd_bank, "raw": cmd_raw, "find": cmd_find}[args.cmd](args, cfg)
