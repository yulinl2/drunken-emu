---
id: plugin.understand-how-plugin-relevance-works
kind: plugin
status: VERIFIED
title: "Understand how plugin relevance works"
sources: [S60]
---

# Understand how plugin relevance works

**Sources:** [S60](src.s60.md)

Each plugin entry in `marketplace.json` can include a `relevance` object. The object names a topic and one or more signals. A signal is a pattern that Claude Code tests against the current session, such as the working directory or files Claude has read.
