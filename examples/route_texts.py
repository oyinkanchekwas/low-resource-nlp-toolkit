"""Route sample texts with the default lexical router."""

from low_resource_nlp import LexicalLanguageRouter


def main() -> None:
    router = LexicalLanguageRouter.default()
    samples = [
        "Ẹ káàrọ̀, báwo ni?",
        "abeg make una check this result",
        "sannu, ina lafiya",
        "asante sana kwa msaada",
    ]
    for text in samples:
        decision = router.route(text)
        print(f"{decision.language_code}\t{decision.confidence:.2f}\t{text}")


if __name__ == "__main__":
    main()
