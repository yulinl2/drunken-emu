---
id: feature.re-sign-aws-requests
kind: feature
status: VERIFIED
title: "Re-sign AWS requests"
sources: [S68]
---

# Re-sign AWS requests

**Sources:** [S68](src.s68.md)

AWS requests carry SigV4 signatures over the request contents, so mask `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` together. The proxy detects a SigV4 request by the access key's sentinel and re-signs the request with the real values, which requires Claude Code v2.1.221 or later. If you mask only the secret, requests are signed with a placeholder the proxy can't detect, so they fail at AWS.
