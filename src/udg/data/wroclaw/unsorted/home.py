import polars as pl

from udg.data.generator import Generator
from udg.data.utils import MultinomialSampler, load_csv, load_json
from udg.features.household import Home
from udg.types import Region


class HomeSampler(Generator[Home]):
    def __init__(self) -> None:
        self._regions_sampler = MultinomialSampler.from_dict(
            load_json(
                "wroclaw/unsorted/region.json",
                structure=[Region],
            )
        )

        self._facilities = load_csv("wroclaw/osm/facilities.csv")
        self._tag_mapping = load_json(
            "osm/tag_mappings.json",
            structure=[str],
            out=set,
        )

    def _region_to_place(self, region: Region, dest_type: str) -> Home:
        tags = self._tag_mapping[dest_type]
        filtered = self._facilities.filter(
            pl.col("tag").is_in(tags) & (pl.col("region_id") == region)
        )

        if filtered.is_empty():
            filtered = self._facilities.filter(pl.col("tag").is_in(tags))

        id_, region_id, x, y = (
            filtered.sample()
            .select(
                "id",
                "region_id",
                "x",
                "y",
            )
            .row(0)
        )

        return Home(id=id_, region=Region(region_id), x=x, y=y)

    def generate(self) -> Home:
        region = self._regions_sampler.sample()
        return self._region_to_place(region, "home")
