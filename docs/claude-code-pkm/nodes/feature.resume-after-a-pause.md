---
id: feature.resume-after-a-pause
kind: feature
status: VERIFIED
title: "Resume after a pause"
sources: [S29]
---

# Resume after a pause

**Sources:** [S29](src.s29.md)

Resume a paused run from `/workflows` by selecting it and pressing `p`. For a run you stopped, ask Claude to relaunch the workflow with the same script. If agents from the stopped run haven't exited yet, Claude Code refuses the relaunch until they have, so a second copy of those agents can't run alongside them.
