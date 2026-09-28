#!/usr/bin/env python3
"""bin/gen_ledger.py — every figure the bank and its consumers have produced, in one place.

Why this exists: the bank now has multiple consumers (MetaProof, and soon MetaSci, HAN), each
appending its own `figures/verdicts.jsonl` as the maker-cold-reader pipeline (bin/figpipe) runs.
There was no single place — human or agent — could look to see the whole bank's output: which
figure ids exist, which repo owns each, whether its most recent round was accepted, what a blind
reader actually said. This reads every reachable verdicts.jsonl (this repo's own
figbank/examples/, plus best-effort sibling clones next to it) and writes two views of the same
aggregation: figbank/ledger.json (machine-readable, for an agent to `jq` or load) and
figbank/LEDGER.md (human-readable, one row per figure id, its latest verdict).

Unlike docs/TREE.md (bin/gen_tree.py), this is NOT CI-gated: TREE.md is deterministic from this
repo's own git state alone, but the ledger's sibling rows depend on repos this container may or
may not have cloned next to it, so staleness here is expected, not a bug — `--check` only asserts
this repo's own rows and internal MD/JSON agreement, never fails for an absent sibling clone.

  python3 bin/gen_ledger.py             # print a summary
  python3 bin/gen_ledger.py --write     # regenerate figbank/LEDGER.md + figbank/ledger.json
  python3 bin/gen_ledger.py --check     # exit 1 if the committed files disagree with this repo's own rows
"""
import json
import os
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.dirname(ROOT)
MD = os.path.join(ROOT, "figbank", "LEDGER.md")
JSON_OUT = os.path.join(ROOT, "figbank", "ledger.json")

# repo label -> its verdicts.jsonl. "drunken-emu" is always present (this repo); the rest are
# best-effort sibling clones, exactly like bin/kb_check.py's --kb pattern in MetaProof: read if
# present, skip (not fail) if not.
SOURCES = [
    ("drunken-emu", os.path.join(ROOT, "figbank", "examples", "verdicts.jsonl")),
    ("MetaProof", os.path.join(HOME, "metaproof", "figures", "verdicts.jsonl")),
    ("MetaSci", os.path.join(HOME, "MetaSci", "figures", "verdicts.jsonl")),
    ("HAN", os.path.join(HOME, "HAN", "figures", "verdicts.jsonl")),
]


def load_rows(path):
    if not os.path.isfile(path):
        return None
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def verdict_of(row):
    reader = row.get("reader")
    if isinstance(reader, dict):
        v = (reader.get("report") or {}).get("verdict")
        if v:
            return v
    return None


def status_of(row):
    a = row.get("accepted")
    if a is True:
        return "accepted"
    if a is False:
        return "rejected"
    return "unverified"  # no round of this id has ever had a reader run


def build():
    """Returns (entries, missing_repos). entries: one dict per figure id, latest round only,
    across all reachable sources. missing_repos: repo labels whose verdicts.jsonl this container
    could not find (no sibling clone here right now) — reported, never hidden."""
    entries = []
    missing = []
    for repo, path in SOURCES:
        rows = load_rows(path)
        if rows is None:
            missing.append(repo)
            continue
        latest = OrderedDict()
        last_verified = {}
        attempts = {}
        for r in rows:
            rid = r["id"]
            attempts[rid] = attempts.get(rid, 0) + 1
            latest[rid] = r  # jsonl is append-only: later lines are later rounds, last one wins
            if r.get("accepted") is not None:
                last_verified[rid] = r  # the most recent round a reader actually ran on, if any
        for fid, row in latest.items():
            raster = row.get("raster") if isinstance(row.get("raster"), dict) else {}
            verified = last_verified.get(fid)
            # a spec/render can change (e.g. re-run after upstream data grew) without a reader
            # re-running on it; show that round's own status, but never hide an *earlier* real
            # verdict behind a silent "unverified" — and flag when the two have drifted apart.
            status_row = verified if verified is not None else row
            entries.append({
                "repo": repo,
                "id": fid,
                "status": status_of(status_row),
                "verdict": verdict_of(status_row),
                "verified_round": status_row.get("round"),
                "verified_ts": status_row.get("ts"),
                "stale": verified is not None and verified is not row,
                "round": row.get("round"),
                "attempts": attempts[fid],
                "ts": row.get("ts"),
                "spec": row.get("spec"),
                "png": raster.get("png"),
                "message": row.get("message") or row.get("note"),
            })
    entries.sort(key=lambda e: (e["repo"], e["id"]))
    return entries, missing


def render_md(entries, missing):
    lines = [
        "# LEDGER — every figure the bank has produced",
        "",
        "Generated by `bin/gen_ledger.py --write` from every reachable `verdicts.jsonl`",
        "(this repo's own `figbank/examples/`, plus sibling clones of every consumer repo",
        "next to this one). One row per figure id: its most recent pipeline round only —",
        "earlier rounds of the same id are in that repo's own `verdicts.jsonl` history.",
        "Not CI-gated (see the module docstring in `bin/gen_ledger.py`): regenerate on demand.",
        "",
    ]
    if missing:
        lines.append(
            f"*Not read this run (no sibling clone present in this container): {', '.join(missing)}.*"
        )
        lines.append("")
    if not entries:
        lines.append("*(no verdicts found)*")
        lines.append("")
        return "\n".join(lines)
    n_accepted = sum(1 for e in entries if e["status"] == "accepted")
    lines.append(f"**{n_accepted}/{len(entries)} accepted**, across {len({e['repo'] for e in entries})} repo(s).")
    lines.append("")
    lines.append("| repo | id | status | reader verdict | verified round | current round | attempts | message |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for e in entries:
        msg = (e["message"] or "").replace("|", "\\|").replace("\n", " ")
        status = e["status"] + (" (stale)" if e["stale"] else "")
        lines.append(
            f"| {e['repo']} | {e['id']} | {status} | {e['verdict'] or '—'} "
            f"| {e['verified_round'] if e['verified_round'] is not None else '—'} "
            f"| {e['round'] if e['round'] is not None else '—'} | {e['attempts']} | {msg} |"
        )
    lines.append("")
    lines.append(
        "`status (stale)` means the id's spec/render changed in a later round than the one a "
        "reader last verified — the verdict above is real but may no longer describe the current "
        "figure; re-run it through `bin/figpipe ... --reader auto` to confirm."
    )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    entries, missing = build()
    if "--check" in sys.argv:
        own = [e for e in entries if e["repo"] == "drunken-emu"]
        if not os.path.isfile(JSON_OUT):
            print("FAIL ledger: figbank/ledger.json does not exist — run bin/gen_ledger.py --write")
            sys.exit(1)
        committed = json.loads(open(JSON_OUT, encoding="utf-8").read())
        committed_own = [e for e in committed["entries"] if e["repo"] == "drunken-emu"]
        if committed_own != own:
            print("FAIL ledger: figbank/ledger.json's drunken-emu rows disagree with this repo's own verdicts.jsonl")
            print("  regenerate with: python3 bin/gen_ledger.py --write")
            sys.exit(1)
        if render_md(committed["entries"], committed["missing"]) != open(MD, encoding="utf-8").read():
            print("FAIL ledger: figbank/LEDGER.md does not match figbank/ledger.json")
            print("  regenerate with: python3 bin/gen_ledger.py --write")
            sys.exit(1)
        print(f"PASS  ledger  figbank/ledger.json + LEDGER.md agree with this repo's own {len(own)} row(s)")
        sys.exit(0)
    if "--write" in sys.argv:
        os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
        with open(JSON_OUT, "w", encoding="utf-8") as f:
            json.dump({"entries": entries, "missing": missing}, f, ensure_ascii=False, indent=1)
            f.write("\n")
        with open(MD, "w", encoding="utf-8") as f:
            f.write(render_md(entries, missing))
        print(f"wrote figbank/LEDGER.md + figbank/ledger.json ({len(entries)} figures, {len(missing)} repo(s) unreachable)")
        sys.exit(0)
    n_accepted = sum(1 for e in entries if e["status"] == "accepted")
    print(f"{n_accepted}/{len(entries)} accepted, {len(missing)} repo(s) unreachable: {', '.join(missing) or 'none'}")
