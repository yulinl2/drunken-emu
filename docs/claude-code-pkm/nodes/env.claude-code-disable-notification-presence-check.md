---
id: env.claude-code-disable-notification-presence-check
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_NOTIFICATION_PRESENCE_CHECK"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_NOTIFICATION_PRESENCE_CHECK

**Sources:** [S81](src.s81.md)

Set to `1` to send the `PushNotification` tool's desktop notification even while you are typing in or focused on the terminal. By default the tool skips both the desktop notification and the mobile push when it detects recent keyboard activity or terminal focus. This variable disables only that local check, so the server can still suppress the mobile push when it detects that you are active. Requires Claude Code v2.1.193 or later
