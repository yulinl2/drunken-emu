---
id: feature.in-a-fan-out-agents-that-share-the-first-agent-s-prompt-cach
kind: feature
status: VERIFIED
title: "In a fan-out, agents that share the first agent's prompt-cache prefix start up to 5 seconds after it by default"
sources: [S29]
---

# In a fan-out, agents that share the first agent's prompt-cache prefix start up to 5 seconds after it by default

**Sources:** [S29](src.s29.md)

why: All but the first read the prefix the first agent cached instead of each processing it uncached
