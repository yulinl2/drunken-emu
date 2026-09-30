#!/usr/bin/env python3
"""fact_check — re-derive a document's own claims about files against the files themselves.

Why this reader exists. Two failures in this project came from a document stating a number
that was true when it was written and false afterwards, with nothing that could notice:
obs 136 (a dossier's sizes were written from impression and were wrong by a wide margin) and
COR-0053 (a label was written as a date eleven times). Both are the same shape — a document
carries a *derived* quantity as prose, the source of that quantity is on disk, and the two are
never compared. This reader compares them.

What it checks. On any line of a markdown file that mentions exactly one resolvable file path,
every quantity of the following kinds is recomputed from that file and diffed:

  md5 <hex>        an md5 or md5 prefix (8-32 hex chars), compared prefix-wise
  N bytes / N B    file size (a number glued to an identifier, as in Qwen2.5-7B, is not a claim)
  N lines          newline count
  N H2 / N H3      count of lines starting with '## ' / '### '
  N links          count of '](http' occurrences
  N words          words by the same regex reader_load.py and load_ledger.py use, so the
                   numbers in LOADS.md and in prose are commensurable

Attribution rule, and why it is narrow. In the first run over this packet the naive rule — one
path on the line owns every number on the line — produced 19 flags of which 3 were real. The
losing cases were all comparisons ("the file has 133 links; the recorded profile of the other
edition is 143") and lines that name one file while quoting another file's checksum. So a claim
is now attributed only when it lies within --near characters (default 90) of the path token,
and a number fused to an identifier is not read as a claim at all.

Separately, every backticked token that looks like a path is resolved, and the outcome is one
of three: it exists; it is AMBIGUOUS (the basename occurs at several places in the tree, all of
which are listed — three ledgers named needs.tsv live here); or it is MISSING. Ambiguity is
information, not an error: a pointer that resolves to two files is exactly the duplication the
seed's step zero asks an instance to reconcile.

Deliberately NOT a gate. It reports; a stale number is not always an error (a document may be
quoting a historical measurement on purpose, and several here do). The verdict belongs to a
reader, so every line says both numbers and names the file.

Usage:
  python3 fact_check.py FILE.md [FILE2.md ...]   # report
  python3 fact_check.py --selftest               # planted-violation control
  python3 fact_check.py --json FILE.md           # machine-readable
Exit code is 0 unless --strict is given, in which case any MISMATCH exits 1.
"""
import re, sys, os, json, hashlib

NEAR = [90]        # attribution window in characters, measured forward from the path token; --near N to change
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]+|[\u4e00-\u9fff]{1,4}")   # same as reader_load.py / load_ledger.py
PATH_RE = re.compile(r"`([^`\s]+\.(?:md|tsv|py|sh|json|txt|patch|bundle|tex|jsx|html))`")
NUM = r"(?<![0-9A-Za-z.\-])([0-9][0-9,]*)"   # not fused to an identifier: Qwen2.5-7B is not "7 bytes"
CLAIMS = [
    ("bytes", re.compile(NUM + r"\s*(?:B\b|bytes\b)")),
    ("lines", re.compile(NUM + r"\s*lines\b")),
    ("h2",    re.compile(NUM + r"\s*H2\b")),
    ("h3",    re.compile(NUM + r"\s*H3\b")),
    ("links", re.compile(NUM + r"\s*links\b")),
    ("words", re.compile(NUM + r"\s*words\b")),
]
MD5_RE = re.compile(r"md5\s*`?([0-9a-f]{8,32})`?", re.I)
SKIP_LINE = re.compile(r"^\s*(?:>?\s*)?(?:\||#)?\s*(?:python3|bash|git|curl)\s", re.I)
# A document may name a file exactly in order to say it is absent — "PROMPT.md never existed in this
# history", "retrieve X from the session below". That is a true sentence, not a dangling pointer, so the
# same line saying so downgrades MISSING to NOTED-ABSENT. Measured: this alone accounts for the two
# PROMPT.md reports in MANIFEST.md and ANSWER-DRAFT.md.
ABSENT_RE = re.compile(r"never existed|does not exist|do not exist|not exist|is absent|are absent|no longer|"
                       r"retrieve|download|not on disk|not here|not in this|unretrievable|missing|lost|"
                       r"未retrieve|不存在|缺失|待取回", re.I)


def roots(doc):
    """Where a path in this document might live, nearest first."""
    d = os.path.dirname(os.path.abspath(doc))
    out = [d]
    p = d
    for _ in range(4):                      # walk up to the packet root and the outputs root
        p = os.path.dirname(p)
        if p and p not in out:
            out.append(p)
    return out


def resolve(token, doc, index):
    """-> (path, status): status is 'exact', 'basename', 'ambiguous' or 'missing'."""
    for r in roots(doc):
        cand = os.path.normpath(os.path.join(r, token))
        if os.path.isfile(cand):
            return cand, "exact"
    hits = index.get(os.path.basename(token), [])
    if len(hits) == 1:
        return hits[0], "basename"
    if len(hits) > 1:
        return hits, "ambiguous"
    return None, "missing"


def build_index(root):
    idx = {}
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
        for fn in files:
            idx.setdefault(fn, []).append(os.path.join(dirpath, fn))
    return idx


def measure(path):
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", "replace")
    return {
        "bytes": len(raw),
        "lines": text.count("\n"),
        "h2": sum(1 for l in text.split("\n") if l.startswith("## ")),
        "h3": sum(1 for l in text.split("\n") if l.startswith("### ")),
        "links": text.count("](http"),
        "words": len(WORD_RE.findall(text)),
        "md5": hashlib.md5(raw).hexdigest(),
    }


def check(doc, index, cache):
    """Yield (status, kind, line_no, message) for one document."""
    out = []
    for n, line in enumerate(open(doc, encoding="utf-8", errors="replace").read().split("\n"), 1):
        if SKIP_LINE.match(line):
            continue
        resolved = []
        for m0 in PATH_RE.finditer(line):
            t = m0.group(1)
            r, status = resolve(t, doc, index)
            if status in ("exact", "basename"):
                resolved.append((t, r, m0.start(), m0.end()))
            elif status == "ambiguous":
                out.append(("AMBIGUOUS", "path", n, f"`{t}` matches {len(r)} files in the tree, so a claim about it "
                                                    f"cannot be attributed: {', '.join(os.path.relpath(x) for x in r[:4])}"))
            else:
                status_word = "NOTED-ABSENT" if ABSENT_RE.search(line) else "MISSING"
                out.append((status_word, "path", n, f"`{t}` resolves to nothing from {os.path.basename(doc)} "
                                                  f"(not relative to the document, the packet root or the outputs root, "
                                                  f"and no file of that basename anywhere in the tree)"))
        if len(resolved) != 1:
            continue                      # a number on a line with two files, or none, cannot be attributed
        tok, path, tstart, tend = resolved[0]
        if path not in cache:
            cache[path] = measure(path)
        m = cache[path]
        def near(hit):
            """A claim belongs to the file named BEFORE it, within the window. Measured on this packet:
            the naive rule (one path owns the whole line) gave 19 flags of which 3 were real; adding a
            90-character window gave 5; requiring the claim to follow the path gives 3, all real. The two
            it drops are a checksum quoted about another file earlier in the same bullet, and a size in
            parentheses attached to a different noun phrase."""
            return 0 <= hit.start() - tend <= NEAR[0]
        for kind, rx in CLAIMS:
            for hit in rx.finditer(line):
                if not near(hit):
                    out.append(("SKIPPED", kind, n, f"{hit.group(1)} {kind} sits {hit.start()-tend:+d} characters from `{tok}` "
                                                    f"— outside the forward attribution window, not checked"))
                    continue
                stated = int(hit.group(1).replace(",", ""))
                actual = m[kind]
                if stated == actual:
                    out.append(("OK", kind, n, f"`{tok}` {kind}={stated:,}"))
                else:
                    out.append(("MISMATCH", kind, n,
                                f"`{tok}` states {kind}={stated:,} — the file has {actual:,} "
                                f"(difference {actual - stated:+,})"))
        for hit in MD5_RE.finditer(line):
            if not near(hit):
                out.append(("SKIPPED", "md5", n, f"an md5 sits {hit.start()-tend:+d} characters from `{tok}` "
                                                 f"— outside the forward attribution window, not checked"))
                continue
            stated = hit.group(1).lower()
            actual = m["md5"]
            if actual.startswith(stated):
                out.append(("OK", "md5", n, f"`{tok}` md5 prefix {stated}"))
            else:
                out.append(("MISMATCH", "md5", n,
                            f"`{tok}` states md5 {stated} — the file hashes to {actual[:len(stated)]} "
                            f"(full {actual})"))
    return out


def report(docs, root, as_json=False, strict=False):
    index = build_index(root)
    cache = {}
    allrows, worst = [], 0
    for doc in docs:
        if not os.path.isfile(doc):
            print(f"SKIP  {doc}: not a file")
            continue
        rows = check(doc, index, cache)
        allrows.append((doc, rows))
        if as_json:
            continue
        ok = sum(1 for s, *_ in rows if s == "OK")
        mis = [r for r in rows if r[0] == "MISMATCH"]
        amb = [r for r in rows if r[0] == "AMBIGUOUS"]
        mss = [r for r in rows if r[0] == "MISSING"]
        nab = [r for r in rows if r[0] == "NOTED-ABSENT"]
        skp = [r for r in rows if r[0] == "SKIPPED"]
        print(f"{os.path.basename(doc):52s} {ok:3d} verified  {len(mis):2d} MISMATCH  {len(amb):2d} ambiguous  "
              f"{len(mss):2d} missing  {len(nab):2d} noted-absent  {len(skp):2d} out-of-window")
        for s, kind, n, msg in mis + amb + mss:
            print(f"    {s:10s} line {n:<5d} {msg}")
        worst = max(worst, len(mis))
    if as_json:
        print(json.dumps({d: [{"status": s, "kind": k, "line": n, "message": m} for s, k, n, m in rows]
                          for d, rows in allrows}, indent=1, ensure_ascii=False))
    return 1 if (strict and worst) else 0


def selftest():
    """Plant one violation of every family and confirm each is caught."""
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    try:
        target = os.path.join(tmp, "target.md")
        open(target, "w", encoding="utf-8").write("# T\n\n## A\n\n### a1\n\n[x](https://example.com)\n\nword word\n")
        m = measure(target)
        doc = os.path.join(tmp, "doc.md")
        open(doc, "w", encoding="utf-8").write(
            f"`target.md` is {m['bytes']} B and hashes to md5 `{m['md5'][:8]}` — both correct\n"
            f"`target.md` has 99 H2 and 98 H3 and 97 links and 96 words and 95 lines and 94 bytes\n"
            f"`target.md` was run on Qwen2.5-7B, which is not a size claim\n"
            f"`target.md` md5 `deadbeef`\n"
            f"see `no-such-file.md` for the rest\n")
        rows = check(doc, build_index(tmp), {})
        fired = {k for s, k, _, _ in rows if s in ("MISMATCH", "MISSING", "AMBIGUOUS", "NOTED-ABSENT")}
        okk = {k for s, k, _, _ in rows if s == "OK"}
        expected = {"bytes", "lines", "h2", "h3", "links", "words", "md5", "path"}
        missing = expected - fired
        for s, k, n, msg in rows:
            if s != "OK":
                print(f"{s:10s} {k:6s} line {n}  {msg}")
        print(f"selftest: {len(expected)} planted families, {len(expected - missing)} fired, "
              f"{len(missing)} silent {sorted(missing) if missing else ''}; "
              f"correct claims not flagged: {sorted(okk)}")
        return 1 if missing else 0
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    for i, a in enumerate(args):
        if a == "--near" and i + 1 < len(args):
            NEAR[0] = int(args[i + 1]); args[i + 1] = "--"
    if "--selftest" in args:
        sys.exit(selftest())
    as_json = "--json" in args
    strict = "--strict" in args
    docs = [a for a in args if not a.startswith("--")]
    if not docs:
        print(__doc__.strip().split("Usage:")[-1])
        sys.exit(0)
    root = os.environ.get("FACT_CHECK_ROOT", os.environ.get("EMU_ROOT", os.getcwd()))
    sys.exit(report(docs, root, as_json, strict))
