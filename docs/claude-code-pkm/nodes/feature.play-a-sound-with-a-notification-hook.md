---
id: feature.play-a-sound-with-a-notification-hook
kind: feature
status: VERIFIED
title: "Play a sound with a Notification hook"
sources: [S74]
---

# Play a sound with a Notification hook

**Sources:** [S74](src.s74.md)

In any terminal you can configure a Notification hook to play a sound or run a custom command when Claude needs your attention. Hooks run alongside the built-in notification rather than replacing it, so terminals that do not receive a desktop notification, such as Warp or the VS Code integrated terminal, can use a hook or set `preferredNotifChannel` to `"terminal_bell"` instead.
