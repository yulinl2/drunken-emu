---
id: feature.inject-dynamic-context
kind: feature
status: VERIFIED
title: "Inject dynamic context"
sources: [S32]
---

# Inject dynamic context

**Sources:** [S32](src.s32.md)

The `` !`` `` syntax runs shell commands before the skill content is sent to Claude. The command output replaces the placeholder, so Claude receives actual data, not the command itself. Claude Code doesn't run these commands on your machine when the skill is synced from your claude.ai account. This restriction requires Claude Code v2.1.228 or later.
