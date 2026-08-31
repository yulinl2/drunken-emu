#!/usr/bin/env bash
# apply_doi.sh — write a minted Zenodo DOI into README.md and CITATION.cff.
# Idempotent: re-running with a different DOI replaces, never duplicates.
# Usage: bin/apply_doi.sh 10.5281/zenodo.1234567
set -eu
DOI="${1:?usage: apply_doi.sh 10.5281/zenodo.NNNNNNN}"
case "$DOI" in 10.5281/zenodo.[0-9]*) ;; *) echo "not a Zenodo DOI: $DOI" >&2; exit 2;; esac
R="$(cd "$(dirname "$0")/.." && pwd)"

python3 - "$R" "$DOI" <<'PY'
import re, sys, pathlib
root, doi = pathlib.Path(sys.argv[1]), sys.argv[2]
badge = f"[![DOI](https://zenodo.org/badge/DOI/{doi}.svg)](https://doi.org/{doi})"

rm = root / "README.md"; t = rm.read_text()
t = re.sub(r"\n\[!\[DOI\]\(https://zenodo\.org/badge/DOI/[^\n]*\n", "\n", t)  # drop old
anchor = re.search(r"^\[!\[README claims\][^\n]*$", t, re.M)
if not anchor:
    raise SystemExit("README.md: CI badge anchor not found; refusing to guess")
t = t[:anchor.end()] + "\n" + badge + t[anchor.end():]
rm.write_text(t)

cf = root / "CITATION.cff"; c = cf.read_text()
c = re.sub(r"\nidentifiers:\n(?:  [^\n]*\n)+", "\n", c)                       # drop old
block = f"identifiers:\n  - type: doi\n    value: {doi}\n    description: Concept DOI, always resolves to the latest version\n"
m = re.search(r"^repository-code:[^\n]*\n", c, re.M)
if not m:
    raise SystemExit("CITATION.cff: repository-code anchor not found; refusing to guess")
c = c[:m.end()] + block + c[m.end():]
cf.write_text(c)
print(f"applied {doi} to README.md and CITATION.cff")
PY
