import random

from udg.data.generator import Generator
from udg.features.household import PersonNumber


class PersonNumberSampler(Generator[PersonNumber]):
    def generate(self) -> PersonNumber:
        person_number = random.choice([1, 2, 3, 4, 5])
        return PersonNumber(person_number)
