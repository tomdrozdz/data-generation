import typing as t
from dataclasses import dataclass

from feature import Feature
from household import CarNumber, PersonNumber
from person import Age, Schedule, Sex, TransportMode


@dataclass
class Person:
    BASIC_FEATURES: t.ClassVar[list[type[Feature]]] = [Age, Sex, TransportMode]

    schedule: Schedule

    features: dict
    user_defined_extras: dict


@dataclass
class Household:
    BASIC_FEATURES: t.ClassVar[list[type[Feature]]] = [CarNumber]

    person_number: PersonNumber
    persons: list[Person]

    features: dict
    user_defined_extras: dict


@dataclass
class TrafficModel:
    households: list[Household]
