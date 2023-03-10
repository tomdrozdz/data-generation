import random
import typing as t
from dataclasses import dataclass

from feature import Feature
from generator import Generator
from household import CarNumber, PersonNumber
from person import Age, Schedule, Sex, TransportMode


@dataclass
class PersonNumberSampler(Generator[PersonNumber]):
    REQUIRES = []

    def generate(self, *_) -> PersonNumber:
        person_number = random.choice([1, 2, 3, 4, 5])
        return PersonNumber(person_number)


@dataclass
class CarNumberSampler(Generator[CarNumber]):
    REQUIRES = [PersonNumber]

    def generate(self, requirements: dict[type[Feature], t.Any]) -> CarNumber:
        person_number: PersonNumber = requirements[PersonNumber]

        if person_number <= 1:
            car_number = random.choice([0, 1])
        else:
            car_number = random.choice([0, 1, 2])

        return CarNumber(car_number)


@dataclass
class AgeSampler(Generator[Age]):
    REQUIRES = []

    def generate(self, *_) -> Age:
        age = random.randint(0, 100)
        return Age(age)


@dataclass
class SexSampler(Generator[Sex]):
    REQUIRES = []

    def generate(self, *_) -> Sex:
        sex = random.choice(["M", "F"])
        return Sex(sex)


@dataclass
class TransportModeDecisionTree(Generator[TransportMode]):
    REQUIRES = [Age, Sex]

    def generate(self, requirements: dict[type[Feature], t.Any]) -> TransportMode:
        age = requirements[Age]
        sex = requirements[Sex]

        ...

        transport_mode = random.choice(["car", "public"])
        return TransportMode(transport_mode)


@dataclass
class ScheduleMaker(Generator[Schedule]):
    REQUIRES = [Age, Sex, TransportMode]

    def generate(self, requirements: dict[type[Feature], t.Any]) -> Schedule:
        age = requirements[Age]
        sex = requirements[Sex]
        transport_mode = requirements[TransportMode]

        ...

        schedule = {"1": "University", "2": "Home"}

        return Schedule(schedule)
