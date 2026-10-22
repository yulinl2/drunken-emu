---
id: feature.resume-sessions-after-stopping-the-server
kind: feature
status: VERIFIED
title: "Resume sessions after stopping the server"
sources: [S21]
---

# Resume sessions after stopping the server

**Sources:** [S21](src.s21.md)

When you stop `claude remote-control` with Ctrl+C, the sessions it was serving stop responding from your phone or browser. As long as you weren't running another `claude remote-control` in the same directory and didn't start this one with `--no-create-session-in-dir`, Claude Code doesn't archive them. To bring them back, run one of these commands in the same directory:
