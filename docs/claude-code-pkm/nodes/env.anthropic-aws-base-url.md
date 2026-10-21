---
id: env.anthropic-aws-base-url
kind: env
status: VERIFIED
title: "ANTHROPIC_AWS_BASE_URL"
sources: [S81]
---

# ANTHROPIC_AWS_BASE_URL

**Sources:** [S81](src.s81.md)

Override the Claude Platform on AWS endpoint URL. Use for custom regions or when routing through an LLM gateway. Defaults to `https://aws-external-anthropic.{region}.api.aws`. Claude Code resolves the region with the same precedence as on Amazon Bedrock
