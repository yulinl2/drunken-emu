---
id: feature.where-transcripts-are-stored
kind: feature
status: VERIFIED
title: "Where transcripts are stored"
sources: [S20]
---

# Where transcripts are stored

**Sources:** [S20](src.s20.md)

By default, Claude Code stores transcripts as JSONL at `~/.claude/projects//.jsonl`, where `` is your working directory path with non-alphanumeric characters replaced by `-`. For a working directory whose converted name exceeds 200 characters, Claude Code truncates the name to 200 characters and appends a hash of the full path, so the directory name stays within filesystem limits.
