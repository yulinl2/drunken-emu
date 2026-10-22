---
id: tool.notebookedit-tool-behavior
kind: tool
status: VERIFIED
title: "NotebookEdit tool behavior"
sources: [S82]
---

# NotebookEdit tool behavior

**Sources:** [S82](src.s82.md)

NotebookEdit modifies a Jupyter notebook one cell at a time, targeting cells by their `cell_id`. It doesn't perform string replacement across the notebook the way Edit does on plain files.
