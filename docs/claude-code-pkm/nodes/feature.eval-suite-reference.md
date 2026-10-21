---
id: feature.eval-suite-reference
kind: feature
status: VERIFIED
title: "Eval suite reference"
sources: [S47]
---

# Eval suite reference

**Sources:** [S47](src.s47.md)

Everything an eval suite can contain lives under the plugin's eval directory, `evals/` unless you configured another. A directory counts as a case when it holds a `prompt.md` or a `case.yaml`, and a case without at least one grader fails to load with an `invalid case.yaml` error that names `graders`. This tree shows every file `claude plugin eval` reads or writes in the eval directory:
