---
id: env.claude-code-disable-dangerous-rm-timeout
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_DANGEROUS_RM_TIMEOUT"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_DANGEROUS_RM_TIMEOUT

**Sources:** [S81](src.s81.md)

Set to `1` to turn off the time limit on critical-path removal prompts. In `auto` mode Claude Code then sends these removals to the classifier instead, and in `bypassPermissions` mode the prompt waits for your answer. Set it in the environment that launches Claude Code, since Claude Code ignores a copy delivered through a settings `env` block. Requires Claude Code v2.1.281 or later
