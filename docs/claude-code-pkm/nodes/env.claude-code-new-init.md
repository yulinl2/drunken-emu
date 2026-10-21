---
id: env.claude-code-new-init
kind: env
status: VERIFIED
title: "CLAUDE_CODE_NEW_INIT"
sources: [S81]
---

# CLAUDE_CODE_NEW_INIT

**Sources:** [S81](src.s81.md)

Set to `1` to make `/init` run an interactive setup flow. The flow asks which files to generate, including CLAUDE.md, skills, and hooks, before exploring the codebase and writing them. Without this variable, `/init` generates a CLAUDE.md automatically without prompting
