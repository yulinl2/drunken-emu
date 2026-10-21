---
id: env.claude-code-sync-plugin-install
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SYNC_PLUGIN_INSTALL"
sources: [S81]
---

# CLAUDE_CODE_SYNC_PLUGIN_INSTALL

**Sources:** [S81](src.s81.md)

Set to `1` in non-interactive mode (the `-p` flag) to wait for plugin installation to complete before the first query. Without this, plugins install in the background and may not be available on the first turn. Combine with `CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS` to bound the wait
