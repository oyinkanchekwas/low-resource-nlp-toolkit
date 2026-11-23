# Emotion labels and ratings

Emotion categories and dimensional ratings describe different annotation choices. The label functions keep category names unless a mapping is supplied. Coordinates are returned when they are supplied with a scale, source, and annotation perspective.

```python
from low_resource_nlp import RatingScale, label_to_valence_arousal

category = label_to_valence_arousal("joy")
print(category.canonical, category.valence, category.arousal)

scale = RatingScale(0, 1, source="your dataset", perspective="reader", version="1")
rating = label_to_valence_arousal("0.5#0.7", scale=scale)
print(rating.valence, rating.arousal, rating.scale)
```

`RatingScale` specifies the common lower and upper bounds for valence and arousal. Both ratings must be finite and lie within those bounds. The source and perspective should describe the material and annotation procedure used for the ratings. Record the resource version when available.

For a dataset with an explicit category mapping, pass `aliases`. To attach dimensional coordinates from an authorised resource, pass `coordinates` with a `RatingScale`. Use the resource's own licence, citation, and access conditions when preparing or sharing the mapping.

```python
aliases = {"happy": "joy"}
coordinates = {"joy": (0.5, 0.7)}
result = label_to_valence_arousal("happy", aliases=aliases, coordinates=coordinates, scale=scale)
```

The command line accepts a dimensional pair with its metadata:

```bash
low-resource-nlp label '0.5#0.7' --scale-min 0 --scale-max 1 --source 'your dataset' --perspective reader
```

## Migrating from 0.3.0

Category labels no longer receive coordinates automatically. `other`, `none`, and `neutral` remain separate. Applications that require a dataset-specific mapping can pass their own `aliases` and `coordinates`. Inputs containing a numeric pair require a `RatingScale`; `parse_label_va` remains available for parsing a pair without assigning its meaning.
