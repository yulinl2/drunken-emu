---
id: question.q1
kind: question
status: OPEN
title: "Q1: Does a hook added mid-session take effect?"
sources: [S2, S3, S9]
---

# Q1: Does a hook added mid-session take effect?

**Sources:** [S2](src.s2.md), [S3](src.s3.md), [S9](src.s9.md)

[Live reload of settings](setting.live-reload.md) says edits to hooks apply live, and a settings file created mid-session loads if its folder already existed. [Observation: mid-session hook had no effect](obs.hook-mid-session-no-effect.md) records a mid-session hook that produced no evaluation in one cloud session. [Observation: SessionStart banner not visible](obs.session-start-banner-not-visible.md) records the related SessionStart observation, and [SessionStart](hook.session-start.md) says plain stdout is added to context. Type: conflict. Next check: a controlled test with one hook present at start and one added mid-session, each logging to a file.

## Linked from

- [Conflict rule: best of, not union](process.conflict-rule.md)
- [Live reload of settings](setting.live-reload.md)
- [Observation: mid-session hook had no effect](obs.hook-mid-session-no-effect.md)
- [Observation: SessionStart banner not visible](obs.session-start-banner-not-visible.md)
