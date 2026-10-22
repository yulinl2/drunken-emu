---
id: precedence.lists-merge
kind: precedence
status: VERIFIED
title: "List keys merge"
sources: [S3]
---

# List keys merge

**Sources:** [S3](src.s3.md)

List keys such as permissions.allow merge across files. Exceptions: fallbackModel takes the whole value from the highest file that defines it; modelPicker takes the whole value from managed, --settings or user settings and ignores project and local files (v2.1.242 or later); availableModels applies the managed list as-is; modelSettings resolves per model together with effortLevel.

## Linked from

- [Precedence rule](precedence.rule.md)
