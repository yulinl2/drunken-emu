---
id: feature.copy-the-session-with-fork
kind: feature
status: VERIFIED
title: "Copy the session with /fork"
sources: [S26]
---

# Copy the session with /fork

**Sources:** [S26](src.s26.md)

Run `/fork` to copy the current conversation into a new background session while the original keeps running. The copy starts with everything in the conversation up to that point; see the bullets below for where the copy runs. It also carries over the model, permission mode, effort level, and any directories or "don't ask again" permission grants you added during the session. The copy appears as it
