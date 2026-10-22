---
id: env.claude-code-idle-compact-min-tokens
kind: env
status: VERIFIED
title: "CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS"
sources: [S81]
---

# CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS

**Sources:** [S81](src.s81.md)

Context size, in tokens, at which idle compaction applies to a conversation (default: `200000`). Accepts a positive whole number, and anything else is ignored. Values below `100000` are raised to `100000`, the lowest threshold. Idle compaction is on by default for conversations that meet its conditions. To turn it off, set `idleCompaction` to `false`. Requires Claude Code v2.1.290 or later
