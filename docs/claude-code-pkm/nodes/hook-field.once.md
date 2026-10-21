---
id: hook-field.once
kind: hook-field
status: VERIFIED
title: "once"
sources: [S85]
---

# once

**Sources:** [S85](src.s85.md)

If `true`, Claude Code removes the hook after its first successful run. A run that fails, blocks with exit code 2, or times out leaves the hook in place, so it runs again on the next matching event. Only honored for hooks declared in skill frontmatter; ignored in settings files and agent frontmatter (required: no)
