# Historical AfriSenti benchmark

The published routing figures concern [version 0.3.0](https://github.com/oyinkanchekwas/low-resource-nlp-toolkit/tree/v0.3.0). Its profile definitions and implementation differ from the configurable routing interface in this development version.

The [original benchmark report](https://github.com/oyinkanchekwas/low-resource-nlp-toolkit/blob/v0.3.0/docs/benchmark.md) records the data revision, split, threshold selection, aggregate results, and uncertainty analysis. Those results have not been reassigned to the current implementation.

The [pinned dataset repository](https://github.com/afrisenti-semeval/afrisent-semeval-2023/tree/5aec3cfcf87b59f885e98641f72e52182776429d) states CC BY 4.0 and requests citations to [AfriSenti](https://aclanthology.org/2023.emnlp-main.862/), [the shared task](https://aclanthology.org/2023.semeval-1.315/), [NaijaSenti](https://aclanthology.org/2022.lrec-1.63/), and [ASAB](https://aclanthology.org/2020.coling-main.91/). The dataset paper's ethics statement restricts commercial and state-actor use without creator approval. Check the applicable conditions before using or distributing source records or derived resources.

The current benchmark runner requires an explicit profile file and local dataset files. Downloading data requires the separate `--download` option. The package contains no source tweets.
