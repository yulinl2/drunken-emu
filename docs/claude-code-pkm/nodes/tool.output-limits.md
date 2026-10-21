---
id: tool.output-limits
kind: tool
status: VERIFIED
title: "Output limits"
sources: [S82]
---

# Output limits

**Sources:** [S82](src.s82.md)

Claude Code streams a command's output to a working file as the command runs; a command whose output passes 5 GB is killed. When the command finishes, Claude Code reads the output back from that file, up to the read-back window described below. How much of the output reaches Claude inline depends on whether Claude Code treats the result as a failure:
