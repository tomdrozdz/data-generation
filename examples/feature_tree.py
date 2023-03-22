from udg import Generator, ModelDefinition
from udg.data import wroclaw
from udg.features import HouseholdFeature
from udg.features.household import CarNumber
from udg.utils import collect_generators
from udg.visualization import AsciiFeatureTree


class Wealth(HouseholdFeature, str):
    pass


class WealthGenerator(Generator[Wealth]):
    def generate(self, car_number: CarNumber) -> Wealth:
        return Wealth("moderate")


if __name__ == "__main__":
    generator_classes = collect_generators(wroclaw.z_palca)
    generators = (generator_cls() for generator_cls in generator_classes)

    model_definition = ModelDefinition.from_generators(
        *generators,
        WealthGenerator(),
    )

    AsciiFeatureTree(model_definition).print()
