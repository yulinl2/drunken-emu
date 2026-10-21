---
id: hook-field.json-that-can-t-be-parsed-or-fails-schema-validation
kind: hook-field
status: VERIFIED
title: "JSON that can't be parsed or fails schema validation"
sources: [S85]
---

# JSON that can't be parsed or fails schema validation

**Sources:** [S85](src.s85.md)

exit 0: Non-blocking error. The notice carries the parse or validation message; exit 2: Blocking error. Your stderr is the reason; any other exit code: Non-blocking error. The notice carries the parse or validation message
