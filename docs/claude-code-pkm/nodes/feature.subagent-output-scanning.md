---
id: feature.subagent-output-scanning
kind: feature
status: VERIFIED
title: "Subagent output scanning"
sources: [S25]
---

# Subagent output scanning

**Sources:** [S25](src.s25.md)

Claude Code scans each subagent's final report before Claude reads it. A subagent may have read files, web pages, or command output you never reviewed, and text from those sources can carry instructions aimed at the main conversation. The scan never removes or rewords anything; it makes two kinds of change you may notice in a report:
