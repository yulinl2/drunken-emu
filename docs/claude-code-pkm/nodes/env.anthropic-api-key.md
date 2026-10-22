---
id: env.anthropic-api-key
kind: env
status: VERIFIED
title: "ANTHROPIC_API_KEY"
sources: [S81]
---

# ANTHROPIC_API_KEY

**Sources:** [S81](src.s81.md)

API key sent as `X-Api-Key` header. When set, this key is used instead of your Claude Pro, Max, Team, or Enterprise subscription even if you are logged in. In non-interactive mode (`-p`), the key is always used when present. In interactive mode, you are prompted to approve the key once before it overrides your subscription. To use your subscription instead, run `unset ANTHROPIC_API_KEY`
