---
id: env.claude-code-enable-background-plugin-refresh
kind: env
status: VERIFIED
title: "CLAUDE_CODE_ENABLE_BACKGROUND_PLUGIN_REFRESH"
sources: [S81]
---

# CLAUDE_CODE_ENABLE_BACKGROUND_PLUGIN_REFRESH

**Sources:** [S81](src.s81.md)

Set to `1` to refresh plugin state at turn boundaries in non-interactive mode after a background install completes. Off by default because the refresh changes the system prompt mid-session, which invalidates prompt caching for that turn
