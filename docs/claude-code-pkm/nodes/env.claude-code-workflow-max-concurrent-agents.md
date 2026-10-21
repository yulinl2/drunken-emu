---
id: env.claude-code-workflow-max-concurrent-agents
kind: env
status: VERIFIED
title: "CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS"
sources: [S81]
---

# CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS

**Sources:** [S81](src.s81.md)

How many agents a single workflow run executes at once, from `1` to `256`. By default, a run executes up to 16 agents at once, fewer when Claude Code has fewer CPUs available; queued `agent()` calls wait for a free slot. Each running agent's transcript stays in Claude Code's memory, so higher values raise memory use. Takes plain digits only; out-of-range values and other spellings keep the default. Requires Claude Code v2.1.269 or later
