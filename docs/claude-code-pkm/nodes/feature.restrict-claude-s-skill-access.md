---
id: feature.restrict-claude-s-skill-access
kind: feature
status: VERIFIED
title: "Restrict Claude's skill access"
sources: [S32]
---

# Restrict Claude's skill access

**Sources:** [S32](src.s32.md)

By default, Claude can invoke any skill that doesn't have `disable-model-invocation: true` set. Skills that define `allowed-tools` grant Claude access to those tools without per-use approval during the turn that invokes the skill; the grant clears when you send your next message. Your permission settings still govern baseline approval behavior for all other tools. A few built-in commands are also
