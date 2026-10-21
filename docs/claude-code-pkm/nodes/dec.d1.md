---
id: dec.d1
kind: decision
status: DECIDED
title: "D1: Location in docs/ on the designated branch"
sources: [S8, S9]
---

# D1: Location in docs/ on the designated branch

**Sources:** [S8](src.s8.md), [S9](src.s9.md)

The notes live under docs/ on claude/code-tools-features-pkm-et02vp. Reasons: the session designates the branch ([S8: This session's system prompt and injected context](src.s8.md)), the Claude app can open files under the working directory, and docs/ is flat by convention ([S9: Repository files](src.s9.md)). Reverse by moving the files and regenerating docs/TREE.md ([Build the node set](process.build.md)).
