#!/usr/bin/env python3

import argparse
from pathlib import Path
from xml.etree import ElementTree as ET

import polars as pl


def facilities_to_xml(data: pl.DataFrame) -> ET.ElementTree:
    facilities = ET.Element("facilities")
    root = ET.ElementTree(facilities)

    for row in data.iter_rows(named=True):
        ET.SubElement(
            facilities,
            "facility",
            id=str(row["id"]),
            x=str(row["x"]),
            y=str(row["y"]),
        )

        # ET.SubElement(facility, "activity", type=str(row["type"]))

    ET.indent(root)
    return root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("output_file", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data = pl.read_csv(args.input_file)
    xml = facilities_to_xml(data)
    xml.write(args.output_file, xml_declaration=True)


if __name__ == "__main__":
    main()
