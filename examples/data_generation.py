from rich.pretty import pprint

from udg import Builder, Generator
from udg.data import wroclaw
from udg.features import HouseholdFeature
from udg.features.household import CarNumber
from udg.utils import collect_generators


# Some extra custom feature that the user defines
class Wealth(HouseholdFeature, str):
    pass


class WealthGenerator(Generator[Wealth]):
    def generate(self, car_number: CarNumber) -> Wealth:
        wealth = "poor" if car_number <= 1 else "rich"
        return Wealth(wealth)


if __name__ == "__main__":
    generator_classes = collect_generators(wroclaw.z_palca)
    generators = (generator_cls() for generator_cls in generator_classes)

    builder = Builder(
        *generators,
        WealthGenerator(),
    )

    traffic_model = builder.build_model(household_number=2)
    pprint(traffic_model)
