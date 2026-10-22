---
id: cmd.rename
kind: command
status: VERIFIED
title: "/rename"
sources: [S80]
---

# /rename

**Sources:** [S80](src.s80.md)

Rename the current session and show the name on the prompt bar. Without a name, auto-generates one from conversation history. Also available in non-interactive mode (`-p`). From every rename surface, including claude.ai and the desktop app, Claude Code replaces control and invisible characters in the new name with spaces and caps the name at 200 characters. If the name is empty once invisible characters are removed, Claude Code rejects it and shows `That name is empty once invisible characters are removed. Usage: /rename `. The character replacement and length cap require Claude Code v2.1.221 or later
