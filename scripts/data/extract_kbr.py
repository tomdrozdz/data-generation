#!/usr/bin/env python3

import argparse
import json
import pickle
from enum import Enum
from pathlib import Path

import geopandas as gpd
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

REGIONS_FILE = (
    Path(__file__).parent.parent.parent / "data" / "kbr" / "EtapII-REJONY_wroclaw.shp"
)
SURVEYS_FILE = (
    Path(__file__).parent.parent.parent
    / "data"
    / "kbr"
    / "Etap V - 1.1_Ankiety w gospodarstwach domowych - Wrocław.xlsx"
)
DISTANCES = (
    Path(__file__).parent.parent.parent / "data" / "processed" / "distances.json"
)


class Features(Enum):
    REGIONS = "regions"
    TRANSPORT_MODE = "transport_mode"

    def __str__(self) -> str:
        return self.value


def read_regions() -> gpd.GeoDataFrame:
    return gpd.read_file(REGIONS_FILE)


def read_surveys() -> pd.DataFrame:
    data = pd.read_excel(
        SURVEYS_FILE,
        "Wrocław_ankiety+podróże",
        engine="openpyxl",
        header=[0, 1],
        nrows=14241,
    )
    data.columns = [f"{i}_{j}" for i, j in data.columns]
    return data


def read_distances() -> dict[str, dict[str, float]]:
    return json.loads(DISTANCES.read_text())


def extract_regions() -> gpd.GeoDataFrame:
    regions = read_regions()

    regions = regions[["NUMBER", "NAME", "geometry"]]
    regions = regions.rename(columns={"NUMBER": "region_id", "NAME": "name"})
    regions = regions.to_crs("EPSG:2177")
    # regions['centroid'] = regions['geometry'].centroid

    return regions


def extract_transport_mode() -> bytes:
    data = read_surveys()
    distances = read_distances()

    data = data[
        [
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jak Pan/Pani ocenia wygodę jazdy pojazdami komunikacji zbiorowej?\xa0",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jak Pan/Pani ocenia\xa0punktualność\xa0komunikacji zbiorowej\xa0we Wrocławiu?\xa0",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jak ocenia Pan/Pani efekty dotychczasowych działań związanych z rozbudową systemu rowerowego we Wrocławiu (dróg i\xa0parkingów rowerowych)?",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [niekorzystne ustawienia sygnalizacji świetlnej]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [brak chodników i konieczność poruszania się jezdnią/poboczem/wydeptaną ścieżką]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [zły stan nawierzchni chodników]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [zastawianie chodników przez parkujące samochody]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [niebezpieczne zachowania kierowców]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [zagrożenie ze strony rowerzystów poruszających się chodnikami]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [zbyt wysokie krawężniki]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [brak bieżącego utrzymania czystości/odśnieżania]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [niewystarczająca liczba przejść dla pieszych]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [brak miejsc wypoczynku na trasie dojścia (np. ławki, zieleń)]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [uciążliwy ruch kołowy]",
            "PREFERENCJE DOT. MOBILNOŚCI MIEJSKIEJ_Jakie elementy stanowią dla Pana/Pani największa uciążliwość w codziennych podróżach pieszych po Wrocławiu (można wskazać maksymalnie 3 odpowiedzi) [niewłaściwe oświetlenie ciągów pieszych]",
            "DANE O GOSPODARSTWIE DOMOWYM_Liczba osób w gospodarstwie domowym [ogółem]",
            "DANE O GOSPODARSTWIE DOMOWYM_Liczba środków transportu w gospodarstwie domowym [Samochód prywatny, zarejestrowany na osobę z gosp. domowego]",
            "DANE O GOSPODARSTWIE DOMOWYM_Liczba środków transportu w gospodarstwie domowym [Samochód prywatny, nie zarejestrowany na osobę z gosp. domowego [użyczone]]",
            "DANE O GOSPODARSTWIE DOMOWYM_Liczba środków transportu w gospodarstwie domowym [Samochód służbowy]",
            "DANE O GOSPODARSTWIE DOMOWYM_Liczba środków transportu w gospodarstwie domowym [Rower]",
            "DANE O RESPONDENCIE_Przedział wiekowy",
            'OPIS PODRÓŻY "ŹRÓDŁO"_Nr rejonu',
            'OPIS PODRÓŻY "CEL"_Nr rejonu',
            "23:59:00_środek transportu grupa",
        ]
    ]
    data.columns = [
        "public_transport_comfort",
        "public_transport_punctuality",
        "bike_comfort",
        "PIESZO Niekorzystne ustawienia sygnalizacji świetlnej",
        "PIESZO Brak chodników i konieczność poruszania się jezdnią/poboczem/wydeptaną ścieżką",
        "PIESZO Zły stan nawierzchni chodników",
        "PIESZO Zastawianie chodników przez parkujące samochody",
        "PIESZO Niebezpieczne zachowania kierowców",
        "PIESZO Zagrożenie ze strony rowerzystów poruszających się chodnikami",
        "PIESZO Zbyt wysokie krawężniki",
        "PIESZO Brak bieżącego utrzymania czystości/odśnieżania",
        "PIESZO Niewystarczająca liczba przejść dla pieszych",
        "PIESZO Brak miejsc wypoczynku na trasie dojścia (np. ławki, zieleń)",
        "PIESZO Uciążliwy ruch kołowy",
        "PIESZO Niewłaściwe oświetlenie ciągów pieszych",
        "person_number",
        "private_car",
        "borrowed_car",
        "work_car",
        "bike_number",
        "age_range",
        "source_region",
        "target_region",
        "transport_mode",
    ]

    data = data.dropna()
    data = data[data["transport_mode"] != "inne"]

    data["car_number"] = data["private_car"] + data["borrowed_car"] + data["work_car"]

    regions_unique = set(distances.keys())
    data = data[
        (data["source_region"].astype("int").astype("str").isin(regions_unique))
        & (data["target_region"].astype("int").astype("str").isin(regions_unique))
    ]

    def _add_regions_num(row: pd.Series) -> pd.Series:
        row["distance"] = distances[str(round(row["source_region"]))][
            str(round(row["target_region"]))
        ]

        return row

    data = data.apply(_add_regions_num, axis=1)

    yes_no_mapping = {
        "Nie": 0,
        "nie": 0,
        "Tak": 1,
        "tak": 1,
    }

    data = data.replace(
        {
            "public_transport_comfort": {
                "bardzo źle": 0,
                "raczej źle": 1,
                "ani dobrze ani źle": 2,
                "nie korzystam z komunikacji zbiorowej": 2,
                "raczej dobrze": 3,
                "bardzo dobrze": 4,
            },
            "public_transport_punctuality": {
                "bardzo źle": 0,
                "raczej źle": 1,
                "ani dobrze ani źle": 2,
                "nie korzystam z komunikacji zbiorowej": 2,
                "raczej dobrze": 3,
                "bardzo dobrze": 4,
            },
            "bike_comfort": {
                "bardzo źle": 0,
                "raczej źle": 1,
                "ani dobrze ani źle": 2,
                "nie korzystam z komunikacji zbiorowej": 2,
                "nie korzystam z systemu dróg i parkingów rowerowych": 2,
                "raczej dobrze": 3,
                "bardzo dobrze": 4,
            },
            "PIESZO Niekorzystne ustawienia sygnalizacji świetlnej": yes_no_mapping,
            "PIESZO Brak chodników i konieczność poruszania się jezdnią/poboczem/wydeptaną ścieżką": yes_no_mapping,
            "PIESZO Zły stan nawierzchni chodników": yes_no_mapping,
            "PIESZO Zastawianie chodników przez parkujące samochody": yes_no_mapping,
            "PIESZO Niebezpieczne zachowania kierowców": yes_no_mapping,
            "PIESZO Zagrożenie ze strony rowerzystów poruszających się chodnikami": yes_no_mapping,
            "PIESZO Zbyt wysokie krawężniki": yes_no_mapping,
            "PIESZO Brak bieżącego utrzymania czystości/odśnieżania": yes_no_mapping,
            "PIESZO Niewystarczająca liczba przejść dla pieszych": yes_no_mapping,
            "PIESZO Brak miejsc wypoczynku na trasie dojścia (np. ławki, zieleń)": yes_no_mapping,
            "PIESZO Uciążliwy ruch kołowy": yes_no_mapping,
            "PIESZO Niewłaściwe oświetlenie ciągów pieszych": yes_no_mapping,
            "age_range": {
                "6-15 (dzieci)": 0,
                "16-19 (młodzież)": 1,
                "20-24 (wiek studencki)": 2,
                "25-44 (młodsi pracownicy)": 3,
                "45-60 (starsi pracownicy kobiety)": 4,
                "45-65 (starsi pracownicy mężczyźni)": 4,
                "61 i więcej (emeryci kobiety)": 5,
                "66 i więcej (emeryci mężczyźni)": 5,
            },
            "transport_mode": {
                "komunikacja samochodowa": "car",
                "komunikacja zbiorowa": "public_transport",
                "pieszo": "pedestrian",
                "rower": "bike",
            },
        }
    )

    data["pedestrian_inconvenience"] = 0
    for c in data.columns:
        if c.startswith("PIESZO "):
            data["pedestrian_inconvenience"] += data[c]

    x = data[
        [
            "public_transport_comfort",
            "public_transport_punctuality",
            "bike_comfort",
            "pedestrian_inconvenience",
            "person_number",
            "age_range",
            "car_number",
            "bike_number",
            "distance",
        ]
    ]
    y = data["transport_mode"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.33,
        random_state=42,
    )
    classifier = DecisionTreeClassifier(random_state=42, max_depth=20)
    classifier.fit(x_train.values, y_train.values)
    y_pred = classifier.predict(x_test.values)

    print(classification_report(y_test, y_pred))

    return pickle.dumps(classifier)


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
        case Features.TRANSPORT_MODE:
            data = extract_transport_mode()

    if isinstance(data, gpd.GeoDataFrame):
        data.to_file(args.output_file)
    elif isinstance(data, bytes):
        args.output_file.write_bytes(data)
    else:
        args.output_file.write_text(json.dumps(data, indent=4) + "\n")


if __name__ == "__main__":
    main()
