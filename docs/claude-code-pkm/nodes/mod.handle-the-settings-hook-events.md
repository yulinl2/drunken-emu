---
id: mod.handle-the-settings-hook-events
kind: mod
status: VERIFIED
title: "Handle the settings hook events"
sources: [S55]
---

# Handle the settings hook events

**Sources:** [S55](src.s55.md)

Settings hooks are the command, HTTP, prompt, and agent hooks you configure in settings files. Each settings hook event, such as `Stop`, `SessionEnd`, or `PostToolUse`, is also an event named `classic.` followed by the settings hook event's name, such as `classic.Stop`. `e` is the JSON a settings hook receives on stdin, including `transcript_path`.
