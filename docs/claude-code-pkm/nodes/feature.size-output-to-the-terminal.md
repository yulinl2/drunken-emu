---
id: feature.size-output-to-the-terminal
kind: feature
status: VERIFIED
title: "Size output to the terminal"
sources: [S78]
---

# Size output to the terminal

**Sources:** [S78](src.s78.md)

Claude Code captures your script's output instead of connecting it directly to the terminal, so `tput cols` and language-level width detection cannot read the terminal size from inside the script. Read the `COLUMNS` and `LINES` environment variables instead. Claude Code sets these to the current terminal dimensions before running your script.
