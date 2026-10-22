---
id: feature.cancel-a-question-with-one-key-press
kind: feature
status: VERIFIED
title: "Cancel a question with one key press"
sources: [S79]
---

# Cancel a question with one key press

**Sources:** [S79](src.s79.md)

To cancel a question with one key press in vim mode, bind another key to `select:cancel` in the `Select` context. You can cancel this way from the `Other` row of a question where you select one option. In screen reader mode or in a question where you can select several options, the bound key doesn't cancel, so cancel with Escape instead.
