---
id: feature.define-trusted-infrastructure
kind: feature
status: VERIFIED
title: "Define trusted infrastructure"
sources: [S64]
---

# Define trusted infrastructure

**Sources:** [S64](src.s64.md)

For most organizations, `autoMode.environment` is the only field you need to set. It tells the classifier which repos, buckets, and domains are trusted: the classifier uses it to decide what "external" means, so any destination not listed is a potential exfiltration target.
