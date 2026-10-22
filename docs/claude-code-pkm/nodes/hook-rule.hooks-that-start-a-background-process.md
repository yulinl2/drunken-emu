---
id: hook-rule.hooks-that-start-a-background-process
kind: hook-rule
status: VERIFIED
title: "Hooks that start a background process"
sources: [S85]
---

# Hooks that start a background process

**Sources:** [S85](src.s85.md)

If your command hook makes its decision in a background process and exits, a deny that process prints after Claude Code has stopped reading doesn't block the tool call. For a hook that isn't async, Claude Code finishes reading the hook's output shortly after the hook's own process exits.
