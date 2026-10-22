---
id: feature.control-the-model-users-run-on
kind: feature
status: VERIFIED
title: "Control the model users run on"
sources: [S70]
---

# Control the model users run on

**Sources:** [S70](src.s70.md)

The `model` setting is an initial selection, not enforcement. It sets which model is active when a session starts, but users can still open `/model` and pick Default, which resolves to the system's runtime default regardless of what `model` is set to, unless `enforceAvailableModels` or the keys that block specific versions apply to it.
