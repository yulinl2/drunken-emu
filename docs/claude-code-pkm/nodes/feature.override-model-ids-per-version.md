---
id: feature.override-model-ids-per-version
kind: feature
status: VERIFIED
title: "Override model IDs per version"
sources: [S70]
---

# Override model IDs per version

**Sources:** [S70](src.s70.md)

On platforms that embed Claude Code and set `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST`, the host's model configuration takes precedence over managed model settings, while a managed `availableModels` allowlist stays in force unless the host supplies its own; Exceptions to managed settings precedence says which keys and variables the host overrides.
