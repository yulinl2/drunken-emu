---
id: feature.how-isolation-relates-to-permission-modes
kind: feature
status: VERIFIED
title: "How isolation relates to permission modes"
sources: [S69]
---

# How isolation relates to permission modes

**Sources:** [S69](src.s69.md)

Permission modes decide whether a tool call runs and whether you are prompted first. Isolation restricts what a command can access once it runs. The two work together: when a permission mode lets actions run without asking you, an isolation boundary limits what those actions can reach.
