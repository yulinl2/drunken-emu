---
id: cmd.branch
kind: command
status: VERIFIED
title: "/branch"
sources: [S80]
---

# /branch

**Sources:** [S80](src.s80.md)

Create a branch of the current conversation at this point, so you can try a different direction without losing the conversation as it stands. Switches you into the branch and preserves the original, which you can return to with `/resume`. To run a copy as a separate background session instead of switching into it, use `/fork`; to hand a side task to a subagent that reports back into this conversation, use `/subtask`
