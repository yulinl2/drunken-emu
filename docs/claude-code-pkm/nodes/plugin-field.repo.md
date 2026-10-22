---
id: plugin-field.repo
kind: plugin-field
status: VERIFIED
title: "repo"
sources: [S51]
---

# repo

**Sources:** [S51](src.s51.md)

In `marketplace add` and `extraKnownMarketplaces`, `repo` must name one repository. `marketplace add` rejects `owner/*` as not a valid `owner/repo` shorthand; in `extraKnownMarketplaces` Claude Code takes it literally and the clone fails (types: `github`)
