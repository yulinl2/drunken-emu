---
id: feature.add-a-custom-model-option
kind: feature
status: VERIFIED
title: "Add a custom model option"
sources: [S70]
---

# Add a custom model option

**Sources:** [S70](src.s70.md)

Use `ANTHROPIC_CUSTOM_MODEL_OPTION` to add a single custom entry to the `/model` picker without replacing the built-in aliases. This is useful for testing model IDs that Claude Code does not list by default. For LLM gateway deployments, Claude Code can populate the picker from the gateway's `/v1/models` endpoint when `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` is set, so this variable is needed
