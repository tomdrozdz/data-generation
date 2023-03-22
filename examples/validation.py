from udg import Generator, ModelDefinition
from udg.features import HouseholdFeature, PersonFeature
from udg.features.household import CarNumber, PersonNumber


class Wealth(HouseholdFeature, PersonFeature, str):
    pass


class WealthGenerator(Generator[Wealth]):
    def generate(self) -> Wealth:
        return Wealth("moderate")


class PersonNumberGenerator(Generator[PersonNumber]):
    def generate(self, car_number: CarNumber) -> PersonNumber:
        return PersonNumber(42)


if __name__ == "__main__":
    ModelDefinition.from_generators(
        WealthGenerator(),
        PersonNumberGenerator(),
        PersonNumberGenerator(),
    )
