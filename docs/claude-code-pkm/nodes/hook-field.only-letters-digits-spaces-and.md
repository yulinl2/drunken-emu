---
id: hook-field.only-letters-digits-spaces-and
kind: hook-field
status: VERIFIED
title: "Only letters, digits, _, -, spaces, ,, and /"
sources: [S85]
---

# Only letters, digits, _, -, spaces, ,, and /

**Sources:** [S85](src.s85.md)

evaluated as: Exact string, or list of exact strings separated by `/` or `,` with optional surrounding whitespace; example: `Bash` matches only the Bash tool; `Edit/Write` and `Edit, Write` each match either tool exactly; `code-reviewer` matches only that agent type
