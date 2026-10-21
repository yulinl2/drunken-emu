---
id: cmd.usage-credits
kind: command
status: VERIFIED
title: "/usage-credits"
sources: [S80]
---

# /usage-credits

**Sources:** [S80](src.s80.md)

Configure usage credits, or request them from your admin, when you hit a limit. Opens your usage-credits billing settings in the browser, except that Team and Enterprise members without billing access instead send a usage-credits request to their admin from the CLI, after confirming in a dialog that the request notifies their admins. When no browser can open the billing page, for example over SSH, the command prints the URL to visit instead; this requires Claude Code v2.1.205 or later, and earlier versions showed nothing in that case. Previously `/extra-usage`
