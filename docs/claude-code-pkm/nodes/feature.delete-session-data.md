---
id: feature.delete-session-data
kind: feature
status: VERIFIED
title: "Delete session data"
sources: [S20]
---

# Delete session data

**Sources:** [S20](src.s20.md)

Transcripts age out under the retention sweep rules. To delete a project's transcripts and related state sooner, run `claude purge`. If you delete a background session with `claude rm `, its transcript stays on disk and remains available through `claude --resume`.
