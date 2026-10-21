---
id: feature.basic-usage
kind: feature
status: VERIFIED
title: "Basic usage"
sources: [S38]
---

# Basic usage

**Sources:** [S38](src.s38.md)

Add the `-p` (or `--print`) flag to any `claude` command to run it non-interactively. Not every CLI option combines with `-p`. Claude Code rejects `--bg`, and rejects `--cloud` with a task description, with an error naming the conflict; `--cloud` with a session ID and `-p` instead queues a message into that cloud session and exits. Options you'll combine with `-p` often include:
