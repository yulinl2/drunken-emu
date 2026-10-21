---
id: feature.session-scratchpad-directory
kind: feature
status: VERIFIED
title: "Session scratchpad directory"
sources: [S16]
---

# Session scratchpad directory

**Sources:** [S16](src.s16.md)

The scratchpad is a per-session directory that Claude Code gives Claude for temporary files: intermediate results, helper scripts, and drafts that don't belong in your project. When Claude says it saved something "to the scratchpad", the file is there. Claude uses it instead of `/tmp`, and can create, edit, and read files in it without a permission prompt.
