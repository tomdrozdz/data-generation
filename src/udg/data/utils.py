import abc
import json
import random
import typing as t
from pathlib import Path

import attr

from udg.features import HouseholdFeature, PersonFeature
from udg.features.person import Age

T = t.TypeVar("T")
DATA = Path(__file__).parent.parent / "_data"


def _structure_dict(
    data: dict,
    structure: list[t.Callable] | None,
    out: t.Callable | None,
) -> t.Any:
    if not structure:
        if out is None:
            return data

        return out(data)

    cls, *rest = structure
    dict_func = AgeRangeDict if cls is AgeRange else dict

    if not rest and hasattr(out, "from_dict"):
        return out.from_dict(dict_func({cls(k): v for k, v in data.items()}))  # type: ignore[union-attr]

    return dict_func({cls(k): _structure_dict(v, rest, out) for k, v in data.items()})


def load_json(
    relative_path: str,
    structure: list[t.Callable] | None = None,
    out: t.Callable | None = None,
) -> dict:
    path = DATA / relative_path
    with path.open() as f:
        data = json.load(f)

    return _structure_dict(data, structure, out)


class AgeRange:
    def __init__(self, str_repr: str) -> None:
        start_str, _, end_str = str_repr.partition("-")
        self.start, self.end = Age(start_str), Age(end_str)


class AgeRangeDict(dict, t.Generic[T]):
    def __init__(self, mapping: dict[AgeRange, T]) -> None:
        contains_dicts = any(isinstance(v, dict) for v in mapping.values())

        data: dict[Age, T]

        if contains_dicts:
            data = {}
            for age_range, v in mapping.items():
                for k in range(age_range.start, age_range.end + 1):
                    data.setdefault(Age(k), {}).update(v)  # type: ignore[attr-defined,arg-type]
        else:
            data = {
                Age(k): v
                for age_range, v in mapping.items()
                for k in range(age_range.start, age_range.end + 1)
            }

        super().__init__(data)

    def __setitem__(self, key: AgeRange, value: T) -> None:
        for k in range(key.start, key.end + 1):
            super().__setitem__(k, value)

    def __getitem__(self, key: int) -> T:
        return super().__getitem__(key)


class Sampler(abc.ABC, t.Generic[T]):
    @abc.abstractmethod
    def sample(self) -> T:
        pass


@attr.define
class BinomialSampler(Sampler):
    _probability: float

    def sample(self) -> bool:
        return random.random() < self._probability


@attr.define
class NormalSampler(Sampler):
    _loc: float
    _scale: float

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> t.Self:
        return cls(loc=data["loc"], scale=data["scale"])

    def sample(self) -> float:
        return random.gauss(mu=self._loc, sigma=self._scale)


@attr.define
class MultinomialSampler(Sampler, t.Generic[T]):
    _values: list[T]
    _probabilities: list[float]

    @classmethod
    def from_dict(cls, data: dict[T, float]) -> t.Self:
        values, probabilities = zip(*data.items())
        return cls(values=list(values), probabilities=list(probabilities))

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
