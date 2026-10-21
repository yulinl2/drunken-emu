---
id: setting.managed-exception.enable-artifact
kind: setting
status: VERIFIED
title: "Managed exception: enableArtifact"
sources: [S3]
---

# Managed exception: enableArtifact

**Sources:** [S3](src.s3.md)

enableArtifact: false, and disableArtifact: true, from any scope are honored even when a managed source sets true. Nothing turns the Artifact tool back on. Requires v2.1.242 or later.
