---
id: plugin-field.github-plugins-marketplace-reference-2
kind: plugin-field
status: VERIFIED
title: "github"
sources: [S51]
---

# github

**Sources:** [S51](src.s51.md)

fields: `repo`, `ref`, `path`, `sparsePaths`; `marketplace add` input: `owner/repo`, `owner/repo@ref`, or `owner/repo#ref`; `extraknownmarketplaces`: Loads; `strictknownmarketplaces`: Allows the same `repo`, `ref`, and `path`. `repo` may be `owner/*`; `blockedmarketplaces`: Blocks the same, and a `git` URL to the same repository
