---
id: feature.organization-effort-limits
kind: feature
status: VERIFIED
title: "Organization effort limits"
sources: [S70]
---

# Organization effort limits

**Sources:** [S70](src.s70.md)

Your organization can cap the effort level in two ways. On a Claude Enterprise plan, organization admins set per-role effort limits, described below. On any plan and any provider, including Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry, the `maxEffortLevel` managed setting caps effort on the client instead. When both apply to a model, the lower cap applies.
