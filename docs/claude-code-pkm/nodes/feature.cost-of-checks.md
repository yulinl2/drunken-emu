---
id: feature.cost-of-checks
kind: feature
status: VERIFIED
title: "Cost of checks"
sources: [S83]
---

# Cost of checks

**Sources:** [S83](src.s83.md)

While the mod is on, checks are background requests to the same model your session is using, and they count toward your plan's usage limits or your API costs. Each check sends what's already in Claude's context, meaning the conversation so far with its tool results, followed by the mod's own instructions and the text of your recent notes. The conversation part is read from the session's prompt cac
