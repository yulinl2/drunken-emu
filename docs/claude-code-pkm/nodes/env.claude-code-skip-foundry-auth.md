---
id: env.claude-code-skip-foundry-auth
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SKIP_FOUNDRY_AUTH"
sources: [S81]
---

# CLAUDE_CODE_SKIP_FOUNDRY_AUTH

**Sources:** [S81](src.s81.md)

Skip Azure authentication for Microsoft Foundry, for a proxy or gateway that injects its own `Authorization` header. Claude Code sends requests without an Azure credential and preserves the `Authorization` header you supply, for example through `ANTHROPIC_CUSTOM_HEADERS`. Ignored when `ANTHROPIC_FOUNDRY_API_KEY` or `ANTHROPIC_FOUNDRY_AUTH_TOKEN` is set. Before v2.1.203, this variable left the Microsoft Foundry client unable to send requests unless an API key was also set
