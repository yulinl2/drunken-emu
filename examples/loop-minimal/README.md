# Minimal instance

From this directory, run `python3 -I ../../bin/loop watch eval`, then
`python3 -I ../../bin/loop watch status`. No hook is installed and no transcript
is read or sent. `stop_runs: []` disables the default record and backup steps.
The runtime writes only `.loop/` here; retain it to retain evaluation history.

This example engine checks one JSON key. Its PASS explicitly leaves meaning
unevaluated. Change `artifact.json` to `{}` to see a failure. Restore the file,
change `policy.json` to `{"required":"other"}`, and evaluate again: unchanged
artifact bytes now receive a new verdict because policy and checker bytes are
declared inputs. An unreadable policy exits 3 (not evaluated).

To adapt this instance, replace the artifact, checker and declared inputs.
Checks run as argument vectors in the instance directory. Exit 0 means pass,
3 means not evaluated, and other exits mean fail. The last stdout line may be
JSON with `layers` and a numeric `vector` (lower is better on every axis).
Declare every file whose changes should invalidate a verdict, including checker
code. External service state and undeclared inputs are not identified by hashes.

The method, evidence bank, goals and verdicts belong to your instance. Add them
and review `loop.json` before enabling host hooks. Hook installation, transcript
parsing and the optional mod target Claude Code; backup additionally requires
bash 4, GNU tools and flock. This example does not verify those integrations.
