---
id: env.claude-code-disable-substitution-rm-prompt
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_SUBSTITUTION_RM_PROMPT"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_SUBSTITUTION_RM_PROMPT

**Sources:** [S81](src.s81.md)

Set to `1` to turn off the critical-path check for a recursive `rm` whose target is entirely the output of a command substitution, such as `rm -rf "$(pwd)"`. The other critical-path checks keep running. Set it in the environment that launches Claude Code, since Claude Code ignores a copy delivered through a settings `env` block. Requires Claude Code v2.1.281 or later
