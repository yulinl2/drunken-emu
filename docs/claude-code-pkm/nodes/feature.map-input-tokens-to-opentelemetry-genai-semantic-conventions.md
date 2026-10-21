---
id: feature.map-input-tokens-to-opentelemetry-genai-semantic-conventions
kind: feature
status: VERIFIED
title: "Map input tokens to OpenTelemetry GenAI semantic conventions"
sources: [S65]
---

# Map input tokens to OpenTelemetry GenAI semantic conventions

**Sources:** [S65](src.s65.md)

Claude Code exports input token counts as they appear in the API response's usage block, so these values exclude tokens read from or written to the prompt cache:
