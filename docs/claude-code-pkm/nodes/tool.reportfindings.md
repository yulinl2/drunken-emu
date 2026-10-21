---
id: tool.reportfindings
kind: tool
status: VERIFIED
title: "ReportFindings"
sources: [S82]
---

# ReportFindings

**Sources:** [S82](src.s82.md)

Reports code-review findings as a structured list, with a file, summary, and failure scenario per finding, so Claude Code can render them instead of printing them as text. Claude calls it when active code-review instructions tell it to. A finding can also carry an optional `category` slug, such as `correctness` or `test-coverage`, shown next to the file location in the rendered list (permission required: No)
