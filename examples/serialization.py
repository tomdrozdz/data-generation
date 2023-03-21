import json
import random

from rich import print_json
from rich.pretty import pprint

from udg import Builder, Generator, TrafficModel
from udg.data import wroclaw
from udg.features import HouseholdFeature
from udg.utils import collect_generators


class Wealth(HouseholdFeature, str):
    pass


class WealthGenerator(Generator[Wealth]):
    def generate(self) -> Wealth:
        return Wealth("moderate")


if __name__ == "__main__":
    generator_classes = collect_generators(wroclaw.z_palca)
    generators = (generator_cls() for generator_cls in generator_classes)

    builder = Builder(*generators)

    random.seed(42)
    traffic_model = builder.build_model(household_number=2)

    serialized = traffic_model.to_dict()
    print_json(json.dumps(serialized))

    deserialized = TrafficModel.from_dict(serialized)
    pprint(deserialized)
