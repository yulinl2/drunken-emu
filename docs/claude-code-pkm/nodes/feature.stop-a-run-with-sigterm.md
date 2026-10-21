---
id: feature.stop-a-run-with-sigterm
kind: feature
status: VERIFIED
title: "Stop a run with SIGTERM"
sources: [S38]
---

# Stop a run with SIGTERM

**Sources:** [S38](src.s38.md)

If you stop a `claude -p` run with SIGTERM, for example with `kill` or from a process supervisor, Claude Code exits with code 143. Claude Code leaves the turn that was in progress unfinished and records no result for it. To end the turn instead, send SIGINT, or call the Agent SDK's `interrupt()`, before you stop the process.
