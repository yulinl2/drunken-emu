---
id: hook.stop-failure
kind: hook
status: VERIFIED
title: "StopFailure"
sources: [S2]
---

# StopFailure

**Sources:** [S2](src.s2.md)

Fires when a turn ends because of an API error. Matchers: rate_limit, overloaded, authentication_failed, oauth_org_not_allowed, account_on_hold, billing_error, invalid_request, model_not_found, server_error, max_output_tokens, cloud_credential_error, unknown. Exit 2 is ignored, except for terminalSequence output.
