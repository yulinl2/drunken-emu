---
id: env.claude-code-shell
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SHELL"
sources: [S81]
---

# CLAUDE_CODE_SHELL

**Sources:** [S81](src.s81.md)

Set the shell Claude Code uses to run Bash tool commands. Accepts a path to a `bash` or `zsh` binary, for example `/opt/homebrew/bin/bash`. Other shells such as `fish` are not supported. If the value is not a working `bash` or `zsh` path, Claude Code ignores it and falls back to auto-detection. Auto-detection uses your `$SHELL` when it points to `bash` or `zsh`, otherwise it picks the first working `zsh` then `bash` found on your `PATH` and standard install locations
