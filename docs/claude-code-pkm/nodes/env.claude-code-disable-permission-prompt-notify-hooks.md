---
id: env.claude-code-disable-permission-prompt-notify-hooks
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS

**Sources:** [S81](src.s81.md)

Set to `1` to stop Claude Code from running your `Notification` hooks for unanswered permission requests in sessions where Claude Code sends them to the Agent SDK's `canUseTool` callback, which is how Claude Desktop and the VS Code extension host Claude Code. Has no effect in terminal sessions. Requires Claude Code v2.1.233 or later
