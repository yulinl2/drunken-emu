# Evidence: applying a correction to 66 students' grades on a phone (2026-10-03)

**What this is.** One real task, recorded as completely and faithfully as possible, because this kit's questions are open:
what a record of a person's task must contain is not known in advance. It is the source the operation-chain work is judged
against (#31; #32 test points T1, T2, T10; #40).

**Consent.** The owner, who is the narrator, chose to publish the narration verbatim (2026-10-04: completeness and fidelity of
data first; "(c) 我也不介意"). The private bundle (speeds-kit, `docs/evidence/2026-10-03-hw1-correction/`) also holds the
screenshots and the chat context; they stay private because they show students' and a colleague's names.

## Files

| File | What |
|---|---|
| `narration.zh.txt` | the narrator's account, written right after the task, verbatim; sha256 `9823c285dcfb9e279818cf5ad19402cae8960f97b40b512eeeb09103ec8d7741` |
| `transcription.jsonl` | the account step by step (format below), every quote verified verbatim by `validate.py` |
| `validate.py` | keeps the transcription anchored to the narration (stdlib only; run it after any edit) |

## Transcription format (one JSON object per line; a candidate, not the settled record format of #32)

| Field | Meaning |
|---|---|
| `id`, `parent` | identity and nesting: goals contain sub-goals and steps; a RELOAD is a goal inside the goal it serves |
| `kind` | `goal`, `step`, `event` (happened to the narrator), `reflection` (the narrator commenting) |
| `op` | primitive of `docs/OPERATION-MODEL.md` (ANCHOR, SCAN, READ, ENUMERATE, DISCRIMINATE, HOLD, KEYIFY, RELOAD, NAVIGATE, RE-ORIENT, INFER, WAIT, REFRESH, COMMIT, VERIFY) |
| `surface` | where it happens: `claude-app`, `files-app`, `safari`, `safari:speedgrader`, `tapgrade-sheet`, `mind` |
| `quote`, `line` | the verbatim words of the narration this entry stands for, and their line |
| `stated` | properties the **narrator stated**, each a verbatim quote (anchor type, confusables, memory, reading, belief…) |
| `inferred` | properties the **transcriber inferred**; kept apart so they can be checked or discarded |
| `scope` | `2026-10-03` for the run itself; `generalized` where the narrator describes what usually happens |
| `t`, `screenshot` | local time and screenshot, where a screenshot dates the step |

**What the first transcription shows.** 61 entries; 36 carry properties the narrator stated, 2 carry inferred ones: the
account itself names anchors, confusables, reading depth and memory state, so most properties need no estimate. 16 entries
describe what usually happens rather than this run. The fixture in PR #43 (`hw1_correction_pass.json`) was transcribed from a
paraphrase (`docs/OPERATION-MODEL.md` §4) with estimated amounts; it can now be checked against this.

## Screenshots (private; hashes for reference)

| File | When / what | sha256 (first 16) |
|---|---|---|
| IMG_0675.png | 12:16 a student's summary comment still lists the old deductions | `44e9286a2870f9d1` |
| IMG_0676.jpeg | a Q8 note still asks for 1% | `769139bb632ce756` |
| IMG_0678.png | 12:19 Q7/Q8 comments: new keys, old deductions and notes | `0f59d3650982319d` |
| IMG_0679.png | 12:23 Settings, 'Loaded on this phone', TapGrade 0.6.4 | `5d45b6ecb34f62fe` |
| IMG_0680.png | 12:59 Re-sync: 54 older summary comments, 70 would change | `d16f3adcd1ec2510` |
| IMG_0683.png | 13:00 'Removed 18 of 54 older summary comments' | `47c3fcbcfda57f87` |
| IMG_0686.png | 13:06 Files picker, top | `36488a1b076c2e8d` |
| IMG_0687.png | 13:06 Files picker, further down | `98e262026caad240` |
| IMG_0688.jpeg | the chat's step list the owner went back to | `4c6de8a880fa1485` |
| IMG_0689.png | 13:30 'Corrections loaded', Scan my students | `f80c903ff07d90b4` |
| IMG_0690.png | 13:36 66 would change | `d97c3b4144811dd1` |
| IMG_0691.png | 13:44 86 rows already corrected, 42 would change, average 87.55 | `0c1b5cc1267c5ace` |
| IMG_0692.png | 13:48 212 rows already corrected, 'Everything already matches', average still 87.55 | `e7a4bc4e8303c56b` |
| IMG_0772.png | next day 17:55, after a reload: average 88.7 (a complete apply predicts 88.73) | `5f64a72c5f5538a7` |
