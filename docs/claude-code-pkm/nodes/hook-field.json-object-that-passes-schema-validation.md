---
id: hook-field.json-object-that-passes-schema-validation
kind: hook-field
status: VERIFIED
title: "JSON object that passes schema validation"
sources: [S85]
---

# JSON object that passes schema validation

**Sources:** [S85](src.s85.md)

exit 0: Success. The fields apply; exit 2: Blocking error. Claude Code still reads the fields, but they can't override the block; any other exit code: Success. Claude Code ignores the exit code, and the fields alone decide. For hooks whose failure blocks the action, the run counts as a failure instead
