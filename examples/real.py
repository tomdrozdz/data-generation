from rich.pretty import pprint

from udg import Builder, ModelDefinition
from udg.data import wroclaw
from udg.utils import collect_generators

if __name__ == "__main__":
    generator_classes = collect_generators(wroclaw.unsorted)
    generators = (generator_cls() for generator_cls in generator_classes)

    print(list(collect_generators(wroclaw.unsorted)))

    model_definition = ModelDefinition.from_generators(
        *generators,
    )

    builder = Builder(model_definition)
    traffic_model = builder.build_model(household_number=1)
    pprint(traffic_model)

    print("---------------------------------------------------------------------------")
