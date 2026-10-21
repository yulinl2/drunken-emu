---
id: feature.name-the-project-directory-yourself
kind: feature
status: VERIFIED
title: "Name the project directory yourself"
sources: [S20]
---

# Name the project directory yourself

**Sources:** [S20](src.s20.md)

By default, Claude Code derives the `` name from the whole working directory path. To choose the name yourself, set `CLAUDE_CODE_PROJECT_DIR_NAME` alongside `CLAUDE_CONFIG_DIR`. Claude Code then stores that session's transcripts and auto memory under your name. This suits a host that embeds Claude Code and gives each session its own config directory. Requires Claude Code v2.1.234 or later.
