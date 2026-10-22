---
id: env.claude-code-startup-failure-results
kind: env
status: VERIFIED
title: "CLAUDE_CODE_STARTUP_FAILURE_RESULTS"
sources: [S81]
---

# CLAUDE_CODE_STARTUP_FAILURE_RESULTS

**Sources:** [S81](src.s81.md)

Set to `1` to have a session started with `--output-format stream-json` write a result message naming why Claude Code refused to start for startup failures that otherwise end with stderr alone. Requires Claude Code v2.1.274 or later
