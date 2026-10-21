---
id: setting.cloud-repo-file-read
kind: setting
status: VERIFIED
title: "Cloud sessions: repo settings read"
sources: [S3]
---

# Cloud sessions: repo settings read

**Sources:** [S3](src.s3.md)

In a single-repository cloud session, the repo's .claude/settings.json is read, because the file is part of the clone. In multi-repository Anthropic-hosted sessions, only enabledPlugins and extraKnownMarketplaces are read from each repo's file.

## Linked from

- [Cloud environments](feature.cloud-environments.md)
