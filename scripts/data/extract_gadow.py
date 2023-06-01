#!/usr/bin/env python3

import argparse
import json
import typing as t
from enum import Enum
from pathlib import Path

import polars as pl

GADOW_FILE = Path(__file__).parent.parent.parent / "data" / "KBR_Gadow_2019.xlsx"


class Features(Enum):
    PERSON_NUMBER = "person_number"
    CHILDREN_NUMBER = "children_number"

    def __str__(self) -> str:
        return self.value


def read_gadow(options: dict[str, t.Any] | None = None) -> pl.DataFrame:
    return pl.read_excel(
        GADOW_FILE,
        read_csv_options=options if options is not None else {"skip_rows": 1},
    )


def extract_person_number() -> dict[str, t.Any]:
    data = read_gadow(options={"skip_rows": 1})

    id_ = data.columns[0]
    values = data.columns[13:17]

    counts = (
        data.select([id_, *values])
        .groupby(id_)
        .agg(pl.sum(values))["sum"]
        .value_counts()
    )

    dist = counts.select(pl.col("sum"), pl.col("counts") / pl.col("counts").sum())
    return {str(number): probability for number, probability in dist.iter_rows()}


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
    #     case Features.CHILDREN_NUMBER:
    #         data = extract_children_number()

    args.output_file.write_text(json.dumps(data, indent=4, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
