---
id: feature.create-your-first-skill
kind: feature
status: VERIFIED
title: "Create your first skill"
sources: [S32]
---

# Create your first skill

**Sources:** [S32](src.s32.md)

This example creates a skill that summarizes the uncommitted changes in your git repository and flags anything risky. It pulls the live diff into the prompt before Claude reads it, so the response is grounded in your actual working tree rather than what Claude can guess from open files. Claude loads the skill automatically when you ask about your changes, or you can invoke it directly with `/summa
