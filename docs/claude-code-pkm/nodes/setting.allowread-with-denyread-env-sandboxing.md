---
id: setting.allowread-with-denyread-env-sandboxing
kind: setting
status: VERIFIED
title: "\"allowRead\": [\"~/\"] with \"denyRead\": [\"~//.env\"]"
sources: [S68]
---

# "allowRead": ["~/"] with "denyRead": ["~//.env"]

**Sources:** [S68](src.s68.md)

result: Every `.env` under the home directory stays blocked and the rest is readable. A wildcard deny holds inside a wider allow the same way an exact path does
