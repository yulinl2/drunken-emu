---
id: setting.curl-noproxy-https-example-com
kind: setting
status: VERIFIED
title: "curl --noproxy '*' https://example.com"
sources: [S68]
---

# curl --noproxy '*' https://example.com

**Sources:** [S68](src.s68.md)

result inside the sandbox: Fails with `Could not resolve host`, because the command has no route around the sandbox proxy
