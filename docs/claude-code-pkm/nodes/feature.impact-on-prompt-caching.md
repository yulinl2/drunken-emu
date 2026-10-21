---
id: feature.impact-on-prompt-caching
kind: feature
status: VERIFIED
title: "Impact on prompt caching"
sources: [S72]
---

# Impact on prompt caching

**Sources:** [S72](src.s72.md)

Enabling or disabling the advisor mid-session does not invalidate your main model's prompt cache. Unlike switching models, toggling `/advisor` keeps the cached prefix intact, and the advisor's returned guidance is cached as part of the transcript on later turns.
