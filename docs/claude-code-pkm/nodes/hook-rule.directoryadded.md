---
id: hook-rule.directoryadded
kind: hook-rule
status: VERIFIED
title: "DirectoryAdded"
sources: [S85]
---

# DirectoryAdded

**Sources:** [S85](src.s85.md)

Runs after you add a working directory mid-session with the `/add-dir` command, or after an SDK client adds one with the `register_repo_root` control request. Use this to prepare a newly added repository, for example by installing its dependencies.
