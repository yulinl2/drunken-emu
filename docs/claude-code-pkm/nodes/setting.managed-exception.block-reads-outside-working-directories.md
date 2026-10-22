---
id: setting.managed-exception.block-reads-outside-working-directories
kind: setting
status: VERIFIED
title: "Managed exception: blockReadsOutsideWorkingDirectories"
sources: [S3]
---

# Managed exception: blockReadsOutsideWorkingDirectories

**Sources:** [S3](src.s3.md)

permissions.blockReadsOutsideWorkingDirectories: true from any scope is honored, even when a managed source sets false. Requires v2.1.257 or later.
