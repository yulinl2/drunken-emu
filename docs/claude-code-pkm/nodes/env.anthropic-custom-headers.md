---
id: env.anthropic-custom-headers
kind: env
status: VERIFIED
title: "ANTHROPIC_CUSTOM_HEADERS"
sources: [S81]
---

# ANTHROPIC_CUSTOM_HEADERS

**Sources:** [S81](src.s81.md)

Custom headers to add to requests (`Name: Value` format, newline-separated for multiple headers). If a name or value contains a character an HTTP header can't carry, such as a curly quote or a zero-width space, the request fails with an error that identifies the pair by position. Requires Claude Code v2.1.227 or later. Invalid request header value lists the exact character set and where the check runs. A value that sets a credential, org or tenant, routing, or API-behavior header, such as `Authorization` or `Host`, counts as a setting that needs approval when server-managed settings deliver it. From project or local settings, such a value follows the rules for when `env` values apply
