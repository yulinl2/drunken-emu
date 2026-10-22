---
id: feature.upgrading-claude-code
kind: feature
status: VERIFIED
title: "Upgrading Claude Code"
sources: [S18]
---

# Upgrading Claude Code

**Sources:** [S18](src.s18.md)

A new Claude Code version typically updates the system prompt or tool definitions, so the first conversation you start after an upgrade builds its cache from the top. Auto-update downloads new versions in the background but applies them on the next launch, never mid-session, so you see this as an uncached first turn after restarting rather than a surprise during a session. Set `DISABLE_AUTOUPDATER
