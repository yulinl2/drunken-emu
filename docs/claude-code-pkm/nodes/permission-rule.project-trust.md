---
id: permission-rule.project-trust
kind: permission-rule
status: VERIFIED
title: "Project trust for allow rules"
sources: [S3]
---

# Project trust for allow rules

**Sources:** [S3](src.s3.md)

Allow rules in project files (permissions.allow, permissions.additionalDirectories, extraKnownMarketplaces and most env values) apply only after each user trusts the folder. Until then the user still sees prompts.

## Linked from

- [Allow, ask and deny lists](permission-rule.allow-ask-deny-lists.md)
