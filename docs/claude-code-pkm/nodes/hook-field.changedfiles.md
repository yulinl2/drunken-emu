---
id: hook-field.changedfiles
kind: hook-field
status: VERIFIED
title: "changedFiles"
sources: [S85]
---

# changedFiles

**Sources:** [S85](src.s85.md)

Absolute paths of the files the command changed, at most 200. Present whenever `files` holds a diff or `moreFiles` is above zero (type: array; example: `["/path/to/src/app.ts"]`)
