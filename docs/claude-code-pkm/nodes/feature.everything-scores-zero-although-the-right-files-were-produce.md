---
id: feature.everything-scores-zero-although-the-right-files-were-produce
kind: feature
status: VERIFIED
title: "Everything scores zero although the right files were produced"
sources: [S47]
---

# Everything scores zero although the right files were produced

**Sources:** [S47](src.s47.md)

Your graders target `files`, the list of created paths, when you meant the file's contents. Use `{ source: file, path: }` as the `target` or `focus`.
