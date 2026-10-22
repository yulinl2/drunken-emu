---
id: setting.keys-read-from-the-highest-ranked-source-only
kind: setting
status: VERIFIED
title: "Keys read from the highest-ranked source only"
sources: [S61]
---

# Keys read from the highest-ranked source only

**Sources:** [S61](src.s61.md)

how claude code combines it: Ignores the key in every lower source, even when the highest-ranked source leaves it unset; examples: Credential helpers such as `apiKeyHelper`, login pins such as `forceLoginOrgUUID`, `modelPicker`, `permissions.defaultMode`
