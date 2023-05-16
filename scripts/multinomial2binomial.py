#!/usr/bin/env python3

import argparse
import json
import typing as t
from pathlib import Path


def multinomial2binomial(data: dict[str, t.Any]) -> dict[str, t.Any]:
    match data:
        case {"0": _, "1": pos_prob}:
            return pos_prob
        case _:
            return {k: multinomial2binomial(v) for k, v in data.items()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("output_file", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data = json.loads(args.input_file.read_text())
    transformed = multinomial2binomial(data)
    args.output_file.write_text(json.dumps(transformed, indent=4) + "\n")


if __name__ == "__main__":
    main()
