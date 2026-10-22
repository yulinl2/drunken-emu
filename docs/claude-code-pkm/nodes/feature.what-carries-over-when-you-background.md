---
id: feature.what-carries-over-when-you-background
kind: feature
status: VERIFIED
title: "What carries over when you background"
sources: [S26]
---

# What carries over when you background

**Sources:** [S26](src.s26.md)

Backgrounding starts a fresh process that resumes from the saved conversation, and in-flight background work moves to it. Running background shell commands, backgrounded subagents, dynamic workflows, scheduled tasks you created with `/loop`, and Claude's automatic replies to artifact comments all carry over and keep running there. A subagent moves together with everything it started, so it carries
