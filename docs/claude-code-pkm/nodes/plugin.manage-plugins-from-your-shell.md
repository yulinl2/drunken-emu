---
id: plugin.manage-plugins-from-your-shell
kind: plugin
status: VERIFIED
title: "Manage plugins from your shell"
sources: [S42]
---

# Manage plugins from your shell

**Sources:** [S42](src.s42.md)

You can also manage plugins without starting a Claude Code session. In your shell, run `claude plugin install`, `enable`, `disable`, or `uninstall` as ordinary terminal commands; they change the same settings the `/plugin` panel does. Each takes `--scope` to target one scope, and uses a default scope when you omit it:
