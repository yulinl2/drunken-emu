---
id: feature.the-session-opens-in-my-home-directory-instead-of-the-repo
kind: feature
status: VERIFIED
title: "The session opens in my home directory instead of the repo"
sources: [S39]
---

# The session opens in my home directory instead of the repo

**Sources:** [S39](src.s39.md)

The `repo` parameter only resolves to clones Claude Code has already seen. Run `claude` inside the clone once so Claude Code records its path, or switch the link to use `cwd` with an absolute path.
