---
id: feature.json-result-format
kind: feature
status: VERIFIED
title: "JSON result format"
sources: [S52]
---

# JSON result format

**Sources:** [S52](src.s52.md)

When you pass `--json` to `plugin install`, the last line of stdout is one JSON object. Parse only that line, because Claude Code prints any command the marketplace declares ahead of it.
