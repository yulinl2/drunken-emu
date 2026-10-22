---
id: env.claude-code-subagent-model
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SUBAGENT_MODEL"
sources: [S81]
---

# CLAUDE_CODE_SUBAGENT_MODEL

**Sources:** [S81](src.s81.md)

The default model for subagents, agent team teammates, and workflow agents that aren't assigned a model another way. Accepts an alias such as `haiku` or a full model name. Two sources take precedence over it: a model Claude passes when it spawns the agent, and a `model` field in the agent's definition, including `inherit`. To change that, set `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`. See Choose a model for the full order. Setting it to `inherit` is the same as leaving it unset. Before v2.1.251, this variable overrode both the per-invocation model and the definition's `model` field
