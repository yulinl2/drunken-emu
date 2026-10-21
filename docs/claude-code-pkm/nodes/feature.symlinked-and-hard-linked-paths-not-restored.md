---
id: feature.symlinked-and-hard-linked-paths-not-restored
kind: feature
status: VERIFIED
title: "Symlinked and hard-linked paths not restored"
sources: [S84]
---

# Symlinked and hard-linked paths not restored

**Sources:** [S84](src.s84.md)

Checkpointing doesn't rewind symlinked or hard-linked files. When you pick Restore code or Restore code and conversation from the `/rewind` menu, Claude Code skips any tracked path that is a symlink or hard link and shows a `Restored the code, but skipped N files` warning. The skipped files keep their current contents. To undo the session's changes to one of them, ask Claude to reverse the edit or
