---
id: permission-rule.read-and-edit
kind: permission-rule
status: VERIFIED
title: "Read and Edit"
sources: [S66]
---

# Read and Edit

**Sources:** [S66](src.s66.md)

To block Claude's file tools from reading a file or directory, add a `Read` deny rule for its path, such as `Read(./.env)` or `Read(./secrets/)`; Exclude sensitive files has a paste-ready example. If your project has a `.claudeignore` file, it has no effect, so move its entries into `Read` deny rules.
