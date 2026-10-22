---
id: mod.how-often-a-site-can-redraw
kind: mod
status: VERIFIED
title: "How often a site can redraw"
sources: [S57]
---

# How often a site can redraw

**Sources:** [S57](src.s57.md)

Claude Code throttles redraws of a site, so your mod can call `$.ui.invalidate` as often as its data changes. For how often each site can redraw, see the limits table.
