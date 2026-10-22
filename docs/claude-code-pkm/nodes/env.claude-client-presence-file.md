---
id: env.claude-client-presence-file
kind: env
status: VERIFIED
title: "CLAUDE_CLIENT_PRESENCE_FILE"
sources: [S81]
---

# CLAUDE_CLIENT_PRESENCE_FILE

**Sources:** [S81](src.s81.md)

Path to a file that an external tool, such as a screen-lock listener, creates when you unlock your screen and deletes when you lock it. While the file exists, Claude Code skips Remote Control mobile push notifications, so you stop getting pushes while you are actively using the computer. When the file is absent or unreadable, notifications are sent as normal. Claude Code checks the file once per push-triggering event rather than polling it. Requires Claude Code v2.1.181 or later
