---
id: permission-rule.webfetch-permissions
kind: permission-rule
status: VERIFIED
title: "WebFetch"
sources: [S66]
---

# WebFetch

**Sources:** [S66](src.s66.md)

in `allow`: Claude fetches without prompting you. Doesn't change which hosts sandboxed commands can reach.; in `deny`: Claude Code removes the `WebFetch` tool, so Claude can't fetch at all. Doesn't change which hosts sandboxed commands can reach.
