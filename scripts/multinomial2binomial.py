#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def _transform(data) -> None:
    for k, v in data.items():
        match v:
            case {"0": _, "1": pos_prob}:
                data[k] = pos_prob
            case _:
                multinomial2binomial(v)


def multinomial2binomial(data: dict[str, dict]) -> dict[str, dict[str, dict]]:
    return {k: _transform(v) for k, v in data.items()}


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
