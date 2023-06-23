import abc
import logging
import pickle
import typing as t
from pathlib import Path
from threading import Lock

import attr
import numpy as np
import orjson
import polars as pl
from sklearn.tree import DecisionTreeClassifier

from udg.features import FamilyFeature, HouseholdFeature, PersonFeature
from udg.features.person import Age

logger = logging.getLogger(__name__)

DATA = Path(__file__).parent.parent / "_data"
T = t.TypeVar("T")
I = t.TypeVar("I", bound=int)


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
    data = orjson.loads(path.read_text())
    return _structure_dict(data, structure, out)


def load_csv(relative_path: str) -> pl.DataFrame:
    return pl.read_csv(DATA / relative_path)


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

    _rng: np.random.Generator = attr.field(init=False, factory=np.random.default_rng)
    _lock: Lock = attr.field(init=False, factory=Lock)

    def sample(self) -> bool:
        with self._lock:
            value = self._rng.random()

        return value < self._probability


@attr.define
class NormalSampler(Sampler):
    _loc: float
    _scale: float

    _rng: np.random.Generator = attr.field(init=False, factory=np.random.default_rng)
    _lock: Lock = attr.field(init=False, factory=Lock)

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> t.Self:
        return cls(loc=data["loc"], scale=data["scale"])

    def sample(self) -> float:
        with self._lock:
            return self._rng.normal(loc=self._loc, scale=self._scale)


@attr.define
class MultinomialSampler(Sampler, t.Generic[T]):
    _values: list[T]
    _probabilities: np.ndarray

    _indices: np.ndarray = attr.field(init=False)

    _rng: np.random.Generator = attr.field(init=False, factory=np.random.default_rng)
    _lock: Lock = attr.field(init=False, factory=Lock)

    @classmethod
    def from_dict(cls, data: dict[T, float]) -> t.Self:
        values, probabilities = zip(*data.items())
        return cls(values=list(values), probabilities=np.array(probabilities))

    def __attrs_post_init__(self) -> None:
        self._indices = np.arange(len(self._values))

    def sample(self) -> T:
        with self._lock:
            index = self._rng.choice(self._indices, p=self._probabilities)

        return self._values[index]


@attr.define
class ConditionalSampler(t.Generic[T]):
    _data: dict
    _hierarchy: list[
        type[HouseholdFeature] | type[PersonFeature] | type[FamilyFeature]
    ] = attr.field(
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

    def sampler_for(self, *args: t.Any) -> Sampler:
        params = {type(arg): arg for arg in args}

        data = self._data
        for feature_type in self._hierarchy:
            data = data[params[feature_type]]

        return data  # type: ignore[return-value]

    def sample(self, *args: t.Any, **kwargs: t.Any) -> T:
        return self.sampler_for(*args).sample(**kwargs)


@attr.define
class DynamicMultinomialSampler(Sampler, t.Generic[I]):
    _classic_sampler: MultinomialSampler[I]

    _current: list[I] = attr.field(init=False)
    _buffer_size: int = attr.field(default=1000)
    _resample_size: int = attr.field(default=200)

    _min_value: I = attr.field(init=False)
    _max_value: I = attr.field(init=False)
    _replace_size: int = attr.field(init=False)

    _rng: np.random.Generator = attr.field(init=False, factory=np.random.default_rng)
    _lock: Lock = attr.field(init=False, factory=Lock)

    def __attrs_post_init__(self) -> None:
        self._current = [self._sample() for _ in range(self._buffer_size)]

        self._min_value = min(self._classic_sampler._values)
        self._max_value = max(self._classic_sampler._values)
        self._replace_size = self._buffer_size - self._resample_size

    @classmethod
    def from_dict(cls, data: dict[I, float]) -> t.Self:
        return cls(classic_sampler=MultinomialSampler.from_dict(data))

    def _sample(self) -> I:
        return self._classic_sampler.sample()

    def _resample_current(self) -> None:
        self._current[self._replace_size :] = [
            self._sample() for _ in range(self._resample_size)
        ]

    def _find_value(self, from_: int, to: int) -> tuple[int, I] | None:
        return next(
            (
                (index, value)
                for index, value in enumerate(self._current)
                if from_ <= value <= to
            ),
            None,
        )

    def sample(self, from_: int | None = None, to: int | None = None) -> I:
        from_ = from_ or self._min_value
        to = to or self._max_value
        to_replace = self._sample()

        with self._lock:
            found = self._find_value(from_, to)

            while not found:
                logger.warning(
                    "Resampling buffer for (%s, %s) (%s)",
                    from_,
                    to,
                    id(self),
                )
                self._resample_current()
                found = self._find_value(from_, to)

            index, value = found
            self._current[index] = to_replace

        return value

    @staticmethod
    def _sort_by_value(t: tuple[int, I]) -> I:
        return t[1]

    def sample_normal(
        self,
        mu: int,
        sigma: int,
        from_: int | None = None,
        to: int | None = None,
    ) -> I:
        from_ = from_ or self._min_value
        to = to or self._max_value
        to_replace = self._sample()

        with self._lock:
            index_value = [
                (index, value)
                for index, value in enumerate(self._current)
                if from_ <= value <= to
            ]
            index_value.sort(key=self._sort_by_value)

            indices, values = zip(*index_value)
            values_np = np.array(values)

            # Approximate the probabilities from a normal distribution
            probabilities = np.exp(-0.5 * ((values_np - mu) / sigma) ** 2) / (
                sigma * np.sqrt(2 * np.pi)
            )
            probabilities = probabilities / probabilities.sum()

            index = self._rng.choice(indices, p=probabilities)
            value = self._current[index]
            self._current[index] = to_replace

        return value


@attr.define
class DecisionTree(t.Generic[T]):
    _classifier: DecisionTreeClassifier
    _out: type[T]

    @classmethod
    def from_pickle(cls, relative_path: str, out: type[T]) -> t.Self:
        path = DATA / relative_path
        return cls(classifier=pickle.loads(path.read_bytes()), out=out)

    def predict(self, *args: t.Any) -> T:
        return self._out(self._classifier.predict(np.array([args]))[0])  # type: ignore[call-arg]
