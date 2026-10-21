---
id: skill-field.disallowed-tools
kind: skill-field
status: VERIFIED
title: "disallowed-tools"
sources: [S32]
---

# disallowed-tools

**Sources:** [S32](src.s32.md)

Tools removed from Claude's available pool while this skill is active. Use for autonomous skills that should never call certain tools, such as `AskUserQuestion` for a background loop. Accepts a space- or comma-separated string, or a YAML list. The restriction clears when you send your next message. Like deny rules, the field can't remove `EndConversation` while any other tool remains. (required: No)
