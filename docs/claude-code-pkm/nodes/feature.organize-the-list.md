---
id: feature.organize-the-list
kind: feature
status: VERIFIED
title: "Organize the list"
sources: [S26]
---

# Organize the list

**Sources:** [S26](src.s26.md)

Agent view groups sessions so the ones that need input are at the top, with `Ready for review` and `Needs input` above `Working` and `Completed`. These group names don't map one-to-one to the states above: a session moves to `Ready for review` when it has an open pull request that needs review or has failing checks, and `Completed` collects finished, failed, and stopped sessions together.
