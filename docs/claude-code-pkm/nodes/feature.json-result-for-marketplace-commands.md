---
id: feature.json-result-for-marketplace-commands
kind: feature
status: VERIFIED
title: "JSON result for marketplace commands"
sources: [S52]
---

# JSON result for marketplace commands

**Sources:** [S52](src.s52.md)

On `plugin marketplace add`, `plugin marketplace remove`, and `plugin marketplace update`, `--json` prints one JSON object on the last line of stdout with `command`, `outcome`, and `message` fields. The following is the result of `claude plugin marketplace remove your-marketplace --json`:
