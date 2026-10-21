---
id: feature.changing-output-style
kind: feature
status: VERIFIED
title: "Changing output style"
sources: [S18]
---

# Changing output style

**Sources:** [S18](src.s18.md)

When you switch output styles mid-session with `/output-style`, `/config`, or the `outputStyle` setting, Claude uses the new style starting with your next message. Claude Code delivers the new style's instructions as a message in the conversation, so that request still reads the system prompt and the earlier conversation from the cache.
