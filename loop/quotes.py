"""Checks each quoted text of a report against the principal's own words, and says where each one stands: FOUND (the same words,
verbatim and in order, inside one record of the bank or one quoted part of a words file), LOOSE (the same words only once case,
dash, quote-mark and ellipsis differences are set aside), ELSEWHERE (the words occur only in a file named with --also: a copy, not
a record of the principal) or MISSING (nowhere). It measures whether the words are there, never whether they answer a question.
No transcript is read: the words come from the bank and from the words files, as record find reads them.

How a quote is found: the double quotation marks of a line are paired by kind, from left to right: a straight mark is closed by the
next straight mark, and an opening curly double mark (U+201C) only by the next closing curly double mark (U+201D). The text between a
pair is one quote, so a curly mark inside a straight quote, and a straight mark inside a curly one, is text of that quote. A table line
is read cell by cell, since a quote lies in one cell. Only then are the pairs shorter than --min left out. A line with a double mark
that pairs with no other cannot be read whole: it is named as having an unpaired double mark, no quote is read from that mark, and the
run fails (exit 1), even when every quote read from the line is FOUND. A straight mark has no direction: straight marks that are
no quotation marks (a unit mark after a number, a fragment of code), in even number on a line, pair with the marks of a quote on
that line; that quote is then not read, and when the texts between are shorter than --min the line is not named. A file that
keeps straight double marks for quoted words only does not meet this.

The apostrophe: gate.N makes the curly apostrophe U+2019 straight before it compares, so a quote that differs from its record only by
U+2019 against the straight apostrophe is FOUND, as at the gate. Every other difference of that kind is LOOSE: the left single quotation
mark U+2018, curly double marks inside a quote, a dash, the case of a letter.

INVARIANT: a quote is FOUND only when its parts occur verbatim in gate.N's form (which makes U+2019 straight), in order, inside one
record of the bank or one quoted part of a words line; the report and the table of --out are never a source; the exit is 0 only when
every quote is FOUND and no line has an unpaired double mark.
FAILS WHEN: a quote that differs from a record in case, in a dash, or in a quote mark other than U+2019 is FOUND; on a line whose straight marks
are all quotation marks, the text between two quotes is read as a quote, or a short quote hides the quote after it; a quote closed by a mark of the other kind is read; a line with an unpaired
double mark exits 0, or is not named in the output; the
parts of an ellipsis that lie in two records, or out of order, are FOUND; a text that occurs only in a file named with --also is FOUND;
a report with no quote exits 0; a source that cannot be read is not named as not read (loop/tests/test_quotes.py)

usage (through record): python3 -I bin/loop record quotes FILE [--also FILE ...] [--min 12] [--out F]
  exit 0: every quote FOUND, and no line with an unpaired double mark. 1: any other class, no quote at all, or a line with an
  unpaired double mark. 3: not evaluated (FILE, or both the bank and every words
  file, cannot be read). 2: a bad option, or an --out that is the report itself.
"""
import json
import pathlib
import re
import sys
import unicodedata

from loop import gate, record

FOUND, LOOSE, ELSEWHERE, MISSING = "FOUND", "LOOSE", "ELSEWHERE", "MISSING"
CLASSES = (FOUND, LOOSE, ELSEWHERE, MISSING)
CUT = 100                                  # characters of a quote the output shows (90 in the table of --out)
HANDOFF = "<command-name>/compact"         # a record with a /compact command: its arguments may be the assistant's own handoff line
LEFT_CURLY, RIGHT_CURLY = chr(0x201C), chr(0x201D)   # the curly double quotation marks (the straight one is the double quote)
MARKS = str.maketrans({**{chr(c): "'" for c in (0x2018, 0x2019, 0x201A, 0x201B)},
                       **{chr(c): '"' for c in (0x201C, 0x201D, 0x201E, 0x201F, 0x00AB, 0x00BB)},
                       **{chr(c): "-" for c in (0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2015, 0x2212)}})
ELLIPSIS = re.compile(r"\.\.\.|" + chr(0x2026))
CELL_LABEL = re.compile(r'\|\s*([^|"]{1,40}?)\s*\|')
BOLD_LABEL = re.compile(r'\*\*([^*"]{1,40}?)\*\*')
CLOSER = {'"': '"', LEFT_CURLY: RIGHT_CURLY}   # the mark that closes a quote which an opening double mark starts


def lenient(text):
    """The loose form of words: compatibility forms folded (NFKC), quote, dash and ellipsis marks made plain, spaces collapsed, case
    folded. The gate's form (gate.N) is stricter: it folds only the apostrophe and the spaces."""
    return " ".join(unicodedata.normalize("NFKC", text).translate(MARKS).split()).casefold()


def segments(quote):
    """The parts of a quote between its ellipses, in order, each stripped; an empty part is no part."""
    return [p.strip() for p in ELLIPSIS.split(quote) if p.strip()]


def in_order(parts, text):
    """Whether each part occurs in text, each after the end of the one before it: the words of an ellipsis, in one text."""
    if not parts:
        return False
    at = 0
    for part in parts:
        i = text.find(part, at)
        if i < 0:
            return False
        at = i + len(part)
    return True


def pair_marks(unit):
    """([the text of each quote], the number of marks that pair with no other) of one unit of a line: a cell of a table line, or the
    line itself. The marks are read from left to right: a double mark opens a quote, which its CLOSER mark ends, and the text between
    is the quote. So a curly mark inside a straight quote is text of that quote. A mark that opens no quote (a straight mark with no straight mark after it,
    or an opening curly mark with no closing curly mark after it), and a closing curly mark with no quote before it, are counted; no quote
    is read from them."""
    quotes, free, i = [], 0, 0
    while i < len(unit):
        ch = unit[i]
        if ch in CLOSER:
            end = unit.find(CLOSER[ch], i + 1)
            if end < 0:
                free += 1
                i += 1
                continue
            quotes.append(unit[i + 1:end])
            i = end + 1
            continue
        if ch == RIGHT_CURLY:
            free += 1
        i += 1
    return quotes, free


def report_quotes(text, min_chars):
    """([(row, quote)], [(line, row, count)]): the quotes of a report of min_chars characters or more, with a letter in them, and the
    lines that hold double marks which pair with no other (pair_marks). A quote lies in one line and in one table cell. Its row is the
    first cell of a table line, else the bold label that starts the line, else the line itself."""
    out, seen, unpaired = [], set(), []
    for n, line in enumerate(text.split("\n"), 1):
        if line.startswith("|"):
            m, cells = CELL_LABEL.match(line), line.split("|")
        else:
            m, cells = BOLD_LABEL.match(line), [line]
        row = (m.group(1).strip().rstrip(".,:") if m else "") or f"line {n}"
        count = 0
        for cell in cells:
            quotes, free = pair_marks(cell)
            count += free
            for quote in quotes:
                if len(quote) >= min_chars and any(ch.isalpha() for ch in quote) and (row, quote) not in seen:
                    seen.add((row, quote))
                    out.append((row, quote))
        if count:
            unpaired.append((n, row, count))
    return out, unpaired


def unpaired_note(n, row, count):
    """What the output says of a line with double marks that pair with no other: the line, and that no quote is read from it."""
    where = f"line {n}" if row == f"line {n}" else f"line {n} ({row})"
    return f"{where} has {count} unpaired double mark(s): no quote is read from {'it' if count == 1 else 'them'}"


def _rel(path, root):
    """The path as the project writes it: relative to the root when it lies under it."""
    p = pathlib.Path(path).resolve()
    try:
        return str(p.relative_to(pathlib.Path(root).resolve()))
    except ValueError:
        return str(p)


def bank_texts(cfg, notes):
    """([(where, text)], read): the texts of the bank's records that record find reads, and whether the bank could be read. A notice of
    the tool, or an old skill body, is no words of the principal's and is not read (record.demoted)."""
    path = cfg.path("bank")
    where = _rel(path, cfg.root)
    try:
        lines = path.read_text(encoding="utf-8").split("\n")
    except FileNotFoundError:
        notes.append(f"bank {where}: no such file; not read")
        return [], False
    except (OSError, UnicodeDecodeError) as e:
        notes.append(f"bank {where} cannot be read ({e}); not read")
        return [], False
    prefixes = record.principal_prefixes(cfg)
    texts = []
    for n, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        try:
            rec = json.loads(raw)
        except ValueError:
            notes.append(f"bank line {n} is not JSON; not read")
            continue
        text = rec.get("text") if isinstance(rec, dict) else None
        if not isinstance(text, str):
            notes.append(f"bank line {n} holds no text; not read")
            continue
        if record.demoted(rec, prefixes):
            continue
        tag = " [a /compact command]" if HANDOFF in text else ""
        texts.append((f"bank line {n}{tag}", text))
    return texts, True


def words_texts(cfg, skip, notes):
    """([(where, text)], [(file, quoted parts)]): the quoted parts of the lines of the words files, as record find reads them
    (record.quoted_parts), each part alone. A file in skip (the report, the table of --out) is no words file: a report quotes its own
    words."""
    pats = [cfg["words"]] if isinstance(cfg["words"], str) else list(cfg["words"])
    names, seen = [], set()
    for pat in pats:
        found = record.words_files(cfg.root, pat)
        if not found:
            notes.append(f"the words glob {pat!r} matches no file")
        for p in found:
            if p.resolve() not in seen:
                seen.add(p.resolve())
                names.append(p)
    texts, read = [], []
    for p in names:
        where = _rel(p, cfg.root)
        if p.resolve() in skip:
            notes.append(f"{where} is the report or the --out table: not a words file")
            continue
        try:
            lines = p.read_text(encoding="utf-8").split("\n")
        except (OSError, UnicodeDecodeError) as e:
            notes.append(f"{where} cannot be read ({e}); not read")
            continue
        parts = [(f"{where} line {n}", part) for n, line in enumerate(lines, 1)
                 for _, _, part in record.quoted_parts(line) if part.strip()]
        texts += parts
        read.append((where, len(parts)))
    return texts, read


def elsewhere_texts(names, skip, notes):
    """([(name, gate form, loose form)], [name]): the files named with --also that can be read. A file in skip is no source."""
    texts, read = [], []
    for name in names:
        p = pathlib.Path(name)
        if p.resolve() in skip:
            notes.append(f"--also {name} is the report or the --out table: not a source")
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            notes.append(f"--also {name} cannot be read ({e}); not read")
            continue
        texts.append((name, gate.N(text), lenient(text)))
        read.append(name)
    return texts, read


def classify(quote, owner, elsewhere):
    """(class, where): FOUND for the first text of the owner sources that holds the parts of the quote verbatim and in order; else
    LOOSE for the first that holds them in order once loosened; else ELSEWHERE for a file named with --also that holds them; else
    MISSING. The owner texts are (where, gate form, loose form), the same for elsewhere."""
    parts = segments(quote)
    gparts, lparts = [gate.N(p) for p in parts], [lenient(p) for p in parts]
    loose = None
    for where, gtext, ltext in owner:
        if in_order(gparts, gtext):
            return FOUND, where
        if loose is None and in_order(lparts, ltext):
            loose = where
    if loose is not None:
        return LOOSE, loose
    for where, gtext, ltext in elsewhere:
        if in_order(gparts, gtext) or in_order(lparts, ltext):
            return ELSEWHERE, where
    return MISSING, "-"


def _cut(text, n=CUT):
    """The text on one line, cut to n characters with an ellipsis."""
    t = " ".join(text.split())
    return t if len(t) <= n else t[: n - 3] + "..."


def table_text(summary, sources, not_read, rows):
    """The table --out writes: the summary, the sources, and one row per quote."""
    lines = ["# Quote check (record quotes)", "", summary, "", sources, not_read, "",
             "A MEASUREMENT: it says whether the words are there, not whether they answer a question. FOUND: verbatim, in order, inside "
             "one record of the bank or one quoted part of a words file. LOOSE: the same words only once case, dash, quote-mark and "
             "ellipsis differences are set aside. ELSEWHERE: only in a file named with --also. MISSING: nowhere.", "",
             "| row | class | quote (cut) | where |", "|---|---|---|---|"]
    lines += [f"| {row} | {cls} | {_cut(q, 90).replace('|', '/')} | {where} |" for cls, row, q, where in rows]
    return "\n".join(lines) + "\n"


def run(cfg, report, also, min_chars, out):
    """Prints the summary, one line per quote, and the sources read and not read; returns the exit code (see the docstring)."""
    if min_chars < 1:
        print("record quotes: --min is 1 or more characters; nothing was checked", file=sys.stderr)
        return 2
    report_path, out_path = pathlib.Path(report), (pathlib.Path(out) if out else None)
    if out_path is not None and out_path.resolve() == report_path.resolve():
        print("record quotes: --out is the report itself; nothing was written", file=sys.stderr)
        return 2
    try:
        text = report_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"record quotes: {report} cannot be read ({e}); nothing was checked", file=sys.stderr)
        return 3
    skip = {report_path.resolve()} | ({out_path.resolve()} if out_path is not None else set())
    notes = []
    btexts, bank_read = bank_texts(cfg, notes)
    wtexts, words_read = words_texts(cfg, skip, notes)
    if not bank_read and not words_read:
        print("record quotes: not evaluated: neither the bank nor a words file can be read; nothing was checked", file=sys.stderr)
        for note in notes:
            print(f"record quotes: {note}", file=sys.stderr)
        return 3
    extra, also_read = elsewhere_texts(also, skip, notes)
    owner = [(where, gate.N(t), lenient(t)) for where, t in btexts + wtexts]
    quoted, unpaired = report_quotes(text, min_chars)
    rows = []
    for row, quote in quoted:
        cls, where = classify(quote, owner, extra)
        rows.append((cls, row, quote, where))
    ok = bool(rows) and all(r[0] == FOUND for r in rows) and not unpaired
    count = {c: sum(1 for r in rows if r[0] == c) for c in CLASSES}
    summary = (f"record quotes: {report}: {len(rows)} quote(s) of {min_chars} or more characters: "
               + ", ".join(f"{c} {count[c]}" for c in CLASSES)
               + ("; every quote is FOUND" if ok else "; nothing was checked" if not rows else "")
               + (f"; {len(unpaired)} line(s) with an unpaired double mark" if unpaired else ""))
    read = [f"bank {_rel(cfg.path('bank'), cfg.root)} ({len(btexts)} record(s) searched)"] if bank_read else []
    read += [f"words {where} ({n} quoted part(s))" for where, n in words_read]
    read += [f"also {name}" for name in also_read]
    sources = "sources read: " + ("; ".join(read) if read else "none")
    not_read = "not read: transcripts (this verb reads none)" + "".join(f"; {note}" for note in notes)
    not_read += "".join(f"; {unpaired_note(n, row, k)}" for n, row, k in unpaired)
    print(summary)
    for cls, row, quote, where in rows:
        print(f"{cls:<10} {row} \"{_cut(quote)}\"" + (f"  [{where}]" if where != "-" else ""))
    print(sources)
    print(not_read)
    if out_path is not None:
        try:
            out_path.write_text(table_text(summary, sources, not_read, rows), encoding="utf-8")
        except OSError as e:
            print(f"record quotes: {out} cannot be written ({e})", file=sys.stderr)
            return 2
        print(f"written {out}")
    return 0 if ok else 1
