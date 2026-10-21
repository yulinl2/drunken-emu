---
id: permission-rule.what-runs-before-you-trust-a-folder
kind: permission-rule
status: VERIFIED
title: "What runs before you trust a folder"
sources: [S66]
---

# What runs before you trust a folder

**Sources:** [S66](src.s66.md)

Each row is one kind of content a repository can supply. The columns are the two situations in which you haven't trusted the folder itself: you trusted only a parent folder, or you ran `claude -p` or the SDK there, which never shows the trust dialog. The parent-folder column doesn't apply inside a nested repository: in an interactive session Claude Code shows the trust dialog for it, and a `claude
