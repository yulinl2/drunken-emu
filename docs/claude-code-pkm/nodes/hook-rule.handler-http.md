---
id: hook-rule.handler-http
kind: hook-rule
status: VERIFIED
title: "Handler type: http"
sources: [S2]
---

# Handler type: http

**Sources:** [S2](src.s2.md)

POSTs the input JSON to url. Fields: url, headers and allowedEnvVars. A non-2xx response or a connection failure is a non-blocking error. Restricted by [Kill switch: allowedHttpHookUrls](setting.kill-switch.allowed-http-hook-urls.md).

## Linked from

- [Kill switch: allowedHttpHookUrls](setting.kill-switch.allowed-http-hook-urls.md)
