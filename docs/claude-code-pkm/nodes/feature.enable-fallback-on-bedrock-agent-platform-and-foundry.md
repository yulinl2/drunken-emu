---
id: feature.enable-fallback-on-bedrock-agent-platform-and-foundry
kind: feature
status: VERIFIED
title: "Enable fallback on Bedrock, Agent Platform, and Foundry"
sources: [S70]
---

# Enable fallback on Bedrock, Agent Platform, and Foundry

**Sources:** [S70](src.s70.md)

On Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry, model IDs are provider-specific, so automatic fallback only operates when Claude Code can identify each model involved:
