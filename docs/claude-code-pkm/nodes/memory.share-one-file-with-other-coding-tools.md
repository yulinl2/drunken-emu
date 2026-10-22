---
id: memory.share-one-file-with-other-coding-tools
kind: memory
status: VERIFIED
title: "Share one file with other coding tools"
sources: [S19]
---

# Share one file with other coding tools

**Sources:** [S19](src.s19.md)

When Claude isn't reading your `AGENTS.md` directly, you can still keep it as the one file every tool shares by putting an `@AGENTS.md` import in a `CLAUDE.md` next to it. Do this when your project also has a `CLAUDE.md`, when you've set Project instructions to `claude-md`, or in sessions that can't load `AGENTS.md`. Add any Claude-specific instructions below the import, and Claude reads the impor
