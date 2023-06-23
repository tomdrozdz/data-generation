import datetime as dt
import random

from udg.data.generator import Generator
from udg.features.family import CarNumber, PersonNumber
from udg.features.household import FamilyNumber
from udg.features.person import Age, Schedule, Sex
from udg.features.person.schedule import SetEndStop, SetLengthStop
from udg.types import Place, Region, Time, TransportMode


class FamilyNumberSampler(Generator[FamilyNumber]):
    def generate(self) -> FamilyNumber:
        family_number = random.choice([1, 2, 3])
        return FamilyNumber(family_number)


class PersonNumberSampler(Generator[PersonNumber]):
    def generate(self) -> PersonNumber:
        person_number = random.choice([1, 2, 3, 4, 5])
        return PersonNumber(person_number)


class CarNumberSampler(Generator[CarNumber]):
    def generate(self, person_number: PersonNumber) -> CarNumber:
        if person_number <= 1:
            car_number = random.choice([0, 1])
        else:
            car_number = random.choice([0, 1, 2])

        return CarNumber(car_number)


class AgeSexSampler(Generator[tuple[Age, Sex]]):
    def generate(self) -> tuple[Age, Sex]:
        age = random.randint(0, 100)
        sex = random.choice(["M", "F"])
        return Age(age), Sex(sex)


class ScheduleMaker(Generator[Schedule]):
    def generate(self, age: Age, sex: Sex) -> Schedule:
        ...

        stops: list[SetEndStop | SetLengthStop] = [
            SetEndStop(
                start_time=Time(hour=8),
                place=Place(id="1", region=Region(1), x=1, y=1),
                transport_mode=TransportMode.CAR,
                end_time=Time(hour=8),
            ),
            SetLengthStop(
                start_time=Time(hour=8),
                place=Place(id="2", region=Region(2), x=2, y=2),
                transport_mode=TransportMode.CAR,
                duration=dt.timedelta(hours=1),
            ),
        ]

        return Schedule(stops=stops)
