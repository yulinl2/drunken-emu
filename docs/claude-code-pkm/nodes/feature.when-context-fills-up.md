---
id: feature.when-context-fills-up
kind: feature
status: VERIFIED
title: "When context fills up"
sources: [S14]
---

# When context fills up

**Sources:** [S14](src.s14.md)

Claude Code manages context automatically as you approach the limit. It clears older tool outputs first, then summarizes the conversation if needed. Your requests and key code snippets are preserved; detailed instructions from early in the conversation may be lost. Put persistent rules in CLAUDE.md rather than relying on conversation history.
