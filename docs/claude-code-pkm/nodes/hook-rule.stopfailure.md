---
id: hook-rule.stopfailure
kind: hook-rule
status: VERIFIED
title: "StopFailure"
sources: [S85]
---

# StopFailure

**Sources:** [S85](src.s85.md)

Runs instead of Stop when the turn ends due to an API error. Claude Code ignores the hook's output and exit code, apart from `terminalSequence`. Use this to log failures, send alerts, or take recovery actions when Claude can't complete a response due to rate limits, authentication problems, or other API errors.
