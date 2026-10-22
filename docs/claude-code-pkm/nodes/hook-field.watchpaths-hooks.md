---
id: hook-field.watchpaths-hooks
kind: hook-field
status: VERIFIED
title: "watchPaths"
sources: [S85]
---

# watchPaths

**Sources:** [S85](src.s85.md)

Array of absolute paths. Replaces the current dynamic watch list. Paths from your `matcher` configuration are always watched. Returning an empty array clears the dynamic list, which is typical when entering a new directory
