---
id: feature.how-the-cache-is-organized
kind: feature
status: VERIFIED
title: "How the cache is organized"
sources: [S18]
---

# How the cache is organized

**Sources:** [S18](src.s18.md)

Each time you send a message in Claude Code, it makes a new API request. The model doesn't remember anything between requests, so Claude Code re-sends the full context: the system prompt, your project context, every prior message and tool result, and your new message. New content is appended at the end, which means most of each request is identical to the one before it. Prompt caching is how the A
