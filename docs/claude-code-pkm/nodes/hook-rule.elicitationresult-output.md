---
id: hook-rule.elicitationresult-output
kind: hook-rule
status: VERIFIED
title: "ElicitationResult output"
sources: [S85]
---

# ElicitationResult output

**Sources:** [S85](src.s85.md)

An ElicitationResult hook can let the user's response through, change its values, or block it. To change or block the response, exit 0 and print a `hookSpecificOutput` object with an `action`. Each row of this table shows what to return for one outcome and what the MCP server receives:
