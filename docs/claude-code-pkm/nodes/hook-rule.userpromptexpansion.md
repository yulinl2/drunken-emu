---
id: hook-rule.userpromptexpansion
kind: hook-rule
status: VERIFIED
title: "UserPromptExpansion"
sources: [S85]
---

# UserPromptExpansion

**Sources:** [S85](src.s85.md)

Runs when a user-typed command expands into a prompt before reaching Claude. Use this to block specific commands from direct invocation, inject context for a particular skill, or log which commands users invoke. For example, a hook matching `deploy` can block `/deploy` unless an approval file is present, or a hook matching a review skill can append the team's review checklist as `additionalContext
