---
id: hook-rule.hook-input-and-output
kind: hook-rule
status: VERIFIED
title: "Hook input and output"
sources: [S85]
---

# Hook input and output

**Sources:** [S85](src.s85.md)

Command hooks receive JSON data via stdin and communicate results through exit codes, stdout, and stderr. HTTP hooks receive the same JSON as the POST request body and communicate results through the HTTP response body. This section covers fields and behavior common to all events. Each event's section under Hook events includes its specific input schema and decision control options.
