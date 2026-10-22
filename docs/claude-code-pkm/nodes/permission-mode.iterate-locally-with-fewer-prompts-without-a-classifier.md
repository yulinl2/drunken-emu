---
id: permission-mode.iterate-locally-with-fewer-prompts-without-a-classifier
kind: permission-mode
status: VERIFIED
title: "Iterate locally with fewer prompts, without a classifier"
sources: [S67]
---

# Iterate locally with fewer prompts, without a classifier

**Sources:** [S67](src.s67.md)

Deny rules still apply, and ask rules that name a command, such as `Bash(git push *)`, still prompt. Auto-allow mode covers other commands that can prompt. To turn the sandbox on from a settings file instead, set `sandbox.enabled` to `true` (start with: Manual mode plus the Bash sandbox in auto-allow mode: `claude --permission-mode default`, then run `/sandbox` and select auto-allow; isolation needed: The built-in Bash sandbox, on macOS, Linux, and WSL2)
