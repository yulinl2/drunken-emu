---
id: feature.customize-the-default-prompt-with-loop-md
kind: feature
status: VERIFIED
title: "Customize the default prompt with loop.md"
sources: [S36]
---

# Customize the default prompt with loop.md

**Sources:** [S36](src.s36.md)

Create a `loop.md` file to replace the built-in maintenance prompt with your own instructions. It defines a single default prompt for bare `/loop`, not a list of separate scheduled tasks, and Claude Code ignores it whenever you supply a prompt on the command line. To schedule additional prompts alongside it, use `/loop ` or ask Claude directly.
