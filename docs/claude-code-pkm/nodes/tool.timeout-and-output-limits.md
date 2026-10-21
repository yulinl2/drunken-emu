---
id: tool.timeout-and-output-limits
kind: tool
status: VERIFIED
title: "Timeout and output limits"
sources: [S82]
---

# Timeout and output limits

**Sources:** [S82](src.s82.md)

Each command runs under a timeout, and Claude manages it: when it wants longer than the default for a command, it passes the `timeout` parameter with that call. You never set a per-command timeout.
