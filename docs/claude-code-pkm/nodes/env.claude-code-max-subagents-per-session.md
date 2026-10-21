---
id: env.claude-code-max-subagents-per-session
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION"
sources: [S81]
---

# CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION

**Sources:** [S81](src.s81.md)

Removed in v2.1.224 and now a no-op. Previously capped the total number of subagents Claude could spawn with the Agent tool in one session (default: 200); spawning past the cap failed with `Subagent spawn limit reached`. The concurrent subagent limit and the depth limit still apply
