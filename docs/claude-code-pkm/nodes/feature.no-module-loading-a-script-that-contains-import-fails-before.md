---
id: feature.no-module-loading-a-script-that-contains-import-fails-before
kind: feature
status: VERIFIED
title: "No module loading: a script that contains import() fails before the run starts"
sources: [S29]
---

# No module loading: a script that contains import() fails before the run starts

**Sources:** [S29](src.s29.md)

why: The script body is plain JavaScript. Put work that needs a library in an agent's task
