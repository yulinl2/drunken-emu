"""Example engine: validate a JSON object's required key, not its meaning."""
import json
import pathlib
import sys


def main():
    try:
        policy = json.loads(pathlib.Path("policy.json").read_text(encoding="utf-8"))
        required = policy["required"]
        if not isinstance(required, str):
            raise ValueError("required must be a string")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"policy unavailable: {exc}")
        return 3
    try:
        artifact = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
        passed = isinstance(artifact, dict) and required in artifact
    except (OSError, ValueError) as exc:
        print(f"artifact invalid: {exc}")
        passed = False
    print(json.dumps({"gate": "pass" if passed else "fail",
                      "layers": {"required_key": "pass" if passed else "fail",
                                 "meaning": "not_evaluated"}}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
