import abc
import typing as t

import attr

from udg.features.base import FamilyFeature, HouseholdFeature, PersonFeature

ThingToGenerate = t.TypeVar(
    "ThingToGenerate",
    bound=HouseholdFeature
    | FamilyFeature
    | PersonFeature
    | tuple[HouseholdFeature, ...]
    | tuple[FamilyFeature, ...]
    | tuple[PersonFeature, ...],
)


@attr.define
class Generator(abc.ABC, t.Generic[ThingToGenerate]):
    @abc.abstractmethod
    def generate(self, *args, **kwargs) -> ThingToGenerate:
        pass
