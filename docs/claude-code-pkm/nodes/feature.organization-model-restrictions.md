---
id: feature.organization-model-restrictions
kind: feature
status: VERIFIED
title: "Organization model restrictions"
sources: [S70]
---

# Organization model restrictions

**Sources:** [S70](src.s70.md)

Organization admins on Claude Enterprise plans restrict which models members can run by disabling individual models in the claude.ai admin console. This restriction is delivered with the account's entitlements when Claude Code authenticates, separate from any `availableModels` list in settings, and the server enforces the same restriction independently when a session is created. Requires Claude Co
