#!/usr/bin/env python3
"""validate.py — the transcription must stay anchored to the narration. Stdlib only.

Checks: the narration's sha256 matches README; ids are unique; every parent exists; every `quote` and every stated
property is a verbatim substring of the narration; every `line` is the line that contains the quote.
Exit 1 on any failure."""
import hashlib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
narr = (HERE / "narration.zh.txt").read_text(encoding="utf-8")
lines = narr.split("\n")
fail = []
want = re.search(r"sha256 `([0-9a-f]{64})`", (HERE / "README.md").read_text(encoding="utf-8"))
got = hashlib.sha256((HERE / "narration.zh.txt").read_bytes()).hexdigest()
if not want or want.group(1) != got: fail.append(f"narration sha256 {got} does not match README")
steps = [json.loads(l) for l in (HERE / "transcription.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
ids = [s["id"] for s in steps]
if len(ids) != len(set(ids)): fail.append("duplicate ids")
for s in steps:
    if s.get("parent") and s["parent"] not in ids: fail.append(f"{s['id']}: parent {s['parent']} missing")
    q = s.get("quote")
    if q:
        if q not in narr: fail.append(f"{s['id']}: quote not verbatim")
        elif s.get("line") and q not in lines[s["line"] - 1]: fail.append(f"{s['id']}: quote not on line {s['line']}")
    for k, vs in (s.get("stated") or {}).items():
        for v in vs:
            if v not in narr: fail.append(f"{s['id']}: stated {k} not verbatim")
print(f"{len(steps)} entries, {sum(1 for s in steps if s.get('stated'))} with stated properties, "
      f"{sum(1 for s in steps if s.get('inferred'))} with inferred, {len(fail)} failures")
for f in fail: print("FAIL", f)
sys.exit(1 if fail else 0)
