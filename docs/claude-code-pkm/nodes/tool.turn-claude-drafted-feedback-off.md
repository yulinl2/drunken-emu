---
id: tool.turn-claude-drafted-feedback-off
kind: tool
status: VERIFIED
title: "Turn Claude-drafted feedback off"
sources: [S82]
---

# Turn Claude-drafted feedback off

**Sources:** [S82](src.s82.md)

Set Claude-drafted feedback to `off` in `/config`, which writes the `feedbackDrafts` setting, or set `CLAUDE_CODE_SEND_FEEDBACK=0` for one session. With either, Claude can't queue drafts. To keep drafting on without cards, set `feedbackDrafts` to `quiet` instead. Administrators can set `feedbackDrafts` in managed settings, which takes precedence over your own setting.
