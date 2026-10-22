---
id: feature.editing-files-in-your-repository
kind: feature
status: VERIFIED
title: "Editing files in your repository"
sources: [S18]
---

# Editing files in your repository

**Sources:** [S18](src.s18.md)

File contents enter context only when Claude reads them, and reads append to the conversation. Editing a file Claude previously read does not retroactively change the earlier read in history. Instead, Claude Code appends a `` noting the file changed, and Claude re-reads it if needed.
