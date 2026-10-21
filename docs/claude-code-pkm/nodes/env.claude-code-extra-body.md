---
id: env.claude-code-extra-body
kind: env
status: VERIFIED
title: "CLAUDE_CODE_EXTRA_BODY"
sources: [S81]
---

# CLAUDE_CODE_EXTRA_BODY

**Sources:** [S81](src.s81.md)

JSON object to merge into the top level of every API request body. Useful for passing provider-specific parameters that Claude Code doesn't expose directly. A value exported in your shell also applies to the background sessions you dispatch with `claude agents` or `--bg`. Before v2.1.206, background sessions ignored a shell-exported value and used whatever copy the background supervisor process inherited
