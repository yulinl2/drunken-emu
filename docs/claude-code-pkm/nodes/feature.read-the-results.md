---
id: feature.read-the-results
kind: feature
status: VERIFIED
title: "Read the results"
sources: [S47]
---

# Read the results

**Sources:** [S47](src.s47.md)

Every run with at least one case writes a `results//` directory inside the eval directory, containing `aggregate-result.json` and `report.html`. For a path target that's under the plugin; for a plugin you named, it's under your current directory, as the target table shows. The summary table, the JSON, and the report all render the same result data.
