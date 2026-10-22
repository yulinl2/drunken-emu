---
id: plugin-field.plugin-x-sets-headers-headershelper-which-only-apply-to-arch
kind: plugin-field
status: VERIFIED
title: "Plugin \"x\" sets headers/headersHelper, which only apply to \"archive\" sources; they have no effect on this entry."
sources: [S51]
---

# Plugin "x" sets headers/headersHelper, which only apply to "archive" sources; they have no effect on this entry.

**Sources:** [S51](src.s51.md)

level: Warning; field: `plugins[i].headers` or `plugins[i].headersHelper`, on an entry whose `source` isn't `archive`
