#!/usr/bin/env python3
"""checks/chain_check.py -- the CLI behind `bin/emu chain check`.  Stdlib only; no browser, no server, no model.

    bin/emu chain check CHAIN.json [CHAIN2.json ...] [--budget B] [--json] [--chain ID ...] [--lookalike X]

For every chain in every file: the load (components and one number), the working-memory verdict, and the findings
of the ten verifiers (checks/chain_verifiers.py), each with its step number.

Exit code
  0   no findings in any chain checked
  1   at least one finding
  2   a file is not a valid chain (the problems are listed, each naming its step), the usage is wrong, or the
      checker itself crashed (a bug in the checker is never reported as a finding: exit 1 means findings only)

A file may hold several chains (hw1_correction_pass.json holds two): the exit code is 1 if ANY of them has a
finding.  `--chain ID` checks only the named chains, wherever they are: an id is unknown only when NO input file
has it, and a file with none of the named chains is skipped.  `--budget B` overrides every chain's own budget
(default 3).
`--json` prints one JSON document on stdout instead of the report.

The report shows each step's free-text `target` next to a finding so a human can find the step.  That text is
looked up here, AFTER the verifiers ran on the blind chain; no verifier ever sees it.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chain as C                      # noqa: E402
import chain_load as L                 # noqa: E402
import chain_verifiers as V            # noqa: E402


def _positive(s: str) -> int:
    try:
        v = int(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{s!r} is not a whole number") from None
    if v < 1:
        raise argparse.ArgumentTypeError("the budget is a number of slots and must be >= 1")
    return v


def _unit(s: str) -> float:
    try:
        v = float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{s!r} is not a number") from None
    if not 0 <= v <= 1:
        raise argparse.ArgumentTypeError("similarity is between 0 and 1")
    return v


def _report(path: str, doc: dict, results: list[dict]) -> list[str]:
    lines = [path]
    by_id = {c["id"]: c for c in doc["chains"]}
    for r in results:
        c, ld = by_id[r["id"]], r["load"]
        prov = c["provenance"]
        task = c["text"].get("task") or ""
        lines.append(f"  {r['id']}" + (f"  {task}" if task else "") + f"  [{prov['source']} {prov['date']}]")
        lines.append(f"    {ld['steps']} steps · B {r['budget']} · peak {ld['peak_slots']} slot(s) "
                     f"(held {ld['peak_held']}) · RELOAD {ld['counts']['reloads']} · "
                     f"RE-ORIENT {ld['counts']['reorients']}")
        lines.append(f"    load {ld['load']:.2f} = {L.summary_line(ld)}")
        if not r["findings"]:
            lines.append("    no findings")
            continue
        lines.append(f"    {len(r['findings'])} finding(s)")
        for f in r["findings"]:
            step = c["steps"][f["step"] - 1]
            tgt = step["text"]["target"]
            if len(tgt) > 60:
                tgt = tgt[:57] + "..."
            lines.append(f"      step {f['step']:<3} {step['op']:<12} {f['verifier']:<18} {f['message']}"
                         + (f"  [{tgt}]" if tgt else ""))
    return lines


def _json_chain(r: dict) -> dict:
    ld = r["load"]
    return {"id": r["id"], "budget": r["budget"], "steps": ld["steps"], "peak_slots": ld["peak_slots"],
            "peak_held": ld["peak_held"], "over_budget_steps": ld["over_budget_steps"], "counts": ld["counts"],
            "terms": ld["terms"], "load": ld["load"], "findings": r["findings"], "ok": not r["findings"]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="bin/emu chain", description="Check recorded operation chains "
                                 "(docs/OPERATION-CHAINS.md). Exit 0 clean, 1 findings, 2 invalid file.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ck = sub.add_parser("check", help="load, validate and run the ten verifiers on chain files")
    ck.add_argument("files", nargs="+", metavar="CHAIN.json")
    ck.add_argument("--budget", type=_positive, default=None, help="working-memory slots B (default: the chain's own, else 3)")
    ck.add_argument("--json", action="store_true", help="print one JSON document instead of the report")
    ck.add_argument("--chain", action="append", default=None, metavar="ID", help="only this chain id, in whichever file has it (repeatable)")
    ck.add_argument("--lookalike", type=_unit, default=V.LOOKALIKE,
                    help=f"similarity at or above which confusables are look-alikes (default {V.LOOKALIKE})")
    args = ap.parse_args(argv)

    docs = []                                                  # every file is read and validated before anything is checked
    for path in args.files:
        try:
            docs.append((path, C.load(path)))
        except C.ChainError as e:
            if args.json:
                print(json.dumps({"ok": False, "error": {"file": path, "problems": e.problems}}, indent=2))
            else:
                print(f"FAIL chain-format: {e}", file=sys.stderr)
            return 2
    # --chain names chains across ALL the files: an id is unknown only when no file has it.  A file with none of the
    # named chains is skipped, so `--chain cheap a.json b.json` checks `cheap` wherever it is.
    known = {c["id"] for _, d in docs for c in d["chains"]}
    unknown = [i for i in (args.chain or []) if i not in known]
    if unknown:
        msg = (f"no chain with id {', '.join(map(repr, unknown))} in any file; "
               + "; ".join(f"{p} has: {', '.join(c['id'] for c in d['chains'])}" for p, d in docs))
        if args.json:
            print(json.dumps({"ok": False, "error": {"file": None, "problems": [msg]}}, indent=2))
        else:
            print(f"FAIL chain-select: {msg}", file=sys.stderr)
        return 2
    files, total, out_lines = [], 0, []
    for path, doc in docs:
        chains = [c for c in doc["chains"] if not args.chain or c["id"] in args.chain]
        if not chains:
            continue
        results = [V.run_chain(c, args.budget, args.lookalike) for c in chains]
        total += sum(len(r["findings"]) for r in results)
        files.append({"file": path, "chains": [_json_chain(r) for r in results]})
        out_lines += _report(path, {"chains": chains}, results)
    failed = total > 0
    if args.json:
        print(json.dumps({"ok": not failed, "findings": total, "files": files}, indent=2))
    else:
        print("\n".join(out_lines))
        print(f"\n{'FAIL' if failed else 'PASS'}  {total} finding(s) in {sum(len(f['chains']) for f in files)} chain(s)")
    return 1 if failed else 0


def cli(argv: list[str] | None = None) -> int:
    """main(), except that a crash is exit 2 with the traceback on stderr: Python's own exit code for an uncaught
    exception is 1, which here means "findings", and a broken checker must not read as a failed chain."""
    try:
        return main(argv)
    except Exception:                                          # argparse's SystemExit passes through untouched
        import traceback
        traceback.print_exc()
        print("FAIL chain-internal: the checker crashed. This is a bug in the checker, not a finding of the chain.",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(cli())
