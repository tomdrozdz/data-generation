from udg import Builder, Generator
from udg.data import wroclaw
from udg.features import HouseholdFeature
from udg.features.household import CarNumber
from udg.utils import collect_generators
from udg.visualization import ModelTree


class Wealth(HouseholdFeature, str):
    pass


class WealthGenerator(Generator[Wealth]):
    def generate(self, car_number: CarNumber) -> Wealth:
        return Wealth("moderate")


if __name__ == "__main__":
    generator_classes = collect_generators(wroclaw.z_palca)
    generators = (generator_cls() for generator_cls in generator_classes)

    builder = Builder(*generators, WealthGenerator())
    ModelTree(builder).print()
