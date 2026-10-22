---
id: hook-rule.stdin-common-fields
kind: hook-rule
status: VERIFIED
title: "Stdin: common fields"
sources: [S2]
---

# Stdin: common fields

**Sources:** [S2](src.s2.md)

Every command hook reads: session_id, prompt_id, transcript_path, cwd, scratchpad_dir (v2.1.257 or later), permission_mode, effort (with a level field), hook_event_name, agent_id and agent_type. HTTP hooks receive the same JSON as the POST body.
