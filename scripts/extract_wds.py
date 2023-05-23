#!/usr/bin/env python3

import argparse
import json
import typing as t
from enum import Enum
from pathlib import Path

import polars as pl

WDS_FILE = Path(__file__).parent.parent / "data" / "wds.tab"


class Features(Enum):
    PERSON_NUMBER = "person_number"
    CHILDREN_NUMBER = "children_number"

    def __str__(self) -> str:
        return self.value


def read_wds() -> pl.DataFrame:
    return pl.read_csv(WDS_FILE, separator="\t")


def extract_person_number() -> dict[str, t.Any]:
    data = read_wds()
    person_numbers = data["G1.int"]
    counts = person_numbers.value_counts()
    dist = counts.select(pl.col("G1.int"), pl.col("counts") / counts["counts"].sum())
    return {str(number): probability for number, probability in dist.iter_rows()}


def extract_children_number() -> dict[str, t.Any]:
    data = read_wds()
    numbers = data.select(
        pl.col("G1.int"),
        pl.col("G6.int").apply(lambda x: 0 if x == -9 else x),
    )

    counts_all = (
        numbers.groupby("G1.int", "G6.int")
        .count()
        .join(numbers.groupby("G1.int").count(), on="G1.int")
    )

    dist = counts_all.select(
        "G1.int",
        "G6.int",
        pl.col("count") / pl.col("count_right"),
    )

    result: dict[str, dict[str, float]] = {}
    for person_number, children_number, probability in dist.iter_rows():
        result.setdefault(str(person_number), {})[str(children_number)] = probability

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("feature", type=Features, choices=Features)
    parser.add_argument("output_file", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    match args.feature:
        case Features.PERSON_NUMBER:
            data = extract_person_number()
        case Features.CHILDREN_NUMBER:
            data = extract_children_number()

    args.output_file.write_text(json.dumps(data, indent=4, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
