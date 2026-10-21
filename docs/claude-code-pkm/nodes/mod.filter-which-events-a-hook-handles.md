---
id: mod.filter-which-events-a-hook-handles
kind: mod
status: VERIFIED
title: "Filter which events a hook handles"
sources: [S55]
---

# Filter which events a hook handles

**Sources:** [S55](src.s55.md)

To run a hook for some events only, pass a filter as the second argument to `on`. Claude Code calls the filter a matcher. It's an object whose fields are compared with the event's, and the hook runs only when every field matches. A field can be a value, an array of allowed values, or a regular expression.
