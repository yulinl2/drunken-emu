---
id: env.claude-code-max-turns
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MAX_TURNS"
sources: [S81]
---

# CLAUDE_CODE_MAX_TURNS

**Sources:** [S81](src.s81.md)

Cap the number of agentic turns when no explicit limit is passed. Equivalent to passing `--max-turns`, which takes precedence when both are set. A value that is not a positive integer is rejected at startup with an error rather than treated as no cap
