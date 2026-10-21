---
id: env.claude-code-enable-cfc
kind: env
status: VERIFIED
title: "CLAUDE_CODE_ENABLE_CFC"
sources: [S81]
---

# CLAUDE_CODE_ENABLE_CFC

**Sources:** [S81](src.s81.md)

Set to `1` to start a CLI session with Chrome integration on, or `0` to start with it off. Takes precedence over the `claudeInChromeDefaultEnabled` setting. The `--chrome` and `--no-chrome` flags take precedence over both. Claude Code ignores `1` in project and local settings
