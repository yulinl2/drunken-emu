---
id: feature.protected-paths
kind: feature
status: VERIFIED
title: "Protected paths"
sources: [S68]
---

# Protected paths

**Sources:** [S68](src.s68.md)

Inside the directories that sandboxed commands can write to, the sandbox still denies writes to the files Claude Code loads configuration and code from. A command that could edit those files could grant itself permissions, or add a hook or MCP server that Claude Code runs outside the sandbox. The permission system has its own protected paths, which control what Claude Code approves before a tool r
