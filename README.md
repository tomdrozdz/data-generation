# Urban Data Generation

## Usage

The project uses `hatch` as a project manager. In order to install it run:

```bash
pip install hatch
```

To create a Python wheel and install it run:

```bash
hatch build
pip install dist/udg-*.whl
```

## Examples

You can also run examples using `hatch` and the development environment:

```
hatch run example:data-generation
hatch run example:feature-tree
hatch run example:serialization
hatch run example:validation
hatch run example:real
```

## Data

Some of the original data sources used in the project are unavailable on GitHub due to
privacy concerns. The data might not also be available online without registration or special access. However, all the necessary information has been extracted and is a part of the repository in the `_data` directory.

All the scripts that were used to extract the data can be found in the [scripts/data](scripts/data) directory.

List of used data sources:

* [Kompleksowe Badanie Ruchu 2018](https://bip.um.wroc.pl/artykul/565/37499/kompleksowe-badania-ruchu-we-wroclawiu-i-otoczeniu-kbr-2018) - used files include:
  * `EtapII-REJONY_wroclaw.shp`
  * `Etap V - 1.1_Ankiety w gospodarstwach domowych - Wrocław.xlsx`
* [Wrocławska Diagnoza Społeczna 2017](https://www.repozytorium.uni.wroc.pl/publication/94542/edition/89133/wroclawska-diagnoza-spoleczna-2017-raport-z-badan-socjologicznych-nad-mieszkancami-miasta-kajdanek-katarzyna-red-pluta-jacek-red) - data in tabular form, unavailable online.
* [Narodowy Spis Powszechny 2011](https://bdl.stat.gov.pl/bdl/start) - downloaded using the data browser on GUS`s website.
* [Gospodarstwa domowe i rodziny. Charakterystyka demograficzna - NSP 2011](https://stat.gov.pl/spisy-powszechne/nsp-2011/nsp-2011-wyniki/gospodarstwa-domowe-i-rodziny-charakterystyka-demograficzna-nsp-2011,5,1.html) - data in tabular form, downloaded from the provided website.

## Scripts

The project also includes a few scripts for visualization and planning trips of agents using the OpenTripPlanner API. To use the planner you need to have a running instance of OpenTripPlanner. The necessary Dockerfile can be found in the [otp](otp) directory.

## Naming scheme

The project makes use of namespaces so the generator names can stay short:

```
udg.data.<city>.<source>.<generator>
```

e.g.:

```python
from udg.data import wroclaw

generator = wroclaw.kbr.TransportModeDecisionTree()
```

## Notes

* We are assuming that there is a hierarchy of features, first we get the Household
  features, then based on those we generate Person features. For now households cannot
  depend on family or personal features.
* The data used for the presentation was generated using the setup in [examples/real.py](examples/real.py) script.
