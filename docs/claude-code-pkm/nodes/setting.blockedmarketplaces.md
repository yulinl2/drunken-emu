---
id: setting.blockedmarketplaces
kind: setting
status: VERIFIED
title: "blockedMarketplaces"
sources: [S61]
---

# blockedMarketplaces

**Sources:** [S61](src.s61.md)

An individual invalid entry is stripped and the valid subset is enforced. An entry that parses but can never match, such as a `hostPattern` regex that doesn't compile, is kept with a warning. It blocks nothing until fixed, but marketplace restrictions stay active. A wholly invalid value is dropped with a warning, since blocking every marketplace would block sources the policy never named.
