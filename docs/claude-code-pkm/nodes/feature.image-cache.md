---
id: feature.image-cache
kind: feature
status: VERIFIED
title: "image-cache//"
sources: [S16]
---

# image-cache//

**Sources:** [S16](src.s16.md)

contents: Attached images saved by Claude Code v2.1.274 and earlier. Later versions save pasted and attached images outside `~/.claude`, in an `images/` directory for each session under the temp directory that `CLAUDE_CODE_TMPDIR` controls. The sweep removes other sessions' leftover directories here, whatever their age.
