---
id: feature.json-output-path-must-end-in-json
kind: feature
status: VERIFIED
title: "--json output path must end in .json"
sources: [S47]
---

# --json output path must end in .json

**Sources:** [S47](src.s47.md)

You put the target after `--json`, so it was read as the output path. Put the target first, as in `claude plugin eval . --json`, or give `--json` an explicit `.json` path.
