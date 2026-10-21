---
id: feature.what-the-sandbox-restricts
kind: feature
status: VERIFIED
title: "What the sandbox restricts"
sources: [S68]
---

# What the sandbox restricts

**Sources:** [S68](src.s68.md)

While the sandbox is on, the shell commands Claude runs start inside its boundary, and so do the processes they start. The sandbox is off by default. To turn it on, run `/sandbox` in a session, as Get started shows, or set `sandbox.enabled` to `true` in a settings file such as `~/.claude/settings.json`.
