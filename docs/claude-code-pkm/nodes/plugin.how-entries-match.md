---
id: plugin.how-entries-match
kind: plugin
status: VERIFIED
title: "How entries match"
sources: [S59]
---

# How entries match

**Sources:** [S59](src.s59.md)

A `url` entry matches on its `url` value; `headers` aren't compared. For `github` and `git` entries, the `repo` or `url`, the `ref`, and the `path` must all match, or be absent on both sides:
