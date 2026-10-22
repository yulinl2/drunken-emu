---
id: feature.write-and-refine-cases
kind: feature
status: VERIFIED
title: "Write and refine cases"
sources: [S47]
---

# Write and refine cases

**Sources:** [S47](src.s47.md)

The cases `claude plugin eval init` writes are plain files you can open, change, and add to. A case is a directory under the plugin's eval directory that contains a `prompt.md`, a `case.yaml`, or both. Give each case at least one grader, as a `graders/.md` file or a `graders:` entry in `case.yaml`, because a case without one fails to load. To group cases, nest them under a directory that isn't its
