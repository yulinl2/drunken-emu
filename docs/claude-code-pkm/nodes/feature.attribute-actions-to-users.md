---
id: feature.attribute-actions-to-users
kind: feature
status: VERIFIED
title: "Attribute actions to users"
sources: [S65]
---

# Attribute actions to users

**Sources:** [S65](src.s65.md)

The standard attributes on each event include the authenticated user's identity: `user.email`, `user.account_uuid`, `user.account_id`, and `organization.id` when signed in with a Claude account or, in a cloud session, when the session's own credentials carry them, plus `user.id` and the per-session `session.id`. `user.id` is an installation-scoped identifier, except in sessions signed in to a Clau
