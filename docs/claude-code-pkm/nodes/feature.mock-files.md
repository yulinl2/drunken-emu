---
id: feature.mock-files
kind: feature
status: VERIFIED
title: "Mock files"
sources: [S47]
---

# Mock files

**Sources:** [S47](src.s47.md)

A `.md` file under `mocks//` answers one tool. Its body is the tool result, with `{{input.}}` and `{{file:fixtures/}}` substitutions. Its frontmatter accepts these keys:
