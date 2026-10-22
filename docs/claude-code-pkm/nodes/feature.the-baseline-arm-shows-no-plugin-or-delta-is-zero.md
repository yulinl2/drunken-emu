---
id: feature.the-baseline-arm-shows-no-plugin-or-delta-is-zero
kind: feature
status: VERIFIED
title: "The baseline arm shows no plugin, or delta is zero"
sources: [S47]
---

# The baseline arm shows no plugin, or delta is zero

**Sources:** [S47](src.s47.md)

If the summary has no `W/OUT` column, or a case fails with "ablation requested but no plugin resolved", the usual cause is that no plugin was found for the case. If every case resumes a transcript through `context.history_file`, the missing column is expected instead, because those cases run one arm by default. Otherwise, add `plugins: ["../.."]` to the case, giving the path from the case director
