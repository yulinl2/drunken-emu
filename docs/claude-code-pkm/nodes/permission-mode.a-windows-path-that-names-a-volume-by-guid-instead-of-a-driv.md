---
id: permission-mode.a-windows-path-that-names-a-volume-by-guid-instead-of-a-driv
kind: permission-mode
status: VERIFIED
title: "A Windows path that names a volume by GUID instead of a drive letter"
sources: [S67]
---

# A Windows path that names a volume by GUID instead of a drive letter

**Sources:** [S67](src.s67.md)

example: `rm -rf '\\?\Volume{GUID}\work\build'`; why it counts: The path doesn't say which drive it's on, so it could be a critical path. Requires Claude Code v2.1.292 or later
