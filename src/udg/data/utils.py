import abc
import json
import random
import typing as t
from pathlib import Path

import attr

from udg.features import HouseholdFeature, PersonFeature

T = t.TypeVar("T")
DATA = Path(__file__).parent.parent / "_data"


def load_json(relative_path: str) -> dict:
    path = DATA / relative_path
    with path.open() as f:
        return json.load(f)


class RangeDict(dict, t.Generic[T]):
    def __init__(self, mapping: dict[tuple[int, int], T]) -> None:
        total = sum(end - start + 1 for start, end in mapping)
        data = {
            k: v for (start, end), v in mapping.items() for k in range(start, end + 1)
        }

        if len(data) != total:
            raise ValueError("Overlapping ranges are not allowed")

        super().__init__(data)

    def __setitem__(self, key: tuple[int, int], value: T) -> None:
        start, end = key
        for k in range(start, end + 1):
            super().__setitem__(k, value)

    def __getitem__(self, key: int) -> T:
        return super().__getitem__(key)


class Sampler(abc.ABC, t.Generic[T]):
    @abc.abstractmethod
    def sample(self) -> T:
        pass


@attr.define
class BinomialSampler(Sampler, t.Generic[T]):
    _probability: float

    def sample(self) -> bool:
        return random.random() < self._probability


@attr.define
class MultinomialSampler(Sampler, t.Generic[T]):
    _values: list[T]
    _probabilities: list[float]

    def sample(self) -> T:
        return random.choices(self._values, weights=self._probabilities)[0]


@attr.define
class ConditionalSampler(t.Generic[T]):
    _data: dict
    _hierarchy: list[type[HouseholdFeature] | type[PersonFeature]] = attr.field(
        init=False,
        factory=list,
    )

    def __attrs_post_init__(self) -> None:
        data = self._data
        while not isinstance(data, Sampler):
            key, data = next(iter(data.items()))

            key_type = type(key)
            if key_type in self._hierarchy:
                raise ValueError(f"Duplicate key type: {key_type}")

            self._hierarchy.append(key_type)

    def sample(self, *args: t.Any) -> T:
        params = {type(arg): arg for arg in args}

        data = self._data
        for feature_type in self._hierarchy:
            data = data[params[feature_type]]

        return data.sample()  # type: ignore[attr-defined]
