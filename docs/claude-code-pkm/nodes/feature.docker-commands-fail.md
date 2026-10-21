---
id: feature.docker-commands-fail
kind: feature
status: VERIFIED
title: "docker commands fail"
sources: [S68]
---

# docker commands fail

**Sources:** [S68](src.s68.md)

`docker` is incompatible with the sandbox. Take the `docker` commands you need out of the sandbox with an `excludedCommands` pattern such as `docker compose *`. Run commands outside the sandbox with `excludedCommands` explains what an excluded `docker` command can reach. A narrower pattern takes fewer commands out of the sandbox.
