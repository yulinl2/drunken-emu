---
id: env.claude-code-forward-subagent-text
kind: env
status: VERIFIED
title: "CLAUDE_CODE_FORWARD_SUBAGENT_TEXT"
sources: [S81]
---

# CLAUDE_CODE_FORWARD_SUBAGENT_TEXT

**Sources:** [S81](src.s81.md)

Set to `1` to emit subagent text and thinking blocks in `claude -p --output-format stream-json` output, the same behavior as the `--forward-subagent-text` flag. Use the variable when a harness invokes `claude` and can't pass the flag itself. Unlike the flag, which exits with an error outside non-interactive mode with stream-json output, the variable is ignored there so that nested invocations keep working when it's set process-wide. Requires Claude Code v2.1.211 or later
