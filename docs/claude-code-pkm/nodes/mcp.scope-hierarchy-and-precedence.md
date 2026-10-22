---
id: mcp.scope-hierarchy-and-precedence
kind: mcp
status: VERIFIED
title: "Scope hierarchy and precedence"
sources: [S31]
---

# Scope hierarchy and precedence

**Sources:** [S31](src.s31.md)

When the same server is defined in more than one place, Claude Code connects to it once, using the definition from the highest-precedence source. The entire server entry from that source is used; fields are not merged across scopes.
