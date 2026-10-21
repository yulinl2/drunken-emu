---
id: feature.keep-developers-from-widening-the-policy
kind: feature
status: VERIFIED
title: "Keep developers from widening the policy"
sources: [S68]
---

# Keep developers from widening the policy

**Sources:** [S68](src.s68.md)

When managed settings set a Boolean key such as `enabled` or `failIfUnavailable`, Claude Code uses the managed value and ignores anything a developer sets locally. For array keys such as `allowRead`, Claude Code merges entries from the scopes the session loads, so a developer can append entries that widen the policy unless a lock covers that key.
