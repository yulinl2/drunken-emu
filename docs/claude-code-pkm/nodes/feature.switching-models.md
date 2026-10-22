---
id: feature.switching-models
kind: feature
status: VERIFIED
title: "Switching models"
sources: [S18]
---

# Switching models

**Sources:** [S18](src.s18.md)

Each model has its own cache. Switching with `/model` means the next request reads the entire conversation history with no cache hits, even though the content is identical.
