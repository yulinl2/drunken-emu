---
id: cmd.heapdump
kind: command
status: VERIFIED
title: "/heapdump"
sources: [S80]
---

# /heapdump

**Sources:** [S80](src.s80.md)

Write a JavaScript heap snapshot and a memory breakdown to `~/Desktop`, or your home directory on Linux without a Desktop folder, for diagnosing high memory usage. Attach only the `-diagnostics.json` file when reporting a memory issue; the `.heapsnapshot` contains your full conversation and credentials, so don't share it. Hidden from the command menu; type it in full. See what to do with the output
