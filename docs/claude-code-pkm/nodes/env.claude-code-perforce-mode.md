---
id: env.claude-code-perforce-mode
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PERFORCE_MODE"
sources: [S81]
---

# CLAUDE_CODE_PERFORCE_MODE

**Sources:** [S81](src.s81.md)

Set to `1` to enable Perforce-aware write protection. When set, Edit, Write, and NotebookEdit fail with a `p4 edit ` hint if the target file lacks the owner-write bit, which Perforce clears on synced files until `p4 edit` opens them. This prevents Claude Code from bypassing Perforce change tracking
