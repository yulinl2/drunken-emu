---
id: feature.check-what-triggered-fallback
kind: feature
status: VERIFIED
title: "Check what triggered fallback"
sources: [S70]
---

# Check what triggered fallback

**Sources:** [S70](src.s70.md)

Fallback can trigger on the first request of a session, before you send anything unusual, because the first request carries workspace context such as your CLAUDE.md content and git status. A repository that contains security or biology material can trip the classifier on that context alone.
