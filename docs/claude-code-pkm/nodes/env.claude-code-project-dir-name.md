---
id: env.claude-code-project-dir-name
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PROJECT_DIR_NAME"
sources: [S81]
---

# CLAUDE_CODE_PROJECT_DIR_NAME

**Sources:** [S81](src.s81.md)

Set together with `CLAUDE_CONFIG_DIR` to choose the `projects/` directory name Claude Code stores that session's transcripts and auto memory under, in place of one derived from the working directory path. For example, starting Claude Code with `CLAUDE_CONFIG_DIR=/srv/tenant-a CLAUDE_CODE_PROJECT_DIR_NAME=work claude` stores them under `/srv/tenant-a/projects/work/`. Claude Code ignores this variable when `CLAUDE_CONFIG_DIR` is unset, and reads it only from the environment you start `claude` from, never from a settings file `env` block. See Name the project directory yourself. Requires Claude Code v2.1.234 or later
