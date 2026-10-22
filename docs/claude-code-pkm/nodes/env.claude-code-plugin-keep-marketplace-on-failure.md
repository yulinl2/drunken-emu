---
id: env.claude-code-plugin-keep-marketplace-on-failure
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE"
sources: [S81]
---

# CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE

**Sources:** [S81](src.s81.md)

Set to `1` to skip the re-clone attempt and keep using the existing marketplace checkout when a marketplace refresh can't reach or authenticate to the remote. Useful in offline or airgapped environments where re-cloning would fail the same way. See Marketplace updates fail in offline environments
