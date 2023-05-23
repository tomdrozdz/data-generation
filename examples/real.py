from pathlib import Path

from rich.pretty import pprint

from udg import Builder, ModelDefinition
from udg.data import wroclaw
from udg.utils import collect_generators

if __name__ == "__main__":
    print("---------------------------------------------------------------------------")
    generator_classes = [
        *collect_generators(wroclaw.unsorted),
        *collect_generators(wroclaw.wds2017),
    ]
    generators = (generator_cls() for generator_cls in generator_classes)

    model_definition = ModelDefinition.from_generators(
        *generators,
    )

    builder = Builder(model_definition)
    traffic_model = builder.build_model(household_number=2)

    pprint(traffic_model)

    save_file = Path(__file__).parent.parent / "matsim.xml"
    traffic_model.to_matsim_xml().write(save_file, xml_declaration=True)
