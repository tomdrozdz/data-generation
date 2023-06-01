import datetime as dt
import random

from udg.data.generator import Generator
from udg.features.household import CarNumber, PersonNumber
from udg.features.person import Age, Schedule, Sex
from udg.features.person.schedule import SetEndStop, SetLengthStop


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
            SetEndStop(place="University", end_time=dt.time(15, 15)),
            SetLengthStop(place="Restaurant", duration=dt.timedelta(hours=1)),
        ]

        return Schedule(stops=stops)
