---
id: env.claude-code-script-caps
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SCRIPT_CAPS"
sources: [S81]
---

# CLAUDE_CODE_SCRIPT_CAPS

**Sources:** [S81](src.s81.md)

JSON object limiting how many times specific scripts may be invoked per session when `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` is set. Keys are substrings matched against the command text; values are integer call limits. For example, `{"deploy.sh": 2}` allows `deploy.sh` to be called at most twice. Matching is substring-based so shell-expansion tricks like `./scripts/deploy.sh $(evil)` still count against the cap. Runtime fan-out via `xargs` or `find -exec` is not detected; this is a defense-in-depth control
