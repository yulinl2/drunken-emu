---
id: permission-rule.additional-directories-grant-file-access-not-configuration
kind: permission-rule
status: VERIFIED
title: "Additional directories grant file access, not configuration"
sources: [S66]
---

# Additional directories grant file access, not configuration

**Sources:** [S66](src.s66.md)

Adding a directory extends where Claude can read and edit files. It doesn't make that directory a full configuration root: most `.claude/` configuration is not discovered from additional directories, though a few types are loaded as exceptions.
