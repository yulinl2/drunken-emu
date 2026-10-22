---
id: feature.what-auto-mode-setup-reads
kind: feature
status: VERIFIED
title: "What /auto-mode-setup reads"
sources: [S64]
---

# What /auto-mode-setup reads

**Sources:** [S64](src.s64.md)

If `~/.claude/settings.json` already holds `autoMode` entries, Claude Code starts by asking whether to add to your environment list or replace it, and keeps the rules you wrote either way. Claude Code then asks how you use this project and offers two optional scans before it scans anything. In the scan, Claude Code always reads these sources:
