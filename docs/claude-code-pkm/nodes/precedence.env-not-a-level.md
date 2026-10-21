---
id: precedence.env-not-a-level
kind: precedence
status: VERIFIED
title: "Environment variables are not a level"
sources: [S3]
---

# Environment variables are not a level

**Sources:** [S3](src.s3.md)

Each variable and key pair has its own rule. For example, ANTHROPIC_MODEL in the shell applies over the model key from any file, while ANTHROPIC_DEFAULT_MODEL applies only when no file sets model. An env block inside a settings file is an ordinary key.

## Linked from

- [ANTHROPIC_MODEL](env.anthropic-model.md)
