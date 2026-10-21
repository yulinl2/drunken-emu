---
id: env.claude-code-git-bash-path
kind: env
status: VERIFIED
title: "CLAUDE_CODE_GIT_BASH_PATH"
sources: [S81]
---

# CLAUDE_CODE_GIT_BASH_PATH

**Sources:** [S81](src.s81.md)

Windows only: path to the Git Bash executable (`bash.exe`). Use when Git Bash is installed but not in your PATH. If the path doesn't exist or the file isn't named `bash.exe`, `sh.exe`, `bash`, or `sh`, Claude Code ignores the variable and auto-detects Git Bash as if it were unset, logging a warning visible with `--debug`. Before v2.1.219, Claude Code exited at startup when the path didn't exist, and used any existing file as the shell without checking that it was bash or sh. See Windows setup
