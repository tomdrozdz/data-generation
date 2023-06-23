#!/usr/bin/env python3

import argparse
import json
import typing as t
from collections import Counter
from enum import Enum
from pathlib import Path

import polars as pl

WDS_FILE = Path(__file__).parent.parent.parent / "data" / "wds.tab"


class Features(Enum):
    PERSON_NUMBER = "person_number"
    CHILD_NUMBER = "child_number"
    BIKE_NUMBER = "bike_number"
    CAR_NUMBER = "car_number"

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


def extract_child_number() -> dict[str, t.Any]:
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
    for person_number, child_number, probability in dist.iter_rows():
        result.setdefault(str(person_number), {})[str(child_number)] = probability

    return result


def extract_bike_number() -> dict[str, t.Any]:
    data = read_wds()
    data = data.select(
        pl.col("G1.int").alias("person_number"),
        (
            pl.col("M3")
            .map_dict(
                {
                    1: "married",
                    2: "partners",
                    3: "single",
                    4: "widow/er",
                    5: "divorced",
                    6: "separated",
                }
            )
            .alias("marital_status")
        ),
        pl.col("Plec").map_dict({1: "F", 2: "M"}).alias("sex"),
        (
            pl.col("G4")
            .map_dict(
                {
                    1: "children",
                    2: "none",
                    3: "partners",
                    4: "married",
                    5: "married_with_children",
                    6: "partners_with_children",
                    7: "single_with_children",
                    8: "children_left",
                }
            )
            .alias("family_type")
        ),
        pl.col("G6.int").apply(lambda x: 0 if x == -9 else x).alias("child_number"),
        pl.col("G18.09.int").alias("bike_number"),
    )

    # Filter out outliers
    data = data.filter(pl.col("bike_number") < 10)

    # Cannot really handle children
    data = data.filter(pl.col("family_type") != "children")

    data = data.select(
        pl.col("person_number"),
        pl.col("marital_status"),
        (
            # Split single parents into mothers and fathers
            pl.when(
                (pl.col("sex") == "F")
                & (pl.col("family_type") == "single_with_children")
            )
            .then("mother_with_children")
            .when(
                (pl.col("sex") == "M")
                & (pl.col("family_type") == "single_with_children")
            )
            .then("father_with_children")
            # Split families with children that left into married/partners/nones
            .when(
                (pl.col("family_type") == "children_left")
                & (pl.col("person_number") == 1)
            )
            .then("none")
            .when(
                (pl.col("family_type") == "children_left")
                & (pl.col("marital_status") == "married")
            )
            .then("married")
            .when(
                (pl.col("family_type") == "children_left")
                & (pl.col("marital_status") == "partners")
            )
            .then("partners")
            .otherwise(pl.col("family_type"))
            .alias("family_type")
        ),
        (
            pl.when(pl.col("child_number") > 4)
            .then(4)
            .otherwise(pl.col("child_number"))
            .alias("child_number")
        ),
        pl.col("bike_number"),
    )

    # Filter out the rest
    data = data.filter(pl.col("family_type") != "children_left")
    data = data.filter(
        ~(
            ~(pl.col("family_type").str.contains("with_children"))
            & (pl.col("child_number") > 0)
        )
    )
    data = data.filter(
        ~(
            (pl.col("family_type").str.contains("with_children"))
            & (pl.col("child_number") == 0)
        )
    )

    data = (
        data.groupby("family_type", "child_number")
        .agg("bike_number")
        .sort(by="child_number")
    )

    dist: dict[str, dict[str, dict[str, float]]] = {}
    for family_type, children, bikes in data.iter_rows():
        counts = Counter(bikes)
        total = len(bikes)
        dist.setdefault(family_type, {})[str(children)] = {
            str(bike): count / total
            for bike, count in sorted(counts.items(), key=lambda x: x[0])
        }

    # Fill out missing values with 0s. TODO: Can this be done better?
    for family_type, children in dist.items():
        if "with_children" not in family_type:
            continue

        for i in range(1, 5):
            if str(i) not in children:
                children[str(i)] = {"0": 1.0}

    return dist


def extract_car_number() -> dict[str, t.Any]:
    data = read_wds()
    data = data.select(
        pl.col("G1.int").alias("person_number"),
        (
            pl.col("M3")
            .map_dict(
                {
                    1: "married",
                    2: "partners",
                    3: "single",
                    4: "widow/er",
                    5: "divorced",
                    6: "separated",
                }
            )
            .alias("marital_status")
        ),
        pl.col("Plec").map_dict({1: "F", 2: "M"}).alias("sex"),
        (
            pl.col("G4")
            .map_dict(
                {
                    1: "children",
                    2: "none",
                    3: "partners",
                    4: "married",
                    5: "married_with_children",
                    6: "partners_with_children",
                    7: "single_with_children",
                    8: "children_left",
                }
            )
            .alias("family_type")
        ),
        pl.col("G6.int").apply(lambda x: 0 if x == -9 else x).alias("child_number"),
        (pl.col("G18.06.int") + pl.col("G18.07.int")).alias("car_number"),
    )

    # Filter out outliers
    data = data.filter(pl.col("car_number") < 10)

    # Cannot really handle children
    data = data.filter(pl.col("family_type") != "children")

    data = data.select(
        pl.col("person_number"),
        pl.col("marital_status"),
        (
            # Split single parents into mothers and fathers
            pl.when(
                (pl.col("sex") == "F")
                & (pl.col("family_type") == "single_with_children")
            )
            .then("mother_with_children")
            .when(
                (pl.col("sex") == "M")
                & (pl.col("family_type") == "single_with_children")
            )
            .then("father_with_children")
            # Split families with children that left into married/partners/nones
            .when(
                (pl.col("family_type") == "children_left")
                & (pl.col("person_number") == 1)
            )
            .then("none")
            .when(
                (pl.col("family_type") == "children_left")
                & (pl.col("marital_status") == "married")
            )
            .then("married")
            .when(
                (pl.col("family_type") == "children_left")
                & (pl.col("marital_status") == "partners")
            )
            .then("partners")
            .otherwise(pl.col("family_type"))
            .alias("family_type")
        ),
        (
            pl.when(pl.col("child_number") > 4)
            .then(4)
            .otherwise(pl.col("child_number"))
            .alias("child_number")
        ),
        pl.col("car_number"),
    )

    # Filter out the rest
    data = data.filter(pl.col("family_type") != "children_left")
    data = data.filter(
        ~(
            ~(pl.col("family_type").str.contains("with_children"))
            & (pl.col("child_number") > 0)
        )
    )
    data = data.filter(
        ~(
            (pl.col("family_type").str.contains("with_children"))
            & (pl.col("child_number") == 0)
        )
    )

    data = (
        data.groupby("family_type", "child_number")
        .agg("car_number")
        .sort(by="child_number")
    )

    dist: dict[str, dict[str, dict[str, float]]] = {}
    for family_type, children, cars in data.iter_rows():
        counts = Counter(cars)
        total = len(cars)
        dist.setdefault(family_type, {})[str(children)] = {
            str(car): count / total
            for car, count in sorted(counts.items(), key=lambda x: x[0])
        }

    # Fill out missing values with 0s. TODO: Can this be done better?
    for family_type, children in dist.items():
        if "with_children" not in family_type:
            continue

        for i in range(1, 5):
            if str(i) not in children:
                children[str(i)] = {"1": 1.0}

    return dist


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
        case Features.CHILD_NUMBER:
            data = extract_child_number()
        case Features.BIKE_NUMBER:
            data = extract_bike_number()
        case Features.CAR_NUMBER:
            data = extract_car_number()

    args.output_file.write_text(json.dumps(data, indent=4) + "\n")


if __name__ == "__main__":
    main()
