---
id: feature.common-boundaries
kind: feature
status: VERIFIED
title: "Common boundaries"
sources: [S64]
---

# Common boundaries

**Sources:** [S64](src.s64.md)

Auto mode allows pushes to any branch of the repository you're working in, including the default branch, and pull request creation by default. A non-default branch whose name marks it as a deploy or publication target, such as `production`, `release`, or `gh-pages`, isn't covered by that default: the classifier judges a push there on its own terms, including as a production deploy. The push's cont
