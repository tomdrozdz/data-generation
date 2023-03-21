import json
import random

from rich.pretty import pprint

from udg import Builder, TrafficModel
from udg.data import wroclaw
from udg.utils import collect_generators

if __name__ == "__main__":
    generator_classes = collect_generators(wroclaw.z_palca)
    generators = (generator_cls() for generator_cls in generator_classes)

    builder = Builder(*generators)

    random.seed(42)
    traffic_model = builder.build_model(household_number=2)

    serialized = traffic_model.to_dict()
    as_json = json.dumps(serialized, indent=2)
    print(as_json)

    deserialized = TrafficModel.from_dict(serialized)
    pprint(deserialized)
