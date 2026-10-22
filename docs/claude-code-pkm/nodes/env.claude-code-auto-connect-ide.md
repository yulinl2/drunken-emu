---
id: env.claude-code-auto-connect-ide
kind: env
status: VERIFIED
title: "CLAUDE_CODE_AUTO_CONNECT_IDE"
sources: [S81]
---

# CLAUDE_CODE_AUTO_CONNECT_IDE

**Sources:** [S81](src.s81.md)

Override automatic IDE connection. By default, Claude Code connects automatically when launched inside a supported IDE's integrated terminal. Set to `false` to prevent this. Set to `true` to force a connection attempt when auto-detection fails, such as when tmux obscures the parent terminal. Takes precedence over the `autoConnectIde` global config setting
