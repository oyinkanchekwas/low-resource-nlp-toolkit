# Technical scope

The toolkit operates on text supplied by the caller. Normalisation preserves diacritics by default. Routing compares lexical and character evidence in caller-supplied profiles, with configurable abstention thresholds.

Scores are relative to the supplied routes and evidence. They are not calibrated probabilities. Profile construction, language coverage, code-mixing, and domain affect the interpretation of a route. A corpus-language label does not establish the language of every token or the correct destination in an application.

Token audits return evidence spans and original character offsets. The full output includes source text. Aggregate output contains counts and a code-switch ratio without text or profile identifiers.

Emotion mappings require explicit category aliases or supplied dimensional coordinates. Numerical ratings need finite scale bounds, a source description, and an annotation perspective. Their interpretation depends on the source instrument and population.

The package contains no dataset, model weights, or bundled language lexicon. The mechanical examples test software operations. Language-identification performance requires a separate evaluation with suitable reference labels.

## Compatibility

Routing and auditing require explicit profiles in version 0.4.0.dev1. The earlier automatic category aliases, coordinates, and category-list constant have been removed. Existing callers need to supply the relevant configuration.

Historical version 0.3.0 benchmark figures remain associated with that version. New profile configurations need their own evaluation.
