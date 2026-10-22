---
id: setting.managed-exception.cross-session-inbound
kind: setting
status: VERIFIED
title: "Managed exception: crossSessionInbound"
sources: [S3]
---

# Managed exception: crossSessionInbound

**Sources:** [S3](src.s3.md)

A stricter value from project or local settings is honored over managed, --settings and user values. The ladder is accept, then hold, then refuse. A project or local value that is not stricter is ignored.
