import typing as t

import attr

from udg.features.base import HouseholdFeature, PersonFeature
from udg.features.household import PersonNumber
from udg.features.person import Schedule
from udg.utils import generate_id

from ..serialization import feature_dicts


@attr.define
class Person:
    id: str = attr.field(factory=generate_id, kw_only=True)
    features: dict[type[PersonFeature], PersonFeature]

    @property
    def schedule(self) -> Schedule:
        return t.cast(Schedule, self.features[Schedule])

    @classmethod
    def from_dict(cls, data: dict) -> t.Self:
        return cls(
            id=data["id"],
            features=feature_dicts.deserialize(data["features"]),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "features": feature_dicts.serialize(self.features),
        }


@attr.define
class Household:
    id: str = attr.field(factory=generate_id, kw_only=True)
    persons: list[Person]
    features: dict[type[HouseholdFeature], HouseholdFeature]

    @property
    def person_number(self) -> PersonNumber:
        return t.cast(PersonNumber, self.features[PersonNumber])

    @classmethod
    def from_dict(cls, data: dict) -> t.Self:
        return cls(
            id=data["id"],
            persons=[Person.from_dict(d) for d in data["persons"]],
            features=feature_dicts.deserialize(data["features"]),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "persons": [person.to_dict() for person in self.persons],
            "features": feature_dicts.serialize(self.features),
        }


@attr.define
class TrafficModel:
    id: str = attr.field(factory=generate_id, kw_only=True)
    households: list[Household]

    @classmethod
    def from_dict(cls, data: dict) -> t.Self:
        return cls(
            id=data["id"],
            households=[Household.from_dict(d) for d in data["households"]],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "households": [household.to_dict() for household in self.households],
        }
