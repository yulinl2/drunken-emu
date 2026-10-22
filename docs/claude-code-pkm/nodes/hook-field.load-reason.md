---
id: hook-field.load-reason
kind: hook-field
status: VERIFIED
title: "load_reason"
sources: [S85]
---

# load_reason

**Sources:** [S85](src.s85.md)

Why the file was loaded: `"session_start"`, `"nested_traversal"`, `"path_glob_match"`, `"include"`, or `"compact"`. The `"compact"` value fires when instruction files are re-loaded after a compaction event
