---
id: env.claude-code-disable-official-marketplace-autoinstall
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL

**Sources:** [S81](src.s81.md)

Set to `1` to disable automatic registration of the official plugin marketplace. Claude Code reads the variable when it is about to register the marketplace, usually during a machine's first interactive launch. If the variable is set at that point, Claude Code skips the registration permanently. Unsetting the variable later doesn't undo the skip. Run `claude plugin marketplace add anthropics/claude-plugins-official` to register the marketplace at any time
