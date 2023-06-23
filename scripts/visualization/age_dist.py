#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import tqdm

from udg.data.utils import load_json
from udg.features.person import Age, Sex
from udg.model.model import TrafficModel


def calculate_age_dist(model: TrafficModel) -> dict[Sex, dict[Age, float]]:
    people = [
        person
        for household in model.households
        for family in household.families
        for person in family.persons
    ]

    dist: dict[Sex, dict[Age, float]] = {
        Sex.M: {},
        Sex.F: {},
    }

    for person in tqdm.tqdm(people):
        sex: Sex = person.features[Sex]  # type: ignore[assignment]
        age: Age = person.features[Age]  # type: ignore[assignment]

        dist[sex][age] = dist[sex].get(age, 0) + 1

    for _, age_dist in dist.items():
        total = sum(age_dist.values())
        for age in age_dist:
            age_dist[age] /= total

    return dist


def load_real_dist(path: str) -> dict[Sex, dict[Age, float]]:
    data = load_json(path, structure=[Sex])
    for dist in data.values():
        oldest = dist.pop("90+")
        smoothed = oldest / 10
        for i in range(90, 100):
            dist[str(i)] = smoothed

    return {
        sex: {Age(age): dist for age, dist in age_dist.items()}
        for sex, age_dist in data.items()
    }


def plot_dists(model: TrafficModel, real_dist_file: str, output_prefix: Path) -> None:
    age_dist = calculate_age_dist(model)
    real_dist = load_real_dist(real_dist_file)

    for sex in Sex:
        fig, ax = plt.subplots(figsize=(8, 6))

        xs = [age for age, _ in sorted(age_dist[sex].items(), key=lambda x: x[0])]
        y_age = [dist for _, dist in sorted(age_dist[sex].items(), key=lambda x: x[0])]
        y_real = [
            dist for _, dist in sorted(real_dist[sex].items(), key=lambda x: x[0])
        ]

        ax.plot(xs, y_age, label="populacja wygenerowana")
        ax.plot(xs, y_real, label="dane rzeczywiste")

        ax.set_xlabel("wiek")
        ax.set_ylabel("udział ludzi w populacji")

        ax.set_xlim((0, 100))
        ax.set_ylim((0, 0.025))
        ax.legend()

        fig.tight_layout()

        stem = f"{output_prefix.stem}_{sex.value}"
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
