"""python3 -m checks.hw2_sample_prediction COMMAND

  rebuild  --speeds-kit PATH [--port 8881] [--commit --replace-previous --trailer T ...] [--tests]
           the whole thing, for another speeds-kit head: read the checkout, measure both bank sizes on a mock Canvas, find the cited lines,
           write the fixture, the inputs, the registration (JSON and text) and the OPERATION-CHAINS section; prints what moved.
  inputs   --speeds-kit PATH        only the inputs file (commit, sha256s, the place of every cited line)
  build    [--check] [--parent SHA] the fixture, the registration and its text from the committed inputs and measured files;
                                    --check changes nothing and exits 1 when a committed file is not what the generator makes
  verify   --speeds-kit PATH        does that checkout still match the committed inputs?
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import inputs as I, rebuild as RB, registration as R


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m checks.hw2_sample_prediction", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rebuild", help="measure and rebuild everything for a speeds-kit checkout")
    r.add_argument("--speeds-kit", required=True, help="a speeds-kit checkout (read only; it may be moved afterwards)")
    r.add_argument("--speeds-kit-commit", help="the commit the files are of (40 hex digits); default: the last commit that touched a file the build reads")
    r.add_argument("--port", type=int, default=8881, help="port of the mock Canvas, 8881-8883 (default 8881); started and stopped by this command")
    r.add_argument("--measured-large", help="use this measured file instead of measuring (the other one is needed too)")
    r.add_argument("--measured-example", help="use this measured file instead of measuring")
    r.add_argument("--commit", action="store_true", help="make the two commits: the chains and measurements first, the registration last")
    r.add_argument("--replace-previous", action="store_true", help="with --commit: first drop the last two commits if they are the pair this command made earlier (soft reset; the working tree is kept)")
    r.add_argument("--trailer", action="append", default=[], help="a trailer line of both commit messages, 'Key: value' (repeat; needed with --commit)")
    r.add_argument("--tests", action="store_true", help="also run test_chain, test_explore_text, gen_tree --check and ci_claims (EMU_PORT=8883)")
    i = sub.add_parser("inputs", help="write only docs/predictions/hw2-sample-pass.inputs.json")
    i.add_argument("--speeds-kit", required=True)
    i.add_argument("--speeds-kit-commit")
    b = sub.add_parser("build", help="rebuild from the committed inputs and measured files")
    b.add_argument("--check", action="store_true")
    b.add_argument("--parent", help="the parent commit to register (default: HEAD)")
    v = sub.add_parser("verify", help="compare a speeds-kit checkout with the committed inputs")
    v.add_argument("--speeds-kit", required=True)
    a = ap.parse_args(argv)

    try:
        if a.cmd == "rebuild":
            if bool(a.measured_large) != bool(a.measured_example):
                ap.error("--measured-large and --measured-example go together")
            measured = {"large": a.measured_large, "example": a.measured_example} if a.measured_large else None
            return RB.rebuild(Path(a.speeds_kit), a.speeds_kit_commit, a.port, measured, a.commit, a.replace_previous, a.trailer, a.tests)
        if a.cmd == "inputs":
            inp = I.make(Path(a.speeds_kit), a.speeds_kit_commit)
            RB.write(I.INPUTS_PATH, I.dump(inp))
            print(f"wrote {I.INPUTS_PATH}: commit {inp['speeds_kit']['commit'][:12]}, script {inp['speeds_kit']['script']['sha256'][:12]}, {len(inp['citations'])} citations")
            return 0
        if a.cmd == "verify":
            problems = I.problems(I.load(), Path(a.speeds_kit))
            for p in problems:
                print(p)
            print("the checkout matches the committed inputs" if not problems else f"{len(problems)} difference(s)")
            return 1 if problems else 0
        if a.cmd == "build":
            if a.check:
                problems = RB.check_all()
                for p in problems:
                    print(p)
                print("every generated file is what the generator makes" if not problems else f"{len(problems)} generated file(s) differ")
                return 1 if problems else 0
            inp = I.load()
            MJ, AJ = RB.read_json(R.MEASURED), RB.read_json(R.MEASURED_EXAMPLE)
            RB.build_chain_files(MJ, AJ, inp)
            RB.build_registration_files(a.parent or RB.git("rev-parse", "HEAD"))
            print("wrote the fixture, the registration JSON, its text and the OPERATION-CHAINS section")
            return 0
    except (I.InputsError, RuntimeError, ValueError) as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
