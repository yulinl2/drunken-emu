---
id: setting.allowread-with-denyread-env
kind: setting
status: VERIFIED
title: "\"allowRead\": [\"~/\"] with \"denyRead\": [\"~/.env\"]"
sources: [S68]
---

# "allowRead": ["~/"] with "denyRead": ["~/.env"]

**Sources:** [S68](src.s68.md)

result: `~/.env` stays blocked and the rest of the home directory is readable. The deny holds inside a wider allow, so a broad allow can't silently re-expose a secret
