"""The HW2 blind-sample prediction, built from files instead of typed by hand.

What it makes (all under this repository, none of it written into a speeds-kit checkout):

    checks/fixtures/chains/tapgrade_0_6_7_sample_pass.json    the seven chains of the pass          (chains.py)
    docs/predictions/hw2-sample-pass.inputs.json              what was read from the speeds-kit checkout: commit, sha256s,
                                                              and the line of every construct of the code and of the docs that a note cites  (inputs.py, cites.py)
    docs/predictions/hw2-sample-pass.measured*.json           the content-blind measurements, large and example-size bank
    docs/predictions/hw2-sample-pass.prediction.json          the registration, machine-readable                     (registration.py)
    docs/predictions/hw2-sample-pass.md                       the registration, for people                           (markdown.py)
    docs/OPERATION-CHAINS.md                                  the short section between its two markers              (markdown.py)

One command remakes all of it for another speeds-kit head (see __main__.py):

    python3 -m checks.hw2_sample_prediction rebuild --speeds-kit PATH --port 8881

Everything a build reads is a committed file (inputs.json, the two measured files, the baselines), so `build --check` can
rebuild it in memory and say whether the committed registration is exactly what the generator makes: a hand edit of a registered file is
found, and so is a change of the generator.  The hand-written parts live in chains.py (the declared properties and their notes),
events.py (the events, their probabilities and what each rests on) and changes.py (why each number moved since the first draft).
"""
