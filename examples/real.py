from rich.pretty import pprint

from udg import Builder, ModelDefinition
from udg.data import Generator, wroclaw
from udg.utils import collect_generators
from udg.visualization import AsciiFeatureTree

if __name__ == "__main__":
    print("---------------------------------------------------------------------------")
    generator_classes: list[type[Generator]] = [
        wroclaw.unsorted.home.HomeSampler,
        wroclaw.unsorted.schedule.ScheduleMaker,
        wroclaw.unsorted.transport_preferences.TransportPreferencesSampler,
        wroclaw.wds2017.bike_number.BikeNumberSampler,
        wroclaw.wds2017.car_number.CarNumberSampler,
        *collect_generators(wroclaw.census),
    ]
    generators = (generator_cls() for generator_cls in generator_classes)

    model_definition = ModelDefinition.from_generators(*generators)

    builder = Builder(model_definition)

    traffic_model = builder.build_model(household_number=2)
    pprint(traffic_model)

    AsciiFeatureTree(model_definition).print()
