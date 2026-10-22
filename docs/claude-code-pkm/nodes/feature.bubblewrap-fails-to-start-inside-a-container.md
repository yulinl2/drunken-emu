---
id: feature.bubblewrap-fails-to-start-inside-a-container
kind: feature
status: VERIFIED
title: "Bubblewrap fails to start inside a container"
sources: [S68]
---

# Bubblewrap fails to start inside a container

**Sources:** [S68](src.s68.md)

In an unprivileged container, bubblewrap can't mount a fresh `/proc` filesystem, so sandboxed commands fail with a `bwrap` error such as `Can't mount proc on /newroot/proc: Operation not permitted`. Set `enableWeakerNestedSandbox` to `true` so the sandbox bind-mounts the container's existing `/proc` instead. Only use this setting when the outer container already provides the isolation boundary you
