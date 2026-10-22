---
id: env.claude-code-skip-fast-mode-network-errors
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS"
sources: [S81]
---

# CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS

**Sources:** [S81](src.s81.md)

Set to `1` to treat a failed fast mode availability check as available, for networks that block the check's direct request to `api.anthropic.com`. Claude Code still honors a "disabled by your organization" response
