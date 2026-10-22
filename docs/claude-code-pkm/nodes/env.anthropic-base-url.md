---
id: env.anthropic-base-url
kind: env
status: VERIFIED
title: "ANTHROPIC_BASE_URL"
sources: [S81]
---

# ANTHROPIC_BASE_URL

**Sources:** [S81](src.s81.md)

Override the API endpoint to route requests through a proxy or gateway. For what happens when that gateway rejects MCP tool search, see Tool search through an LLM gateway. As of v2.1.196, Remote Control is disabled when this points at a host other than `api.anthropic.com`, matching its behavior on Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry
