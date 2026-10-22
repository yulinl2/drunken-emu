---
id: hook-rule.block-the-action-when-a-hook-fails
kind: hook-rule
status: VERIFIED
title: "Block the action when a hook fails"
sources: [S85]
---

# Block the action when a hook fails

**Sources:** [S85](src.s85.md)

On most events, when a hook fails or times out, Claude Code still carries out the action. A policy hook with a wrong path or a crashing script then lets everything through. To block the action instead, set `"onFailure": "block"` on a `command` or `http` hook. Requires Claude Code v2.1.295 or later.
