---
id: feature.remote-settings-json
kind: feature
status: VERIFIED
title: "remote-settings.json"
sources: [S16]
---

# remote-settings.json

**Sources:** [S16](src.s16.md)

contents: Cached copy of server-managed settings for your organization, or `{}` when your organization has configured none. Only present when the session fetches them. Claude Code checks for updates at startup and hourly during a session. Claude Code deletes it when you log out.
