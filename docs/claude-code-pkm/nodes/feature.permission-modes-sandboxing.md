---
id: feature.permission-modes-sandboxing
kind: feature
status: VERIFIED
title: "Permission modes"
sources: [S68]
---

# Permission modes

**Sources:** [S68](src.s68.md)

`/sandbox` is not a permission mode. Permission modes decide whether a tool call runs and whether you are prompted first, while the sandbox restricts what a Bash command can access once it runs. They differ in what they control and what replaces the per-action prompt:
