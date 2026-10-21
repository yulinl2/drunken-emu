---
id: feature.virtual-machine
kind: feature
status: VERIFIED
title: "Virtual machine"
sources: [S69]
---

# Virtual machine

**Sources:** [S69](src.s69.md)

A dedicated virtual machine provides the strongest separation, with its own kernel and, in cloud or microVM deployments, its own virtualized hardware. Options include cloud instances, local hypervisors, and microVMs such as Firecracker. Use this approach when you are evaluating untrusted code, when your security policy requires kernel-level separation between the agent and the host, or when no hos
