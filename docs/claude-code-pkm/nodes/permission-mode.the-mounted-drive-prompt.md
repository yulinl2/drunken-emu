---
id: permission-mode.the-mounted-drive-prompt
kind: permission-mode
status: VERIFIED
title: "The mounted drive prompt"
sources: [S67]
---

# The mounted drive prompt

**Sources:** [S67](src.s67.md)

The mounted drive prompt appears on macOS, Linux, and WSL when a recursive `rm` targets a listed mounted drive path, such as `/mnt/c` or `/Volumes/USB/build`. Its reason reads `Dangerous rm operation on mounted drive path: `. A `/*` target gets the prompt without the recursive flag, since Claude Code reads `rm /Volumes/USB/build/*` as a removal of `/Volumes/USB/build`.
