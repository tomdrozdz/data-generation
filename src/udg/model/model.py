import datetime as dt
import typing as t
from xml.etree import ElementTree as ET

import attr

from udg.features.base import HouseholdFeature, PersonFeature
from udg.features.household import PersonNumber
from udg.features.person import Schedule
from udg.features.person.schedule import SetLengthStop
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

    def to_matsim_xml(self) -> ET.Element:
        person = ET.Element("person", id=self.id)
        features = self.features.copy()
        schedule: Schedule = features.pop(Schedule)  # type: ignore[assignment]

        attributes = ET.SubElement(person, "attributes")
        for key, value in features.items():
            attribute = ET.SubElement(attributes, "attribute", name=key.__name__)
            attribute.text = str(value)

        plan = ET.SubElement(person, "plan", selected="yes")
        for stop in schedule.stops:
            assert isinstance(stop, SetLengthStop)
            ET.SubElement(
                plan,
                "activity",
                facility_id=stop.place.id,
                x=str(stop.place.x),
                y=str(stop.place.y),
                end_time=(
                    dt.datetime.combine(dt.date(2, 2, 2), stop.start_time)
                    + stop.duration
                ).strftime("%H:%M:%S"),
            )
            ET.SubElement(plan, "leg", mode=stop.transport_mode.value)

        return person


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

    def to_matsim_xml(self) -> t.Iterator[ET.Element]:
        yield from (person.to_matsim_xml() for person in self.persons)


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

    @property
    def household_count(self) -> int:
        return len(self.households)

    @property
    def person_count(self) -> int:
        return sum(household.person_number for household in self.households)

    def to_matsim_xml(self) -> ET.ElementTree:
        population = ET.Element("population")
        root = ET.ElementTree(population)

        population.extend(
            person
            for household in self.households
            for person in household.to_matsim_xml()
        )

        ET.indent(root)
        return root
