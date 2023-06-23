import datetime as dt
import enum
import random

import polars as pl

from udg.data.generator import Generator
from udg.data.utils import (
    AgeRange,
    AgeRangeDict,
    BinomialSampler,
    ConditionalSampler,
    DecisionTree,
    MultinomialSampler,
    NormalSampler,
    load_csv,
    load_json,
)
from udg.features.family import BikeNumber, CarNumber, PersonNumber
from udg.features.household.home import Home
from udg.features.person import Age, Schedule, Sex, TransportPreferences
from udg.features.person.schedule import SetEndStop, SetLengthStop
from udg.types import Place, Region, Time, TransportMode


class DestinationType(enum.Enum):
    HOME = "home"
    WORK = "work"
    SCHOOL = "school"
    UNIVERSITY = "university"
    ADULTS_ENTERTAINMENT = "adults_entertainment"
    CULTURE = "culture_and_entertainment"
    GASTRONOMY = "gastronomy"
    GROCERIES = "grocery_shopping"
    HEALTH = "healthcare"
    LEISURE = "leisure_time_schools"
    OFFICIAL_MATTERS = "official_matters"
    OTHER = "other"
    OTHER_SHOPPING = "other_shopping"
    PHARMACY = "pharmacy"
    RELIGION = "religion"
    SERVICES = "services"
    SPORT = "sport"

    def __str__(self) -> str:
        return str(self.value)


class ScheduleMaker(Generator[Schedule]):
    def __init__(self) -> None:
        self._any_travel = ConditionalSampler[bool](
            data=load_json(
                "wroclaw/unsorted/any_travel.json",
                structure=[AgeRange, Sex],
                out=BinomialSampler,
            )
        )

        self._cancel_trip = ConditionalSampler[bool](
            data=load_json(
                "wroclaw/unsorted/trip_cancel.json",
                structure=[DestinationType],
                out=BinomialSampler,
            )
        )

        self._start_hour = ConditionalSampler[int](
            data=load_json(
                "wroclaw/unsorted/start_hour.json",
                structure=[DestinationType, int],
                out=MultinomialSampler,
            )
        )

        self._travel_chains = ConditionalSampler[str](
            data=load_json(
                "wroclaw/unsorted/travel_chains.json",
                structure=[AgeRange, Sex, str],
                out=MultinomialSampler,
            )
        )

        self._other_travels = ConditionalSampler[DestinationType](
            data=load_json(
                "wroclaw/unsorted/other_travels.json",
                structure=[AgeRange, Sex, DestinationType],
                out=MultinomialSampler,
            )
        )

        self._spend_time = ConditionalSampler[int](
            data=load_json(
                "wroclaw/unsorted/spend_time.json",
                structure=[AgeRange, Sex, DestinationType, str],
                out=NormalSampler,
            )
        )

        self._gravities = ConditionalSampler[Region](
            data=load_json(
                "wroclaw/unsorted/gravities.json",
                structure=[DestinationType, Region, Region],
                out=MultinomialSampler,
            )
        )

        self._distances: dict[Region, dict[Region, float]] = load_json(
            "wroclaw/unsorted/distances.json",
            structure=[Region, Region],
        )

        self._transport_modes = DecisionTree.from_pickle(
            "wroclaw/kbr/transport_mode.pkl",
            out=TransportMode,
        )

        self._age_brackets = AgeRangeDict(
            {
                AgeRange("6-15"): 0,
                AgeRange("16-19"): 1,
                AgeRange("20-24"): 2,
                AgeRange("25-44"): 3,
                AgeRange("45-65"): 4,
                AgeRange("66-100"): 5,
            }
        )

        self._facilities = load_csv("wroclaw/osm/facilities.csv")
        self._tag_mapping = load_json(
            "osm/tag_mappings.json",
            structure=[DestinationType],
            out=set,
        )

    def _region_to_place(self, region: Region, dest_type: DestinationType) -> Place:
        tags = self._tag_mapping[dest_type]
        filtered = self._facilities.filter(
            pl.col("tag").is_in(tags) & (pl.col("region_id") == region)
        )

        if filtered.is_empty():
            # TODO: Is this really the correct approach? Isn't it better to take
            # anything in the region?
            filtered = self._facilities.filter(pl.col("tag").is_in(tags))

        id_, region_id, x, y = (
            filtered.sample()
            .select(
                "id",
                "region_id",
                "x",
                "y",
            )
            .row(0)
        )
        return Place(id=id_, region=Region(region_id), x=x, y=y)

    def generate(
        self,
        person_number: PersonNumber,
        car_number: CarNumber,
        bike_number: BikeNumber,
        age: Age,
        sex: Sex,
        home: Home,
        transport_preferences: TransportPreferences,
    ) -> Schedule:
        if age <= 5:
            return Schedule(stops=[])

        if not self._any_travel.sample(age, sex):
            return Schedule(stops=[])

        stops: list[SetEndStop | SetLengthStop] = []
        age_bracket = self._age_brackets[age]
        dest_region = home.region

        first_dest_str, *travel_chain = self._travel_chains.sample(age, sex).split(",")
        first_dest = (
            DestinationType(first_dest_str)
            if first_dest_str != "inne"
            else self._other_travels.sample(age, sex)
        )

        if not self._cancel_trip.sample(first_dest):
            start_time = Time(
                hour=self._start_hour.sample(first_dest),
                minute=random.randint(0, 59),
            )
            spend_time = dt.timedelta(
                minutes=round(self._spend_time.sample(age, sex, first_dest))
            )
            dest_region = self._gravities.sample(first_dest, home.region)
            transport_mode = self._transport_modes.predict(
                *transport_preferences.as_input(),
                person_number,
                age_bracket,
                car_number,
                bike_number,
                self._distances[home.region][dest_region],
            )

            stops.append(
                SetLengthStop(
                    start_time=start_time,
                    place=self._region_to_place(dest_region, first_dest),
                    transport_mode=transport_mode,
                    duration=spend_time,
                )
            )

        current_region = dest_region
        for dest_str in travel_chain:
            dest = (
                DestinationType(dest_str)
                if dest_str != "inne"
                else self._other_travels.sample(age, sex)
            )

            if self._cancel_trip.sample(dest):
                continue

            start_time = start_time + spend_time
            spend_time = dt.timedelta(
                minutes=round(self._spend_time.sample(age, sex, dest))
            )
            dest_region = (
                self._gravities.sample(dest, current_region)
                if dest is not DestinationType.HOME
                else home.region
            )
            transport_mode = self._transport_modes.predict(
                *transport_preferences.as_input(),
                person_number,
                age_bracket,
                car_number,
                bike_number,
                self._distances[current_region][dest_region],
            )

            stops.append(
                SetLengthStop(
                    start_time=start_time,
                    place=self._region_to_place(dest_region, dest),
                    transport_mode=transport_mode,
                    duration=spend_time,
                )
            )

            current_region = dest_region

        return Schedule(stops=stops)
