---
id: feature.remote-control-isn-t-enabled-for-this-account
kind: feature
status: VERIFIED
title: "\"Remote Control isn't enabled for this account\""
sources: [S21]
---

# "Remote Control isn't enabled for this account"

**Sources:** [S21](src.s21.md)

Claude Code checked Remote Control availability for the account you're signed in with and the check came back off. The usual cause is cached entitlements that are out of date after a plan change. Run `claude auth logout` then `claude auth login` to refresh them, and update Claude Code if you're on an old version.
