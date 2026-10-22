---
id: feature.sessions-show-as-failed-or-stopped-after-shutdown
kind: feature
status: VERIFIED
title: "Sessions show as failed or stopped after shutdown"
sources: [S26]
---

# Sessions show as failed or stopped after shutdown

**Sources:** [S26](src.s26.md)

Shutting down or restarting your machine stops running background sessions. A session that was waiting on your input stays under `Needs input` when you come back. For any other running session, what agent view shows depends on how long ago it last made progress:
