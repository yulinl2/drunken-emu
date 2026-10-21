---
id: feature.a-session-is-slow-to-respond-after-attaching
kind: feature
status: VERIFIED
title: "A session is slow to respond after attaching"
sources: [S26]
---

# A session is slow to respond after attaching

**Sources:** [S26](src.s26.md)

When a session that has finished or is waiting for your next message stays unattached for about an hour, the supervisor stops its process to free resources. Attaching starts a fresh process from where it left off and switches to the session immediately while the process restarts. Sessions that are working, paused on a permission prompt or other dialog, or pinned aren't stopped this way, so pin a s
