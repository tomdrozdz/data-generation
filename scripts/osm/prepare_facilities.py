#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.geometry import Point


def download_amenities(place: str) -> gpd.GeoDataFrame:
    ox.settings.timeout = 600
    tags = {"amenity": True}

    gdf = ox.geometries_from_place(place, tags).reset_index()

    columns = ["osmid", "amenity", "name", "geometry"]
    gdf_sub = gdf[columns]
    gdf_sub = gdf_sub.to_crs("EPSG:2177")
    gdf_sub["geometry"] = gdf_sub["geometry"].centroid

    return gdf_sub


def download_buildings(place: str) -> gpd.GeoDataFrame:
    ox.settings.timeout = 600
    tags = {"building": True}

    gdf = ox.geometries_from_place(place, tags).reset_index()

    columns = ["osmid", "building", "name", "geometry"]
    gdf_sub = gdf[columns]
    gdf_sub = gdf_sub.to_crs("EPSG:2177")
    gdf_sub["area"] = gdf_sub["geometry"].area
    gdf_sub["geometry"] = gdf_sub["geometry"].centroid

    return gdf_sub


def download_shops(place: str) -> gpd.GeoDataFrame:
    ox.settings.timeout = 600
    tags = {"shop": True}

    gdf = ox.geometries_from_place(place, tags).reset_index()

    columns = ["osmid", "shop", "name", "geometry"]
    gdf_sub = gdf[columns]
    gdf_sub = gdf_sub.to_crs("EPSG:2177")
    gdf_sub["geometry"] = gdf_sub["geometry"].centroid

    return gdf_sub


def get_region_id(regions: gpd.GeoDataFrame, point: Point) -> int:
    for _, region_id, _, region_polygon, *_ in regions.itertuples():
        if point.within(region_polygon):
            return region_id

    return -1


def transform_geodata(
    gdf: gpd.GeoDataFrame,
    regions: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    gdf["region_id"] = gdf.apply(
        lambda r: get_region_id(regions, r["geometry"]),
        axis=1,
    )
    gdf["x"] = gdf.apply(lambda r: str(r["geometry"].coords[0][0]), axis=1)
    gdf["y"] = gdf.apply(lambda r: str(r["geometry"].coords[0][1]), axis=1)

    return gdf


def process_sub_df(df: pd.DataFrame, category: str) -> pd.DataFrame:
    df["id"] = df.apply(lambda r: category + "_" + str(r["osmid"]), axis=1)
    df["category"] = category
    df = df.rename(columns={category: "tag"})
    df = df[["id", "category", "tag", "name", "region_id", "x", "y"]]

    return df


def prepare_facilities(
    place: str,
    regions: gpd.GeoDataFrame,
    config: dict,
) -> pd.DataFrame:
    buildings_min_area = config["buildings_min_area"]
    buildings_tags_to_leave = config["buildings_tags_to_leave"]
    shops_tags_to_leave = config["shops_tags_to_leave"]
    shops_tags_mapping = config["shops_tags_mapping"]
    amenities_tags_to_leave = config["amenities_tags_to_leave"]
    amenities_tags_mapping = config["amenities_tags_mapping"]

    buildings = download_buildings(place)
    buildings = buildings[buildings["area"] > buildings_min_area]
    buildings = buildings[buildings["building"].isin(buildings_tags_to_leave)]
    buildings = transform_geodata(buildings, regions)

    shops = download_shops(place)
    shops = shops[shops["shop"].isin(shops_tags_to_leave)]
    shops = shops.replace(shops_tags_mapping)
    shops = transform_geodata(shops, regions)

    amenities = download_amenities(place)
    amenities = amenities[amenities["amenity"].isin(amenities_tags_to_leave)]
    amenities = amenities.replace(amenities_tags_mapping)
    amenities = transform_geodata(amenities, regions)

    buildings = process_sub_df(buildings, "building")
    shops = process_sub_df(shops, "shop")
    amenities = process_sub_df(amenities, "amenity")
    facilities = pd.concat([shops, amenities, buildings])

    return facilities


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("place")
    parser.add_argument("regions_path", type=Path)
    parser.add_argument("output_path", type=Path)
    parser.add_argument(
        "--config-path",
        type=Path,
        default=Path(__file__).parent / "config.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    regions = gpd.read_file(args.regions_path)
    config = json.loads(args.config_path.read_text())

    data = prepare_facilities(args.place, regions, config)
    data.to_csv(args.output_path, index=False)


if __name__ == "__main__":
    main()
