import abc
import typing as t

import attr

from udg.features.base import HouseholdFeature, PersonFeature

ThingToGenerate = t.TypeVar(
    "ThingToGenerate",
    bound=HouseholdFeature
    | PersonFeature
    | tuple[HouseholdFeature, ...]
    | tuple[PersonFeature, ...],
)


@attr.define
class Generator(abc.ABC, t.Generic[ThingToGenerate]):
    @abc.abstractmethod
    def generate(self, *args, **kwargs) -> ThingToGenerate:
        pass
