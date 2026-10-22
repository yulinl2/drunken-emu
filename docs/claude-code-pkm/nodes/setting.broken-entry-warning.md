---
id: setting.broken-entry-warning
kind: setting
status: VERIFIED
title: "Broken entry: Settings Warning"
sources: [S3]
---

# Broken entry: Settings Warning

**Sources:** [S3](src.s3.md)

Individual entries that fail, such as a malformed permission rule or an unknown hook event name, trigger a Settings Warning. Claude Code skips those values and keeps the rest of the file.
