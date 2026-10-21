---
id: env.claude-code-file-read-max-output-tokens
kind: env
status: VERIFIED
title: "CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS"
sources: [S81]
---

# CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS

**Sources:** [S81](src.s81.md)

Override the default token limit for file reads, which is 25,000 tokens. Useful when you need to read larger files in full. A read that Claude makes with the `allow_large` parameter can go past this limit when the context window has room
