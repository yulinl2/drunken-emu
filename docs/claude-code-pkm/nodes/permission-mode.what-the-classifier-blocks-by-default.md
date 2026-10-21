---
id: permission-mode.what-the-classifier-blocks-by-default
kind: permission-mode
status: VERIFIED
title: "What the classifier blocks by default"
sources: [S67]
---

# What the classifier blocks by default

**Sources:** [S67](src.s67.md)

The classifier trusts your working directory and the remotes that were configured for it when the session started. A remote added or repointed during the session with `git remote add` or `git remote set-url` isn't trusted, and everything else is treated as external until you configure trusted infrastructure.
