---
id: feature.enable-option-key-shortcuts-on-macos
kind: feature
status: VERIFIED
title: "Enable Option key shortcuts on macOS"
sources: [S74]
---

# Enable Option key shortcuts on macOS

**Sources:** [S74](src.s74.md)

Some Claude Code shortcuts use the Option key, such as Option+Enter for a newline or Option+P to switch models. On macOS, most terminals do not send Option as a modifier by default, so these shortcuts do nothing until you enable it. The terminal setting for this is usually labeled "Use Option as Meta Key"; Meta is the historical Unix name for the key now labeled Option or Alt.
