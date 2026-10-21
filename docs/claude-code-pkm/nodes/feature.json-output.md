---
id: feature.json-output
kind: feature
status: VERIFIED
title: "JSON output"
sources: [S52]
---

# JSON output

**Sources:** [S52](src.s52.md)

With `--json`, Claude Code prints an array with one object per installation. Each object carries the fields below. `id`, `version`, `scope`, `enabled`, and `installPath` are always present, and the others appear only when they apply.
