---
id: hook-rule.defer-a-tool-call-for-later
kind: hook-rule
status: VERIFIED
title: "Defer a tool call for later"
sources: [S85]
---

# Defer a tool call for later

**Sources:** [S85](src.s85.md)

`"defer"` is for integrations that run `claude -p` as a subprocess and read its JSON output, such as an Agent SDK app or a custom UI built on top of Claude Code. It lets that calling process pause Claude at a tool call, collect input through its own interface, and resume where it left off. Claude Code honors this value only in non-interactive mode with the `-p` flag. In interactive sessions it log
