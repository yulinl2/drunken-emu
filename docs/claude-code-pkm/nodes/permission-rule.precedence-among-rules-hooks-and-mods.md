---
id: permission-rule.precedence-among-rules-hooks-and-mods
kind: permission-rule
status: VERIFIED
title: "Precedence among rules, hooks, and mods"
sources: [S66]
---

# Precedence among rules, hooks, and mods

**Sources:** [S66](src.s66.md)

PreToolUse hook decisions don't bypass permission rules. Claude Code evaluates deny and ask rules regardless of what a PreToolUse hook returns: a matching deny rule blocks the call, and a matching ask rule still prompts even when the hook returned `"allow"` or `"ask"`. This preserves the deny-first precedence described in Manage permissions, including deny rules set in managed settings.
