---
id: env.claude-code-force-strikethrough
kind: env
status: VERIFIED
title: "CLAUDE_CODE_FORCE_STRIKETHROUGH"
sources: [S81]
---

# CLAUDE_CODE_FORCE_STRIKETHROUGH

**Sources:** [S81](src.s81.md)

Set to `1` to force strikethrough rendering for `~~text~~` in Claude's responses when your terminal supports it but is not auto-detected, such as over SSH without `TERM_PROGRAM` forwarded. Without this, undetected terminals show the literal `~~` markers instead of rendering the text as strikethrough. Requires Claude Code v2.1.186 or later
