---
id: feature.disable-specific-subagents
kind: feature
status: VERIFIED
title: "Disable specific subagents"
sources: [S25]
---

# Disable specific subagents

**Sources:** [S25](src.s25.md)

You can prevent Claude from using specific subagents by adding them to the `deny` array in your settings. Use the format `Agent(subagent-name)` where `subagent-name` matches the subagent's name field.
