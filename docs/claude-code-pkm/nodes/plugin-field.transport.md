---
id: plugin-field.transport
kind: plugin-field
status: VERIFIED
title: "transport"
sources: [S50]
---

# transport

**Sources:** [S50](src.s50.md)

Communication transport: `stdio` (default) or `socket`. Claude Code accepts `socket` but runs every server over stdio, so the stdout protocol rules apply to all servers (required: No)
