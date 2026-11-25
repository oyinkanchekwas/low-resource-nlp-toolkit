# Technical scope

The toolkit normalises text and compares language profiles with words and character patterns. Normalisation preserves diacritics by default. You can set confidence and score-margin thresholds to leave weak matches unassigned.

Scores sum weighted lexical and character matches. Confidence is the highest route score divided by the sum of positive route scores, with zero returned for an empty sum. Probability estimates require calibration against annotated outcomes. Profile construction, language coverage, code-mixing, and domain affect the interpretation of a route. Corpus-language labels describe whole messages. Token-level assessment and application routing require reference labels matched to those tasks.

To examine code-switching, compare the suggested language for each word with the surrounding sentence. Character positions link each result to the input text. Use `to_dict()` to read the text alongside the results, or `to_aggregate_dict()` for counts and the code-switch ratio.

Emotion mappings use category aliases or dimensional coordinates. Numerical ratings need finite scale bounds, a source description, and an annotation perspective. Their interpretation depends on the source instrument and population.

The examples use a small test vocabulary. Evaluate language identification with independently labelled examples that match your task.

## Compatibility

Language routing requires profiles in version 0.4.0.dev2. Set category aliases and dimensional coordinates through the corresponding function arguments. Update imports that used the removed category-list constant.

Historical version 0.3.0 benchmark figures remain associated with that version. New profile configurations need their own evaluation.
