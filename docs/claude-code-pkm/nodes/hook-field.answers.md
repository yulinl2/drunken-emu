---
id: hook-field.answers
kind: hook-field
status: VERIFIED
title: "answers"
sources: [S85]
---

# answers

**Sources:** [S85](src.s85.md)

Optional. Maps question text to the selected option label. Multi-select answers join labels with commas. Claude doesn't set this field; supply it via `updatedInput` to answer programmatically (type: object; example: `{"Which framework?": "React"}`)
