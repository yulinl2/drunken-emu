---
id: feature.a-git-command-fails-with-unable-to-unlink-old
kind: feature
status: VERIFIED
title: "A git command fails with unable to unlink old"
sources: [S68]
---

# A git command fails with unable to unlink old

**Sources:** [S68](src.s68.md)

`git merge`, `git checkout`, and similar commands fail with `unable to unlink old` when they need to replace a file the sandbox denies writes to. On Linux and WSL2 the error ends with `Read-only file system`. The file can be in one of these places:
