---
id: env.claude-code-sync-skills
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SYNC_SKILLS"
sources: [S81]
---

# CLAUDE_CODE_SYNC_SKILLS

**Sources:** [S81](src.s81.md)

Set to `1` in non-interactive mode with the `-p` flag to make Claude Code download the skills enabled for your claude.ai account in that run and wait for the list of them, up to `CLAUDE_CODE_SYNC_SKILLS_WAIT_TIMEOUT_MS`, before it runs the first query. Requires claude.ai authentication. Terminal sessions where you sign in with your claude.ai account sync these skills without this variable, so set it only when a `-p` run needs your current skills on its first query
