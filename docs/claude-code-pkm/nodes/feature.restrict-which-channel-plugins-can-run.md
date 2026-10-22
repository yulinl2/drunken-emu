---
id: feature.restrict-which-channel-plugins-can-run
kind: feature
status: VERIFIED
title: "Restrict which channel plugins can run"
sources: [S34]
---

# Restrict which channel plugins can run

**Sources:** [S34](src.s34.md)

By default, any plugin on the Anthropic-maintained allowlist can register as a channel. Admins on Team and Enterprise plans can replace that allowlist with their own by setting `allowedChannelPlugins` in managed settings. Use this to restrict which official plugins are allowed, approve channels from your own internal marketplace, or both. Each entry names a plugin and the marketplace it comes from
