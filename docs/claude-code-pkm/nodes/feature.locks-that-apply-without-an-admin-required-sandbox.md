---
id: feature.locks-that-apply-without-an-admin-required-sandbox
kind: feature
status: VERIFIED
title: "Locks that apply without an admin-required sandbox"
sources: [S68]
---

# Locks that apply without an admin-required sandbox

**Sources:** [S68](src.s68.md)

Some settings make Claude Code ignore the repository keys that directly override one restriction, even when the sandbox isn't admin-required. Each one has this effect only when you set it in a file its row names, and the repository's other sandbox settings still apply. Requires Claude Code v2.1.285 or later.
