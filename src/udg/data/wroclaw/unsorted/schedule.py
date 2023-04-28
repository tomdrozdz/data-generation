import datetime as dt
import enum

import cattrs

from udg.data.generator import Generator
from udg.data.utils import (
    BinomialSampler,
    ConditionalSampler,
    MultinomialSampler,
    load_json,
)
from udg.features.person import Age, Schedule, Sex
from udg.features.person.schedule import SetEndStop, SetLengthStop

# class DayScheduleSampler:
#     def __init__(
#         self,
#         travel_chains_dist: dict[str, dict[str, float]],
#         start_hour_dist: dict[str, dict[str, float]],
#         other_travels_dist: dict[str, dict[str, float]],
#         spend_time_dist_params: dict[str, dict[str, dict[str, int]]],
#     ) -> None:
#         Parameters
#         ----------
#             travel_chains_dist: dict
#                 Dictionary
#                 {age_sex: str : {
#                     travel_chain: str : probability: float}
#                 }
#                 contains probabilities for specific chains of destinations,
#                 ordered according to their sequence of execution.
#             start_hour_dist: dict
#                 Dictionary
#                 {dest_type: str : {
#                     hour: str : probability: float}
#                 }
#                 contains probabilities for start hours for travel with
#                 specific destination type. Sampled hour will be converted
#                 to int.
#             other_travels_dist: dict
#                 Dictionary
#                 {age_sex: str : {
#                     other_place_type: str : probability: float}
#                 }}
#                 contains probabilities of performing an activity from
#                 the available subcategories for the category "inne".
#             spend_time_dist_params: dict
#                 Dictionary
#                 {age_sex: str : {
#                     place_type: str : {
#                         "loc" : mean_minutes: int,
#                         "scale" : std_minutes: int
#                     }
#                 }}

#         self.travel_chains_samplers = {}
#         for age_sex, dist in travel_chains_dist.items():
#             self.travel_chains_samplers[age_sex] = BaseSampler(dist)

#         self.start_hours_samplers = {}
#         for dest_type, dist in start_hour_dist.items():
#             self.start_hours_samplers[dest_type] = BaseSampler(dist)

#         self.other_travels_samplers = {}
#         for age_sex, dist in other_travels_dist.items():
#             self.other_travels_samplers[age_sex] = BaseSampler(dist)

#         self.spend_time_samplers = {}
#         for age_sex in spend_time_dist_params.keys():
#             self.spend_time_samplers[age_sex] = {}
#             for place_type, params in spend_time_dist_params[age_sex].items():
#                 self.spend_time_samplers[age_sex][place_type] = BaseNormalSampler(
#                     loc=params["loc"], scale=params["scale"], min_value=10
#                 )

#     def __call__(self, age_sex: str) -> list[ScheduleElement]:
#         schedule = []

#         if age_sex != "0-5":
#             any_travel = self.any_travel_samplers[age_sex]()

#             if any_travel == "1":
#                 travel_chain = self.travel_chains_samplers[age_sex]().split(",")

#                 first_destination = travel_chain[0]

#                 if first_destination == "inne":
#                     first_destination_with_other_split = self.other_travels_samplers[
#                         age_sex
#                     ]()
#                 else:
#                     first_destination_with_other_split = first_destination

#                 first_start_time = (
#                     int(self.start_hours_samplers[first_destination]()) * 60
#                     + self._sample_minutes()
#                 )
#                 first_spend_time = self.spend_time_samplers[age_sex][
#                     first_destination_with_other_split
#                 ]()

#                 if (
#                     self.trip_cancel_prob[first_destination_with_other_split]
#                     <= np.random.random()
#                 ):
#                     # do not cancel this trip, so add it to schedule
#                     schedule.append(
#                         ScheduleElement(
#                             travel_start_time=first_start_time,
#                             dest_activity_type=first_destination_with_other_split,
#                             dest_activity_dur_time=first_spend_time,
#                         )
#                     )

#                 prev_start_time = first_start_time
#                 prev_spend_time = first_spend_time

#                 for next_destination in travel_chain[
#                     1:
#                 ]:  # will work fine (min travels in chain = 2)
#                     if next_destination == "inne":
#                         next_destination_with_other_split = self.other_travels_samplers[
#                             age_sex
#                         ]()
#                     else:
#                         next_destination_with_other_split = next_destination

#                     next_start_time = prev_start_time + prev_spend_time
#                     next_spend_time = self.spend_time_samplers[age_sex][
#                         next_destination_with_other_split
#                     ]()

#                     if (
#                         self.trip_cancel_prob[next_destination_with_other_split]
#                         <= np.random.random()
#                     ):
#                         # do not cancel this trip, so add it to schedule
#                         schedule.append(
#                             ScheduleElement(
#                                 travel_start_time=next_start_time,
#                                 dest_activity_type=next_destination_with_other_split,
#                                 dest_activity_dur_time=next_spend_time,
#                             )
#                         )
#                     prev_start_time = next_start_time
#                     prev_spend_time = next_spend_time

#         return schedule

#     def _sample_minutes(self) -> int:
#         return int(np.random.uniform(0, 60))


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
        any_travel_data = cattrs.structure(
            load_json("wroclaw/unsorted/any_travel.json"),
            dict[Sex, dict[Age, dict]],
        )
        self._any_travel = ConditionalSampler[bool](
            data={
                sex: {
                    age: MultinomialSampler(
                        values=[bool(int(k)) for k in dd],
                        probabilities=[v for v in dd.values()],
                    )
                    for age, dd in d.items()
                }
                for sex, d in any_travel_data.items()
            }
        )

        cancel_trip_data = load_json("wroclaw/unsorted/trip_cancel.json")
        self._cancel_trip = ConditionalSampler[bool](
            data={
                Destination(destination): BinomialSampler(probability=probability)
                for destination, probability in cancel_trip_data.items()
            }
        )

        start_hour_data = load_json("wroclaw/unsorted/start_hour.json")
        self._start_hour = ConditionalSampler[bool](
            data={
                Destination(destination): MultinomialSampler(
                    values=[int(k) for k in d],
                    probabilities=[v for v in d.values()],
                )
                for destination, d in start_hour_data.items()
            }
        )

    def generate(self, age: Age, sex: Sex) -> Schedule:
        if age <= 5:
            return Schedule(stops=[])

        if not self._any_travel.sample(age, sex):
            return Schedule(stops=[])

        print(self._cancel_trip.sample(Destination.SCHOOL))
        print(self._start_hour.sample(Destination.SCHOOL))

        stops: list[SetEndStop | SetLengthStop] = [
            SetEndStop(place="University", end_time=dt.time(15, 15)),
            SetLengthStop(place="Restaurant", duration=dt.timedelta(hours=1)),
        ]

        return Schedule(stops=stops)
