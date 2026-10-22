---
id: setting.network
kind: setting
status: VERIFIED
title: "Network"
sources: [S68]
---

# Network

**Sources:** [S68](src.s68.md)

default: No direct route out. Connections go through a proxy on your machine that checks each host against your allowed domains, which start empty. Your permission mode decides what happens to other hosts; change it with: `network.allowedDomains`, `network.deniedDomains`
