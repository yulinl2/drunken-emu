---
id: plugin.unrecognized-fields
kind: plugin
status: VERIFIED
title: "Unrecognized fields"
sources: [S50]
---

# Unrecognized fields

**Sources:** [S50](src.s50.md)

An unrecognized top-level key is stripped, and an unrecognized key inside a `userConfig` option, `channels` entry, `lspServers` config, or `monitors` entry is rejected:
