---
id: feature.customize-the-system-prompt
kind: feature
status: VERIFIED
title: "Customize the system prompt"
sources: [S38]
---

# Customize the system prompt

**Sources:** [S38](src.s38.md)

Use `--append-system-prompt` to add instructions while keeping Claude Code's default behavior. This example pipes a PR diff to Claude and instructs it to review for security vulnerabilities. Save it as a shell script, for example `review.sh`:
