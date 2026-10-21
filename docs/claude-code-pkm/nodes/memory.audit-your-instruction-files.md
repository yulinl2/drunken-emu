---
id: memory.audit-your-instruction-files
kind: memory
status: VERIFIED
title: "Audit your instruction files"
sources: [S19]
---

# Audit your instruction files

**Sources:** [S19](src.s19.md)

To have Claude check your instruction files for outdated or conflicting content, run `/doctor prompt-audit` in a session. Claude looks for problems such as instructions written for older models, references to files or commands that don't exist, and files that contradict each other. You get a report of findings with proposed edits, and nothing in your files changes until you ask Claude to apply the
