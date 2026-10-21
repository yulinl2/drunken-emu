---
id: env.claude-code-tmux-truecolor
kind: env
status: VERIFIED
title: "CLAUDE_CODE_TMUX_TRUECOLOR"
sources: [S81]
---

# CLAUDE_CODE_TMUX_TRUECOLOR

**Sources:** [S81](src.s81.md)

Set to any non-empty value, such as `1`, to allow 24-bit truecolor output inside tmux. Setting it to `0` or `false` still allows truecolor, unlike most on/off variables; unset the variable to restore the 256-color clamp. By default, Claude Code clamps to 256 colors when `$TMUX` is set because tmux does not pass through truecolor escape sequences unless configured to. Set this after adding `set -ga terminal-overrides ',*:Tc'` to your `~/.tmux.conf`. See Terminal configuration for other tmux settings
