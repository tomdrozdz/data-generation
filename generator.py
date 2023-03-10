import abc
import typing as t
from dataclasses import dataclass

from feature import Feature

ThingToGenerate = t.TypeVar("ThingToGenerate", bound=Feature, covariant=True)


@dataclass
class Generator(abc.ABC, t.Generic[ThingToGenerate]):
    REQUIRES: t.ClassVar[list[type[Feature]]]

    @abc.abstractmethod
    def generate(self, requirements: dict[type[Feature], t.Any]) -> ThingToGenerate:
        pass
