---
id: feature.go-based-clis-fail-tls-verification-on-macos
kind: feature
status: VERIFIED
title: "Go-based CLIs fail TLS verification on macOS"
sources: [S68]
---

# Go-based CLIs fail TLS verification on macOS

**Sources:** [S68](src.s68.md)

Tools such as `gh`, `gcloud`, and `terraform` may fail TLS verification under Seatbelt. To run these tools outside the sandbox, add a pattern for each tool, such as `gh *`, to `excludedCommands`. The tool then runs with your full access and its stored credentials. If you are using `httpProxyPort` with a MITM proxy and custom CA, set `enableWeakerNetworkIsolation` to `true` instead.
