---
id: env.claude-code-enable-gateway-model-discovery
kind: env
status: VERIFIED
title: "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY"
sources: [S81]
---

# CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY

**Sources:** [S81](src.s81.md)

Set to `1` to populate the `/model` picker from your gateway's `/v1/models` endpoint when `ANTHROPIC_BASE_URL` points at an Anthropic-compatible gateway such as LiteLLM, Kong, or an internal proxy. Off by default because gateways backed by a shared API key would otherwise show every user every model the key can access. Discovered models are still filtered by an `availableModels` allowlist the session receives; deliver the list through MDM or a managed settings file, since server-managed delivery is not available on gateway configurations
