---
id: env.anthropic-betas
kind: env
status: VERIFIED
title: "ANTHROPIC_BETAS"
sources: [S81]
---

# ANTHROPIC_BETAS

**Sources:** [S81](src.s81.md)

Comma-separated list of additional `anthropic-beta` header values to include in API requests. Claude Code already sends the beta headers it needs; use this to opt into an Anthropic API beta before Claude Code adds native support. Unlike the `--betas` flag, which requires API key authentication, this variable works with all auth methods including Claude.ai subscription
