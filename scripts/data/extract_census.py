#!/usr/bin/env python3

import argparse
import json
import typing as t
from enum import Enum
from pathlib import Path

import polars as pl

AGE_SEX_FILE = (
    Path(__file__).parent.parent.parent
    / "data"
    / "census"
    / "__year__"
    / "wroclaw_age_sex.csv"
)
FAMILY_TYPES_FILE = (
    Path(__file__).parent.parent.parent
    / "data"
    / "census"
    / "__year__"
    / "wroclaw_family_types.csv"
)
VOIVODESHIP_HOUSEHOLD_FILE = (
    Path(__file__).parent.parent.parent
    / "data"
    / "census"
    / "__year__"
    / "tablice_wynikowe.xlsx"
)


class Features(Enum):
    AGE = "age"
    SEX = "sex"
    HOUSEHOLD_STRUCTURE = "household_structure"
    FAMILY_TYPE = "family_type"
    PERSON_NUMBER = "person_number"
    CHILD_NUMBER = "child_number"
    SIMPLE_CHILD_NUMBER = "simple_child_number"

    def __str__(self) -> str:
        return self.value


def read_age_sex(year: int) -> pl.DataFrame:
    path = str(AGE_SEX_FILE).replace("__year__", str(year))
    return pl.read_csv(path, separator=";")


def read_family_types(year: int) -> pl.DataFrame:
    path = str(FAMILY_TYPES_FILE).replace("__year__", str(year))
    return pl.read_csv(path, separator=";")


def read_voivodeship_household(sheet_name: str, year: int) -> pl.DataFrame:
    path = str(VOIVODESHIP_HOUSEHOLD_FILE).replace("__year__", str(year))
    return pl.read_excel(path, sheet_name=sheet_name)


def extract_sex(year: int) -> dict[str, t.Any]:
    data = read_age_sex(year)
    data = data.filter(pl.col("Wymiar 1") != "ogółem")

    counts = data.groupby("Wymiar 1").agg(pl.sum(str(year)))
    dist = counts.select(
        pl.col("Wymiar 1"),
        pl.col(str(year)) / pl.col(str(year)).sum(),
    )
    dist = dist.select(
        pl.col("Wymiar 1").map_dict({"mężczyźni": "M", "kobiety": "F"}),
        (str(year)),
    )

    return {sex: probability for sex, probability in dist.iter_rows()}


def extract_age(year: int) -> dict[str, t.Any]:
    data = read_age_sex(year)

    def _age_dist_fox_sex(data: pl.DataFrame, sex: str) -> dict[str, t.Any]:
        filtered = data.filter(
            (pl.col("Wymiar 1") == sex) & (pl.col("Wymiar 2") != "ogółem")
        )
        dist = filtered.select(
            pl.col("Wymiar 2").map_dict({"90 i więcej": "90+"}, default=pl.first()),
            pl.col(str(year)) / pl.col(str(year)).sum(),
        )
        return {str(age): probability for age, probability in dist.iter_rows()}

    return {
        "M": _age_dist_fox_sex(data, "mężczyźni"),
        "F": _age_dist_fox_sex(data, "kobiety"),
    }


def extract_household_structure(year: int) -> dict[str, t.Any]:
    data = read_voivodeship_household("TABL. 1", year)
    data = data.rename({f"_duplicated_{i}": str(i) for i in range(9)})
    data = data.drop(*(str(i) for i in range(9)))
    data = pl.concat(
        (
            data[29],
            data[31],
            data[36],
            data[41],
            data[46],
            data[47],
            data[48],
        )
    )

    total = data.select(pl.col("").cast(pl.Int64)).sum().item()

    def _household_structure_dist(row: int) -> float:
        _, count = data.row(row)
        return int(count) / total

    return {
        "single_family": _household_structure_dist(0),
        "single_family_with_parents": _household_structure_dist(1),
        "single_family_with_others": _household_structure_dist(2),
        "two_families_related": _household_structure_dist(3),
        "two_families_unrelated": _household_structure_dist(4),
        "three_and_more_families": _household_structure_dist(5),
        "unrelated": _household_structure_dist(6),
    }


def extract_family_type(year: int) -> dict[str, t.Any]:
    data = read_family_types(year)
    data = data.drop("Kategoria", "Grupa", "Podgrupa (wymiary)")
    data = data.filter(pl.col("Wymiar 2") != "wskaźnik precyzji")
    data = data[1:]
    data = data.filter(pl.col("Wymiar 1").str.contains("razem").is_not())

    print(data)

    total = data.select(pl.col(str(year)).cast(pl.Int64)).sum().item()

    def _prob(row: int) -> float:
        *_, count = data.row(row)
        return int(count) / total

    return {
        "married": _prob(0),
        "married_with_children": _prob(1),
        "partners": _prob(2),
        "partners_with_children": _prob(3),
        "mother_with_children": _prob(4),
        "father_with_children": _prob(5),
    }


def extract_person_number(year: int) -> dict[str, t.Any]:
    data = read_voivodeship_household("TABL. 1", year)
    data = data.drop("").rename({f"_duplicated_{i}": str(i + 1) for i in range(9)})
    data = data.drop("8", "9")
    data = pl.concat(
        (
            data[29],
            data[31],
            data[36],
            data[41],
            data[46],
            data[47],
            data[48],
        )
    )

    def _household_person_dist(row: int) -> dict[str, float]:
        _, *counts = data.row(row)
        int_counts = [int(count) if count != "-" else 0 for count in counts]
        total = sum(int_counts)
        return {str(i + 1): int_counts[i] / total for i in range(7)}

    return {
        "single_family": _household_person_dist(0),
        "single_family_with_parents": _household_person_dist(1),
        "single_family_with_others": _household_person_dist(2),
        "two_families_related": _household_person_dist(3),
        "two_families_unrelated": _household_person_dist(4),
        "three_and_more_families": _household_person_dist(5),
        "unrelated": _household_person_dist(6),
    }


def extract_child_number(year: int) -> dict[str, t.Any]:
    data = read_voivodeship_household("TABL. 17", year)
    data = data.drop("").rename({f"_duplicated_{i}": str(i) for i in range(6)})
    data = data.drop("0", "5")
    data = data[13:17]
    data = data.select(*(pl.col(str(i)).cast(pl.Int64) for i in range(1, 5)))

    def _household_person_dist(data: pl.DataFrame) -> dict[str, dict[str, float]]:
        total = data.sum(axis=1).item()
        transposed = data.transpose()
        return {str(i + 1): transposed[i].item() / total for i in range(4)}

    return {
        "married_with_children": _household_person_dist(data[0]),
        "partners_with_children": _household_person_dist(data[1]),
        "mother_with_children": _household_person_dist(data[2]),
        "father_with_children": _household_person_dist(data[3]),
    }


def extract_simple_child_number(year: int) -> dict[str, t.Any]:
    data = read_voivodeship_household("TABL. 17", year)
    data = data.drop("").rename({f"_duplicated_{i}": str(i) for i in range(6)})
    data = data.drop("0").rename({"5": "0"})
    data = data[12]
    data = data.select(*(pl.col(str(i)).cast(pl.Int64) for i in range(5)))

    def _household_child_dist(person_number: int) -> dict[str, float]:
        cutoff = person_number if person_number < 5 else 5
        filtered = data.select(*(pl.col(str(i)) for i in range(cutoff)))

        total = filtered.sum(axis=1).item()
        transposed = filtered.transpose()

        return {str(i): transposed[i].item() / total for i in range(cutoff)}

    return {
        str(person_number): _household_child_dist(person_number)
        for person_number in range(1, 8)
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("feature", type=Features, choices=Features)
    parser.add_argument("output_file", type=Path)

    parser.add_argument("--year", type=int, default=2011)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    match args.feature:
        case Features.SEX:
            data = extract_sex(args.year)
        case Features.AGE:
            data = extract_age(args.year)
        case Features.HOUSEHOLD_STRUCTURE:
            data = extract_household_structure(args.year)
        case Features.FAMILY_TYPE:
            data = extract_family_type(args.year)
        case Features.PERSON_NUMBER:
            data = extract_person_number(args.year)
        case Features.CHILD_NUMBER:
            data = extract_child_number(args.year)
        case Features.SIMPLE_CHILD_NUMBER:
            data = extract_simple_child_number(args.year)

    args.output_file.write_text(json.dumps(data, indent=4) + "\n")


if __name__ == "__main__":
    main()
