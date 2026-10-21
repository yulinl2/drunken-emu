---
id: feature.runs-time-out-or-hit-the-turn-cap
kind: feature
status: VERIFIED
title: "Runs time out or hit the turn cap"
sources: [S47]
---

# Runs time out or hit the turn cap

**Sources:** [S47](src.s47.md)

The defaults are 10 turns and 300 seconds. Raise `max_turns` and `timeout_seconds` in the case for tasks that need more, and use `--max-cost-usd` as the cost ceiling rather than tight per-run limits.
