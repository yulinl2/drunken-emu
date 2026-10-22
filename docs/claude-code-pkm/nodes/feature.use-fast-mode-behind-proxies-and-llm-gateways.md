---
id: feature.use-fast-mode-behind-proxies-and-llm-gateways
kind: feature
status: VERIFIED
title: "Use fast mode behind proxies and LLM gateways"
sources: [S71]
---

# Use fast mode behind proxies and LLM gateways

**Sources:** [S71](src.s71.md)

Before offering fast mode, Claude Code checks your organization's fast mode availability with a request directly to `api.anthropic.com`. The check doesn't follow `ANTHROPIC_BASE_URL`, so on a network that routes Claude traffic through an LLM gateway and blocks direct egress to `api.anthropic.com`, the check fails even though inference requests work. The check does use a configured HTTP proxy, so a
