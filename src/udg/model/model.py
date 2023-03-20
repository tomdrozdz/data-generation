import attr

from udg.features.base import HouseholdFeature, PersonFeature
from udg.features.household import PersonNumber
from udg.features.person import Schedule


@attr.define
class Person:
    schedule: Schedule

    features: dict[type[PersonFeature], PersonFeature]


@attr.define
class Household:
    person_number: PersonNumber
    persons: list[Person]

    features: dict[type[HouseholdFeature], HouseholdFeature]


@attr.define
class TrafficModel:
    households: list[Household]
