---
id: feature.check-resolved-settings
kind: feature
status: VERIFIED
title: "Check resolved settings"
sources: [S40]
---

# Check resolved settings

**Sources:** [S40](src.s40.md)

Settings merge across managed, user, project, and local scopes. Managed settings apply first when present. Among the rest, the closer scope overrides the broader one in the order local, then project, then user. Some settings can also be set by command-line flags or environment variables, which act as another override layer. When a setting doesn't seem to apply, the value you set is usually being o
