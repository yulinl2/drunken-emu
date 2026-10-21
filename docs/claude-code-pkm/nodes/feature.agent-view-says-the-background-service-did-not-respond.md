---
id: feature.agent-view-says-the-background-service-did-not-respond
kind: feature
status: VERIFIED
title: "Agent view says the background service did not respond"
sources: [S26]
---

# Agent view says the background service did not respond

**Sources:** [S26](src.s26.md)

If attaching, peeking, or `claude logs` reports that the background service did not respond, the supervisor process has likely stalled. Stop it and let the next `claude agents` start a fresh one. To keep your background sessions running through the restart, pass `--keep-workers`:
