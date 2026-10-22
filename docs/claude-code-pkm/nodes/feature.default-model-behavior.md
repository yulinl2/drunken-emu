---
id: feature.default-model-behavior
kind: feature
status: VERIFIED
title: "Default model behavior"
sources: [S70]
---

# Default model behavior

**Sources:** [S70](src.s70.md)

With the default prefix matching, `availableModels` on its own leaves the Default option on the system's runtime default for the account until you also set `enforceAvailableModels`. If that default is a model you intend to restrict, set `enforceAvailableModels` as well, or block that model.
