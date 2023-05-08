#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def agesex2conditional(data: dict[str, dict]) -> dict[str, dict[str, dict]]:
    transformed: dict[str, dict[str, dict]] = {}

    for age_sex, dist in data.items():
        age_range, _, sex = age_sex.partition("_")
        age_range = age_range.replace("x", "99")
        sex = sex.replace("K", "F")
        transformed.setdefault(age_range, {})[sex] = dist

    return transformed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("output_file", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data = json.loads(args.input_file.read_text())
    transformed = agesex2conditional(data)
    args.output_file.write_text(json.dumps(transformed, indent=4) + "\n")


if __name__ == "__main__":
    main()
