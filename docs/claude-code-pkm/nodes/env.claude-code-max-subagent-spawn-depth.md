---
id: env.claude-code-max-subagent-spawn-depth
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH"
sources: [S81]
---

# CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH

**Sources:** [S81](src.s81.md)

Number of subagent layers allowed below the main conversation (default: 3). At the default, subagents can spawn their own subagents, and a subagent at the third layer can't spawn further; set `1` to turn nesting off. In v2.1.217 through v2.1.218, the default was 1, so a subagent couldn't spawn its own unless you raised the limit; v2.1.219 raised the default to 3. Accepts a positive whole number in plain digits; anything else is ignored, so the limit can be adjusted but not removed. Requires Claude Code v2.1.217 or later
