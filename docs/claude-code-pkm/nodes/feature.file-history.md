---
id: feature.file-history
kind: feature
status: VERIFIED
title: "file-history//"
sources: [S16]
---

# file-history//

**Sources:** [S16](src.s16.md)

contents: Pre-edit snapshots of files Claude changed, used for checkpoint restore. Holds snapshots for the 100 most recent checkpoints; snapshot files that no retained checkpoint references are deleted, except each file's first snapshot
