---
id: feature.keys-read-from-every-admin-source
kind: feature
status: VERIFIED
title: "Keys read from every admin source"
sources: [S61]
---

# Keys read from every admin source

**Sources:** [S61](src.s61.md)

Under the default `"first-wins"` setting, Claude Code reads most keys only from the source it selected, and ignores a value in a lower-ranked source even when the selected source leaves that key unset.
