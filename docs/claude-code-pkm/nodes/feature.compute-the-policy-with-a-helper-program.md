---
id: feature.compute-the-policy-with-a-helper-program
kind: feature
status: VERIFIED
title: "Compute the policy with a helper program"
sources: [S61]
---

# Compute the policy with a helper program

**Sources:** [S61](src.s61.md)

A `policyHelper` is an executable your MDM policy or managed settings file names, and Claude Code runs it to compute managed settings at startup. When the selected source configures one and the helper emits a `managedSettings` object, that output changes what Claude Code reads:
