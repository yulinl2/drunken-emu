---
id: feature.json-result
kind: feature
status: VERIFIED
title: "JSON result"
sources: [S47]
---

# JSON result

**Sources:** [S47](src.s47.md)

`aggregate-result.json`, and `--json` output, is a versioned document with `schemaVersion: 1` for CI scripts to parse. Field names are camelCase and new fields are added without renaming existing ones, so write your script to ignore fields it doesn't recognize.
