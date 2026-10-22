---
id: mod.fs
kind: mod
status: VERIFIED
title: "$.fs"
sources: [S54]
---

# $.fs

**Sources:** [S54](src.s54.md)

methods: `read`, `write`, `list`, `exists`, `stat`, `ancestors`. `write` isn't atomic: it replaces the file's content in place, so another process can read a partly written file. Keep data that several sessions change in `$.store`.
