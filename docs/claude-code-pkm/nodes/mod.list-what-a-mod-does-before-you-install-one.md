---
id: mod.list-what-a-mod-does-before-you-install-one
kind: mod
status: VERIFIED
title: "List what a mod does before you install one"
sources: [S53]
---

# List what a mod does before you install one

**Sources:** [S53](src.s53.md)

Before you install a mod, you can list which events it handles and what it asks Claude Code to do, such as read a file or make a network request, without running it. Get the plugin's files first, for example by cloning its repository. Then, in your shell, run `claude plugin validate` on the plugin's directory:
