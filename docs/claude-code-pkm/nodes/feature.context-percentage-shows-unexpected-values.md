---
id: feature.context-percentage-shows-unexpected-values
kind: feature
status: VERIFIED
title: "Context percentage shows unexpected values"
sources: [S78]
---

# Context percentage shows unexpected values

**Sources:** [S78](src.s78.md)

The status line reports the counts from the last API response, while `/context` adds an estimate for messages added since that response, so `/context` can read higher until the next response. Use `used_percentage` for the simplest accurate context state. For the formula behind `used_percentage`, see Context window fields.
