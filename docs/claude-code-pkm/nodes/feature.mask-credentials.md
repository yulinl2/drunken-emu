---
id: feature.mask-credentials
kind: feature
status: VERIFIED
title: "Mask credentials"
sources: [S68]
---

# Mask credentials

**Sources:** [S68](src.s68.md)

When you mask a credential, Claude Code shows sandboxed commands a per-session placeholder called the sentinel, and the sandbox proxy substitutes the real value on outbound requests to hosts you allow. A `deny` entry under Protect credentials blocks the credential instead. For files on macOS, Claude Code blocks the file instead of masking it. The `sandbox.credentials` reference lists every field.
