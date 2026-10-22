---
id: feature.list-sessions-as-json
kind: feature
status: VERIFIED
title: "List sessions as JSON"
sources: [S26]
---

# List sessions as JSON

**Sources:** [S26](src.s26.md)

`claude agents --json` prints active sessions as a JSON array and exits: every live session, plus background sessions that are still working or blocked even when their process has exited. Add `--all` to also include completed background sessions, and `--cwd ` to limit the list to sessions started under that directory.
