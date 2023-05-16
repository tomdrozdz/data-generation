import datetime as dt
import enum
import random

from udg.data.generator import Generator
from udg.data.utils import (
    AgeRange,
    BinomialSampler,
    ConditionalSampler,
    MultinomialSampler,
    NormalSampler,
    load_json,
)
from udg.features.person import Age, Schedule, Sex
from udg.features.person.schedule import SetEndStop, SetLengthStop


class Destination(enum.Enum):
    HOME = "dom"
    WORK = "praca"
    SCHOOL = "szkola"
    UNIVERSITY = "uczelnia"
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
                structure=[Destination],
                out=BinomialSampler,
            )
        )

        self._start_hour = ConditionalSampler[int](
            data=load_json(
                "wroclaw/unsorted/start_hour.json",
                structure=[Destination, int],
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

        self._other_travels = ConditionalSampler[Destination](
            data=load_json(
                "wroclaw/unsorted/other_travels.json",
                structure=[AgeRange, Sex, Destination],
                out=MultinomialSampler,
            )
        )

        self._spend_time = ConditionalSampler[int](
            data=load_json(
                "wroclaw/unsorted/spend_time.json",
                structure=[AgeRange, Sex, Destination, str],
                out=NormalSampler,
            )
        )

    def generate(self, age: Age, sex: Sex) -> Schedule:
        if age <= 5:
            return Schedule(stops=[])

        if not self._any_travel.sample(age, sex):
            return Schedule(stops=[])

        stops: list[SetEndStop | SetLengthStop] = []

        travel_chain = self._travel_chains.sample(age, sex).split(",")
        first_destination_str = travel_chain[0]
        first_destination = (
            Destination(first_destination_str)
            if first_destination_str != "inne"
            else self._other_travels.sample(age, sex)
        )

        start_time = dt.time(
            hour=self._start_hour.sample(first_destination),
            minute=random.randint(0, 59),
        )
        spend_time = dt.timedelta(
            minutes=round(self._spend_time.sample(age, sex, first_destination))
        )

        if not self._cancel_trip.sample(first_destination):
            stops.append(
                SetLengthStop(
                    start_time=start_time,
                    place=first_destination.value,
                    duration=spend_time,
                )
            )

        for destination_str in travel_chain[1:]:
            destination = (
                Destination(destination_str)
                if destination_str != "inne"
                else self._other_travels.sample(age, sex)
            )

            start_time = (
                dt.datetime.combine(dt.date(1, 1, 1), start_time) + spend_time
            ).time()
            spend_time = dt.timedelta(
                minutes=round(self._spend_time.sample(age, sex, destination))
            )

            if not self._cancel_trip.sample(destination):
                stops.append(
                    SetLengthStop(
                        start_time=start_time,
                        place=destination.value,
                        duration=spend_time,
                    )
                )

        return Schedule(stops=stops)
