---
id: env.claude-code-force-session-persistence
kind: env
status: VERIFIED
title: "CLAUDE_CODE_FORCE_SESSION_PERSISTENCE"
sources: [S81]
---

# CLAUDE_CODE_FORCE_SESSION_PERSISTENCE

**Sources:** [S81](src.s81.md)

Set to `1` to force transcript persistence, prompt history, and `claude agents` registration even when this `claude` was launched from inside another Claude Code session. Use when an inherited `CLAUDE_CODE_CHILD_SESSION` value, for example from a `screen` session or a background launcher first started by Claude Code's Bash tool, causes a genuine top-level session to be misclassified as nested. As of v2.1.178, Claude Code detects the tmux case automatically and ignores the inherited marker, so tmux no longer needs this variable. Also honored on v2.1.169 and earlier; has no effect on v2.1.170 and v2.1.171, where the nested-session detection it overrides was removed
