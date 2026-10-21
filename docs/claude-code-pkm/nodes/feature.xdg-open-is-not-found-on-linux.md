---
id: feature.xdg-open-is-not-found-on-linux
kind: feature
status: VERIFIED
title: "xdg-open is not found on Linux"
sources: [S39]
---

# xdg-open is not found on Linux

**Sources:** [S39](src.s39.md)

The `xdg-open` command is part of the `xdg-utils` package, which minimal server images, containers, and WSL distributions often leave out. Install `xdg-utils` with your distribution's package manager, for example `sudo apt install xdg-utils`, then run the command again. If the command then runs but nothing opens, `xdg-open` may have no desktop environment to dispatch to; see Clicking the link does
