# Urban Data Generation (working title)

## Examples

```
hatch run examples:data-generation
```

```
hatch run examples:dependency-tree
```

```
hatch run examples:serialization
```

(`pip install hatch`)

## Naming scheme

We will make use of namespaces so the generator names will stay short:

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
  depend on personal features.
