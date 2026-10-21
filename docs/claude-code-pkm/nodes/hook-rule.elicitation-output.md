---
id: hook-rule.elicitation-output
kind: hook-rule
status: VERIFIED
title: "Elicitation output"
sources: [S85]
---

# Elicitation output

**Sources:** [S85](src.s85.md)

An Elicitation hook can answer the request for the user, decline or cancel it, or leave it to the dialog. To answer, decline, or cancel, exit 0 and print a `hookSpecificOutput` object with an `action`. The server gets your answer and no dialog appears. Each row of this table shows what to return for one outcome and what the MCP server receives:
