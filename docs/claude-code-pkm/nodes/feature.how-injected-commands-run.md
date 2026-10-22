---
id: feature.how-injected-commands-run
kind: feature
status: VERIFIED
title: "How injected commands run"
sources: [S32]
---

# How injected commands run

**Sources:** [S32](src.s32.md)

Claude Code picks the tool that runs a skill's injected commands from the `shell` key in the skill's frontmatter and your environment. Every combination runs the commands through the Bash tool or the PowerShell tool, except one that fails the invocation outright:
