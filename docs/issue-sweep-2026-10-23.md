# Which questions survived the 2026-10-23 sweep?

Provenance: Codex session, repository `1e71a8b597528ae222556b5c1a922890f45bc739`.
Read all 82 issue-collection records: **56 issues (48 open, 8 closed)** and
26 PRs. Read all 96 issue/PR conversation comments. The next issue page was
empty, and the comment count equals the sum declared by the records. Inline
reviews of the open PRs and their current branches were inspected as well.
This is a dated reading, not an independent blind replication of prior workers.

The original texts remain in GitHub. No issue is closed or rewritten by this
sweep; a merged component is evidence about a question, not its replacement.

| Question family | Existing issues | What still needs an observation? |
| --- | --- | --- |
| Tree tooling beyond this repo | #2 | Does a filesystem-root consumer justify changing the git-tracked index tool? |
| Figures, layout and acceptance | #5–#8, #10–#15, #23, #25, #26, #28 | External SVG and native plot paths already exist. Do current research-owned figures have fresh source-correct verdicts? Are the two-reader/round-limit practices actually enforced? Is a real multi-parent graph needed beyond the existing repeated-node projection? |
| Interactive tutorial | #16–#22 | Can one actual chapter connect live data, an interaction and an independently interpreted verdict? Content belongs with its research owner; the kit owns reusable instruments. |
| Previously exposed figure | #24 | Is the analytic HAN figure on `attempt/plot-wrap` intended to be public? The branch still exists. No deletion or publication decision is inferred. |
| Person, chains and verifiers | #31–#40 | The chain layer is on main (#43), but can a captured run establish properties that narrated defaults cannot? Are load weights calibrated against a held-out experience? The void publisher registration scored nothing. |
| Bootstrap, conventions and provenance | #44, #47–#53, #55 | #45/#65 removed the external startup dependency. Does that reduce task-start friction in real new sessions? Can the generated index reflect exactly the eventual commit during merges? |
| Feedback delivery | #54, #59, #66–#75 | #77 landed the loop plumbing; #78 fixed launch paths. Does a real harness deliver its signal? Do held-out reader outcomes improve? Which proposed oracle/adverse-pattern interpretation did the owner mean? |
| Plain HTML | #76 | The closed-details false target is fixed (#79). Can the public CLI audit the unchanged consumer page, and which parts remain unmeasured? This patch supplies the native target path and paired controls. |
| Repetition and compaction | #81 | The 23-check-in experiment is complete. Case 1 and far recall remain unobserved; P1 is undecidable from the visible trace. Can another surface reproduce the retained-message distinction? |

## Where do competing pending branches disagree with the evidence?

| Open PR | Current head | Question retained |
| --- | --- | --- |
| #4, prose readers | `27b2ba52bfcf5eb73503db5b38129c477f18c54b` | Its own review and consumption report show missing controls, write-into-input behavior and poor portability. Would the measured read-in consumer justify a narrower reader instead of merging all four? |
| #58, calendar readers | `c7aa2e38176c62b62f990fde9afb4bfdf5a6e007` | Could the reader-cost questions work through the current browser layer with planted controls? A non-applicable dispatch sketch is not a working adapter. |
| #82, tools/harness PKM | `984f488f8e09178798374655e32ad4a91fd97da8` | Do 5,571 generated nodes and zero GAP statuses establish conceptual adequacy? Some nodes are task headings; the PR itself discloses that handwritten ids do not refresh from fetched rows. How will those competing claims be compared semantically? |

The closed PRs were also read: #1/#27 (explore), #3 (fragments), #9/#41/#45/#65
(bootstrap), #29/#30/#42/#43/#56/#57 (browser and operation-model history),
#46 (index), #60–#64 (claims/imports/targets/CI), #77–#80 (loop/launch/visibility).
Their observations supersede older blocker statements only in the scopes they
actually tested. In particular #72's launch defect is fixed; its requested
environment matrix and flake rate are not established by that fix.

## Why this experiment, given those alternatives?

A consumer-local browser script already demonstrated HTML rendering (#76).
The remaining repeated friction is the JSX-only public entry point: smoke and
shots also assume `#root`. Reusing the existing checks with an unchanged HTML
target is smaller than introducing a second auditor or converting the page to
React. Local serving also works where a managed browser blocks `file://`
(observed in this session). The native path preserves relative files and the
old JSX behavior. The tests deliberately retain failures instead of defining
HTML success as merely finding a body.

What does this leave open? #71's full coverage model, #68's real hook delivery,
#70's held-out improvement test, P-9d8b's captured chains, and all questions of
meaning. This session installed no hooks and made no causal claim about #81's
provider internals. Code controls and a same-session source-aware screenshot
reading are not independent human experiences.

## What was run on this patch?

The full Python suite: **388 passed, zero skips** (Python 3.12, Playwright
headless shell 151.0.7922.34 / revision 1234). Figbank's direct test runs:
**42 + 20 + 3 passed**. `checks/ci_claims.py`: all six claims hold.
`bin/gen_tree.py --check`: 197 tracked files. All eight native-target controls
pass; the new native-HTML smoke test fails on original main `1e71a8b` with
exit 2 from its JSX-only path. These checks establish mechanics and regression
coverage, not hook delivery or a reader's understanding.
