---
id: feature.when-a-run-hits-your-usage-limit
kind: feature
status: VERIFIED
title: "When a run hits your usage limit"
sources: [S29]
---

# When a run hits your usage limit

**Sources:** [S29](src.s29.md)

When an agent hits your claude.ai usage limit, the run pauses rather than failing that agent: the agents that hit the limit wait for the reset, and no new agents start. Shortly after the limit resets, the waiting agents run again and the run continues on its own. Requires Claude Code v2.1.271 or later; on earlier versions, the affected agents fail.
