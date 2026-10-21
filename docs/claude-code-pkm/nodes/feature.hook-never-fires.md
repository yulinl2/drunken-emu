---
id: feature.hook-never-fires
kind: feature
status: VERIFIED
title: "Hook never fires"
sources: [S40]
---

# Hook never fires

**Sources:** [S40](src.s40.md)

cause: `matcher` is a JSON array instead of a string; fix: Use a single string with `/` to match multiple tools, for example `"Edit/Write"`. See matcher patterns.
