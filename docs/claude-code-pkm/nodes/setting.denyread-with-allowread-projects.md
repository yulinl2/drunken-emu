---
id: setting.denyread-with-allowread-projects
kind: setting
status: VERIFIED
title: "\"denyRead\": [\"~/\"] with \"allowRead\": [\"~/projects\"]"
sources: [S68]
---

# "denyRead": ["~/"] with "allowRead": ["~/projects"]

**Sources:** [S68](src.s68.md)

result: `~/projects` is readable and the rest of the home directory stays blocked. The narrower allow re-opens that part of the denied region
