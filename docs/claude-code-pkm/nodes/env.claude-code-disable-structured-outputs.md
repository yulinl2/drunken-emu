---
id: env.claude-code-disable-structured-outputs
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS

**Sources:** [S81](src.s81.md)

Set to `1` to stop Claude Code from sending the structured-output `output_config.format` field and the `anthropic-beta` value that pairs with it, for an LLM gateway whose upstream rejects them. This leaves on the other pre-release capabilities that `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` turns off. Requires Claude Code v2.1.288 or later
