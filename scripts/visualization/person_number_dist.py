#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tqdm

from udg.data.utils import load_json
from udg.features.household import HouseholdStructure
from udg.model.model import TrafficModel


def calculate_person_dist(
    model: TrafficModel,
) -> dict[HouseholdStructure, dict[int, float]]:
    dist: dict[HouseholdStructure, dict[int, float]] = {
        structure: {} for structure in HouseholdStructure
    }

    for household in tqdm.tqdm(model.households):
        household_structure: HouseholdStructure = household.features[HouseholdStructure]  # type: ignore[assignment]
        person_number = int(sum(family.person_number for family in household.families))
        if person_number > 7:
            person_number = 7

        dist[household_structure][person_number] = (
            dist[household_structure].get(person_number, 0) + 1
        )

    for _, person_dist in dist.items():
        total = sum(person_dist.values())
        for person_number in person_dist:
            person_dist[person_number] /= total

    return dist


def load_real_dist(path: str) -> dict[HouseholdStructure, dict[int, float]]:
    return load_json(
        path,
        structure=[HouseholdStructure, int],
    )


def plot_dists(model: TrafficModel, real_dist_file: str, output_prefix: Path) -> None:
    person_dist = calculate_person_dist(model)
    real_dist = load_real_dist(real_dist_file)

    for hs in HouseholdStructure:
        fig, ax = plt.subplots(figsize=(8, 6))

        xs = np.array([i for i in range(1, 8)])
        y_pn = [person_dist[hs].get(x, 0) for x in xs]
        y_real = [real_dist[hs].get(x, 0) for x in xs]

        width = 0.4  # the width of the bars

        ax.bar(xs, y_pn, width=width, label="wygenerowana populacja")
        ax.bar(xs + width, y_real, width=width, label="dane rzeczywiste")

        ax.set_xlabel("liczba osób w gospodarstwie")
        ax.set_ylabel("udział gospodarstw w populacji")

        ax.set_xlim((0, 8))
        ax.set_ylim((0, 1))
        ax.legend()

        x_labels = [str(i) for i in range(1, 8)]
        x_labels[x_labels.index("7")] = "7+"
        ax.set_xticks(xs + (width / 2), x_labels)

        fig.tight_layout()

        stem = f"{output_prefix.stem}_{hs.value}"
        fig.savefig(output_prefix.with_stem(stem), dpi=300)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("model_file", type=Path)
    parser.add_argument("real_dist_file")
    parser.add_argument("output_files", type=Path)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data = json.loads(args.model_file.read_text())
    traffic_model = TrafficModel.from_dict(data)
    plot_dists(traffic_model, args.real_dist_file, args.output_files)


if __name__ == "__main__":
    main()
