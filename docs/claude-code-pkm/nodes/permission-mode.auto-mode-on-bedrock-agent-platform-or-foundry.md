---
id: permission-mode.auto-mode-on-bedrock-agent-platform-or-foundry
kind: permission-mode
status: VERIFIED
title: "Auto mode on Bedrock, Agent Platform, or Foundry"
sources: [S67]
---

# Auto mode on Bedrock, Agent Platform, or Foundry

**Sources:** [S67](src.s67.md)

On Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, and signed-in Claude apps gateway sessions, auto mode is available by default. If you don't set a permission mode there, interactive sessions start in auto mode, and `claude -p` or Agent SDK runs start in Manual mode, whose config value is `default`:
