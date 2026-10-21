---
id: feature.denying-an-entire-tool
kind: feature
status: VERIFIED
title: "Denying an entire tool"
sources: [S18]
---

# Denying an entire tool

**Sources:** [S18](src.s18.md)

If you add a bare tool name like `Bash` or `WebFetch` as a deny rule, Claude can't call that tool from your next request on, whether you add the rule through `/permissions` or by editing a settings file directly. That includes a rule you add through `/permissions` in the middle of a turn.
