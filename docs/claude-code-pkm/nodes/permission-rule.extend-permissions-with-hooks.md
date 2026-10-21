---
id: permission-rule.extend-permissions-with-hooks
kind: permission-rule
status: VERIFIED
title: "Extend permissions with hooks"
sources: [S66]
---

# Extend permissions with hooks

**Sources:** [S66](src.s66.md)

Claude Code hooks let you register custom shell commands that evaluate permissions at runtime. When Claude Code makes a tool call, PreToolUse hooks run before the permission prompt, for every tool except `EndConversation`. The hook output can deny the tool call, force a prompt, or skip the prompt to let the call proceed.
