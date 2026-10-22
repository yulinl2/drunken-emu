---
id: feature.configure-tmux
kind: feature
status: VERIFIED
title: "Configure tmux"
sources: [S74]
---

# Configure tmux

**Sources:** [S74](src.s74.md)

When Claude Code runs inside tmux, by default Shift+Enter submits instead of inserting a newline, and desktop notifications and the progress bar never reach the outer terminal. Add these lines to `~/.tmux.conf`, then run `tmux source-file ~/.tmux.conf` to apply them to the running server:
