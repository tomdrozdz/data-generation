from pprint import pprint

import inputs
from builder import Builder
from extras import Wealth, WealthGenerator
from utils import collect_generators

if __name__ == "__main__":
    generators = collect_generators(inputs)
    builder = Builder(
        *generators,
        WealthGenerator,
        household_extras=[Wealth],
    )

    traffic_model = builder.build_model(household_number=2)
    pprint(traffic_model)
