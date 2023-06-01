#!/usr/bin/env python3

import argparse
import json
from enum import Enum
from pathlib import Path

import geopandas as gpd

REGIONS_FILE = (
    Path(__file__).parent.parent.parent / "data" / "kbr" / "EtapII-REJONY_wroclaw.shp"
)


class Features(Enum):
    REGIONS = "regions"

    def __str__(self) -> str:
        return self.value


def extract_regions() -> gpd.GeoDataFrame:
    regions = gpd.read_file(REGIONS_FILE)

    regions = regions[["NUMBER", "NAME", "geometry"]]
    regions = regions.rename(columns={"NUMBER": "region_id", "NAME": "name"})
    regions = regions.to_crs("EPSG:2177")
    # regions['centroid'] = regions['geometry'].centroid

    return regions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("feature", type=Features, choices=Features)
    parser.add_argument("output_file", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    match args.feature:
        case Features.REGIONS:
            data = extract_regions()

    if isinstance(data, gpd.GeoDataFrame):
        data.to_file(args.output_file)
    else:
        args.output_file.write_text(json.dumps(data, indent=4, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
