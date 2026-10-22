---
id: hook-rule.subagentstop-input
kind: hook-rule
status: VERIFIED
title: "SubagentStop input"
sources: [S85]
---

# SubagentStop input

**Sources:** [S85](src.s85.md)

In addition to the common input fields, SubagentStop hooks receive `stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path`, and `last_assistant_message`. The `agent_type` field is the value used for matcher filtering. The `transcript_path` is the main session's transcript, while `agent_transcript_path` is the subagent's own transcript stored in a nested `subagents/` folder. The `last
