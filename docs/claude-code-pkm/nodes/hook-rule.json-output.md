---
id: hook-rule.json-output
kind: hook-rule
status: VERIFIED
title: "JSON output"
sources: [S85]
---

# JSON output

**Sources:** [S85](src.s85.md)

Exit codes only let you block or stay silent, but JSON output gives you finer-grained control. Instead of exiting with code 2 to block, exit 0 and print a JSON object to stdout. Claude Code reads specific fields from that JSON to control behavior, including decision control for blocking, allowing, or escalating to the user.
