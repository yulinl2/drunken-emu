---
id: env.claude-code-disable-auto-memory
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_AUTO_MEMORY"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_AUTO_MEMORY

**Sources:** [S81](src.s81.md)

Set to `1` to disable auto memory. Set to `0` to force auto memory on even when `--bare` mode or `autoMemoryEnabled: false` would otherwise disable it. When disabled, Claude does not create or load auto memory files
