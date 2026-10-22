---
id: plugin.failures-that-validation-doesn-t-catch
kind: plugin
status: VERIFIED
title: "Failures that validation doesn't catch"
sources: [S51]
---

# Failures that validation doesn't catch

**Sources:** [S51](src.s51.md)

`claude plugin validate` doesn't report every failure. An entry `hooks` written as a file path or array passes validation, and the error appears only when the plugin loads, as Hooks in an entry describes. Errors fetching a `source` also appear only after install, not in validation.
