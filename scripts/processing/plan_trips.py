#!/usr/bin/env python3

import argparse
import json
import typing as t
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import pyproj
import tqdm

from udg.features.household import Home
from udg.model.model import Household, Person, TrafficModel
from udg.types import TransportMode

transformer = pyproj.Transformer.from_crs(2177, 4326, always_xy=True)
transport_mode_mapping = {
    TransportMode.CAR: "CAR",
    TransportMode.PUBLIC_TRANSPORT: "TRANSIT",
    TransportMode.BIKE: "BICYCLE",
    TransportMode.PEDESTRIAN: "WALK",
}


def _process_person(
    client: httpx.Client,
    household: Household,
    person: Person,
) -> list[str]:
    plans: list[str] = []

    home: Home = household.features[Home]  # type: ignore[assignment]
    previous_lon, previous_lat = transformer.transform(home.x, home.y)

    trip = 1
    for stop in person.schedule.stops:
        lon, lat = transformer.transform(stop.place.x, stop.place.y)

        if stop.transport_mode != TransportMode.PUBLIC_TRANSPORT:
            previous_lon, previous_lat = lon, lat
            continue

        response = client.get(
            "",
            params={
                "fromPlace": f"{previous_lat},{previous_lon}",
                "toPlace": f"{lat},{lon}",
                "date": "2023-06-19",
                "time": stop.start_time,  # type: ignore[dict-item]
                "arriveBy": True,
                "mode": transport_mode_mapping[stop.transport_mode],
            },
        )

        previous_lon, previous_lat = lon, lat
        try:
            plan = response.json()["plan"]["itineraries"]
        except KeyError:
            print("OTP OSM error")
            continue

        plans.extend(
            ",".join(
                (
                    person.id,
                    str(trip),
                    str(i),
                    leg["mode"],
                    leg["legGeometry"]["points"],
                    str(leg["startTime"]),
                    str(leg["endTime"]),
                    leg.get("agencyId", ""),
                    leg.get("routeId", ""),
                    leg.get("tripId", ""),
                    leg.get("from", {}).get("stopId", ""),
                    leg.get("to", {}).get("stopId", ""),
                )
            )
            for part in plan
            for i, leg in enumerate(part["legs"], start=1)
        )
        trip += 1

    return plans


def plan_trips(model: TrafficModel, otp_plan_url: str) -> t.Iterator[str]:
    people = [
        (household, person)
        for household in model.households
        for family in household.families
        for person in family.persons
    ]
    total = len(people)

    with (
        httpx.Client(base_url=otp_plan_url) as client,
        tqdm.tqdm(total=total) as pbar,
        ThreadPoolExecutor(max_workers=10) as executor,
    ):
        for data in executor.map(
            _process_person,
            (client for _ in range(total)),
            (household for household, _ in people),
            (person for _, person in people),
        ):
            yield "\n".join(data) + "\n" if data else ""
            pbar.update(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file", type=Path)
    parser.add_argument("output_file", type=Path)

    parser.add_argument(
        "--otp-plan-url",
        default="http://localhost:8080/otp/routers/default/plan",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data = json.loads(args.input_file.read_text())
    traffic_model = TrafficModel.from_dict(data)

    with args.output_file.open("w") as f:
        f.write(
            "person_id,trip_id,leg_id,mode,geometry,start_time,end_time,agency_id,route_id,pt_trip,from_stop,to_stop\n"
        )
        for trip in plan_trips(traffic_model, args.otp_plan_url):
            f.write(trip)


if __name__ == "__main__":
    main()
