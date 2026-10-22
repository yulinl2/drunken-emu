---
id: env.claude-code-user-dialog-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_USER_DIALOG_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_CODE_USER_DIALOG_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Deadline in milliseconds before Claude Code cancels a dialog it forwards to a remote client such as a Remote Control or SDK host, or the approval dialog for a held cross-session message; permission prompts and `AskUserQuestion` questions use their own flows and aren't governed by it. On Claude Code v2.1.236 or later, it also bounds the mid-session Fable usage-credits consent prompt in a session that may be running unattended. Control inbound messages and non-interactive sessions cover the full held-message expiry rules, including the cases where the deadline doesn't apply. Overrides the `dialogExpiry` setting. `0` or a negative value disables the deadline. Ignored in project and local settings
