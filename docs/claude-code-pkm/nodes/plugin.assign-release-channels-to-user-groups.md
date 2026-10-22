---
id: plugin.assign-release-channels-to-user-groups
kind: plugin
status: VERIFIED
title: "Assign release channels to user groups"
sources: [S59]
---

# Assign release channels to user groups

**Sources:** [S59](src.s59.md)

To run stable and early-access channels, host two marketplaces that point at different refs of the same plugins. Then give each user group its own marketplace through either separate endpoint-managed settings or a gateway policy. Server-managed settings from the admin console apply to every user in your organization, so they can't assign different settings to different groups.
