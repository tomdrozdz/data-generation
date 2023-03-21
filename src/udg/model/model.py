import typing as t

import attr

from udg.features.base import HouseholdFeature, PersonFeature
from udg.features.household import PersonNumber
from udg.features.person import Schedule

from .serialization import feature_dicts


@attr.define
class Person:
    features: dict[type[PersonFeature], PersonFeature]

    @property
    def schedule(self) -> Schedule:
        return t.cast(Schedule, self.features[Schedule])

    @classmethod
    def from_dict(cls, data: dict) -> t.Self:
        return cls(features=feature_dicts.deserialize(data["features"]))

    def to_dict(self) -> dict:
        return {"features": feature_dicts.serialize(self.features)}


@attr.define
class Household:
    persons: list[Person]

    features: dict[type[HouseholdFeature], HouseholdFeature]

    @property
    def person_number(self) -> PersonNumber:
        return t.cast(PersonNumber, self.features[PersonNumber])

    @classmethod
    def from_dict(cls, data: dict) -> t.Self:
        return cls(
            persons=[Person.from_dict(d) for d in data["persons"]],
            features=feature_dicts.deserialize(data["features"]),
        )

    def to_dict(self) -> dict:
        return {
            "persons": [person.to_dict() for person in self.persons],
            "features": feature_dicts.serialize(self.features),
        }


@attr.define
class TrafficModel:
    households: list[Household]

    @classmethod
    def from_dict(cls, data: dict) -> t.Self:
        return cls(households=[Household.from_dict(d) for d in data["households"]])

    def to_dict(self) -> dict:
        return {"households": [household.to_dict() for household in self.households]}
