---
id: feature.if-the-working-directory-is-deleted
kind: feature
status: VERIFIED
title: "If the working directory is deleted"
sources: [S38]
---

# If the working directory is deleted

**Sources:** [S38](src.s38.md)

If the working directory of a `claude -p` or Agent SDK session is deleted mid-session, the session keeps running. When a turn starts while the directory is missing, Claude Code emits a warning message in `stream-json` output, and shell commands fail until the directory exists again.
