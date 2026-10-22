---
id: env.claude-code-disable-git-instructions
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS

**Sources:** [S81](src.s81.md)

Set to `1` to remove built-in commit and PR workflow instructions and the git status snapshot from Claude's context. Useful when using your own git workflow skills. Takes precedence over the `includeGitInstructions` setting when set
