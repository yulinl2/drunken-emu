---
id: hook-field.reason-hooks-3
kind: hook-field
status: VERIFIED
title: "reason"
sources: [S85]
---

# reason

**Sources:** [S85](src.s85.md)

The denial reason. For a classifier verdict, in most sessions it names the matched rule in square brackets, such as `[Data Exfiltration]`; see Review denials for the other forms. For a no-verdict denial, it starts with `Auto mode could not evaluate this action and is blocking it for safety`. For a denial because the classifier model was unavailable, it is the fixed text `Classifier unavailable`
