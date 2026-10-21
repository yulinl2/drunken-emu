---
id: env.claude-code-gateway-model-discovery-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_GATEWAY_MODEL_DISCOVERY_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_CODE_GATEWAY_MODEL_DISCOVERY_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Timeout in milliseconds for the gateway model discovery request that `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY` turns on (default: `3000`). Raise it when your gateway needs longer than three seconds to answer `/v1/models` at startup. Takes plain digits only; `0`, negative values, and other spellings keep the default. Requires Claude Code v2.1.269 or later
