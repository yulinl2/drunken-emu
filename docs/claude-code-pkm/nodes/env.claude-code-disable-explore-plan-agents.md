---
id: env.claude-code-disable-explore-plan-agents
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS

**Sources:** [S81](src.s81.md)

Set to `1` to disable the built-in Explore and Plan subagents. Claude explores with its search tools or the general-purpose subagent instead, and plan mode reads files directly rather than launching Explore and Plan agents. Custom subagents named `Explore` or `Plan` are unaffected. To remove every built-in subagent type in the Agent SDK or non-interactive mode, use `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS` instead. Requires Claude Code v2.1.198 or later
