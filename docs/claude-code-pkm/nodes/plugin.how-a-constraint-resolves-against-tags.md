---
id: plugin.how-a-constraint-resolves-against-tags
kind: plugin
status: VERIFIED
title: "How a constraint resolves against tags"
sources: [S46]
---

# How a constraint resolves against tags

**Sources:** [S46](src.s46.md)

When a user installs a plugin that declares `{ "name": "secrets-vault", "version": "~2.1.0" }`, the dependency installs from the highest `secrets-vault--v` tag that satisfies `~2.1.0` on the repository that hosts `secrets-vault`. When no tag satisfies the range, the install either fails or uses the marketplace's current copy:
