---
id: env.anthropic-foundry-auth-token
kind: env
status: VERIFIED
title: "ANTHROPIC_FOUNDRY_AUTH_TOKEN"
sources: [S81]
---

# ANTHROPIC_FOUNDRY_AUTH_TOKEN

**Sources:** [S81](src.s81.md)

Bearer token for Microsoft Foundry authentication, such as a Microsoft Entra access token. Claude Code sends it as the `Authorization: Bearer` header. Takes precedence over `ANTHROPIC_FOUNDRY_API_KEY` and over the Azure default credential chain. See Microsoft Foundry. Requires Claude Code v2.1.203 or later
