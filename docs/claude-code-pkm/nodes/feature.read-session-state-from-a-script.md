---
id: feature.read-session-state-from-a-script
kind: feature
status: VERIFIED
title: "Read session state from a script"
sources: [S26]
---

# Read session state from a script

**Sources:** [S26](src.s26.md)

`claude agents --json` is the supported way to read session state from outside Claude Code, for example from a status bar, a scheduler, or another Claude session that supervises background work. Poll `claude agents --json --all`, which keeps listing sessions whose process has exited, and read each entry's `state`, `status`, and `waitingFor`.
