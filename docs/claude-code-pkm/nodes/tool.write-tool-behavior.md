---
id: tool.write-tool-behavior
kind: tool
status: VERIFIED
title: "Write tool behavior"
sources: [S82]
---

# Write tool behavior

**Sources:** [S82](src.s82.md)

The Write tool creates a new file or overwrites an existing one with the full content provided. It doesn't append or merge. Write also overwrites an existing file whose bytes don't decode and saves the new content as UTF-8, as described under non-UTF-8 files.
