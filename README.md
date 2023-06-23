# Urban Data Generation (working title)

## Examples

```
hatch run example:data-generation
```

```
hatch run example:feature-tree
```

```
hatch run example:serialization
```

```
hatch run example:validation
```

```
hatch run example:real
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
