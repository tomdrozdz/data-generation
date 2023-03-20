# TODO:

* JSON serialization and deserialization using `cattrs` (should be simple).
* Maybe add an option to draw a nice dependency tree of features.

# Example

```
hatch run examples:data-generation
```

(`pip install hatch`)

# Naming scheme

We will make use of namespaces so the generator names will stay short:

```
udg.data.<city>.<source>.<generator>
```

e.g.:

```python
from udg.data import wroclaw

generator = wroclaw.kbr.TransportModeDecisionTree()
```

# Notes

* We are assuming that there is a hierarchy of features, first we get the Household
  features, then based on those we generate Person features. For now households cannot
  depend on personal features.

* Na razie cechy `PersonNumber` w `Household` i `Schedule` w `Person` są zdefiniowane
  osobno, bo ułatwia to trochę kod w `Builder`, chyba nie będzie sytuacji gdzie jedna
  z tych cech nie będzie występować.
