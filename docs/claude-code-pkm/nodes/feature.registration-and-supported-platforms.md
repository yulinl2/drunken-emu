---
id: feature.registration-and-supported-platforms
kind: feature
status: VERIFIED
title: "Registration and supported platforms"
sources: [S39]
---

# Registration and supported platforms

**Sources:** [S39](src.s39.md)

Claude Code registers the `claude-cli://` handler with your operating system on macOS, Linux, and Windows when you send your first prompt of an interactive session. Starting `claude` and exiting without sending a prompt doesn't register the handler. You don't run a separate install command. Registration writes to user-level locations only:
