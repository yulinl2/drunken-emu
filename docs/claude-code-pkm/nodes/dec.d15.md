---
id: dec.d15
kind: decision
status: DECIDED
title: "Overlapping candidates: one winner per group"
---

# Overlapping candidates: one winner per group

Groups: 84; winners kept: 84; losers demoted to SUPERSEDED: 107. Two active nodes overlap when they share a surface family and a normalized title, and their bodies say the same thing (word Jaccard similarity of at least 0.5, or an overlap coefficient of at least 0.8 with four or more content words). The winner is the first in this order: a body that is not a placeholder, VERIFIED status, the longer body, the shorter id, then the alphabetically first id. A loser keeps its old body after a pointer to the winner: demote, do not destroy. Nothing is merged or averaged. A hand-written node and a generated row with the same id are not a group: the hand-written node stays, because it is curated and cites a source. Check: build/best_of.py --verify reports zero groups among active nodes.
