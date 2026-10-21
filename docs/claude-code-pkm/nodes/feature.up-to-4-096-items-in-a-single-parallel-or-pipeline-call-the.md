---
id: feature.up-to-4-096-items-in-a-single-parallel-or-pipeline-call-the
kind: feature
status: VERIFIED
title: "Up to 4,096 items in a single parallel() or pipeline() call: the runtime rejects a longer list with an error"
sources: [S29]
---

# Up to 4,096 items in a single parallel() or pipeline() call: the runtime rejects a longer list with an error

**Sources:** [S29](src.s29.md)

why: A silent cap would drop part of the workload without telling the script
