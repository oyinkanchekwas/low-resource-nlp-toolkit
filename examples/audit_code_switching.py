"""Audit language evidence in short code-switched text."""

from low_resource_nlp import audit_code_switching


def main() -> None:
    samples = [
        "abeg make una check this model output",
        "Ẹ káàrọ̀, this result looks useful",
        "sannu ina lafiya, please review the data",
    ]

    for text in samples:
        report = audit_code_switching(text)
        print(f"\n{text}")
        print(f"dominant={report.dominant_language_code} mix={dict(report.language_mix)}")
        print(f"warnings={list(report.warnings)}")
        for span in report.spans:
            print(f"  {span.language_code}\t{span.text}")


if __name__ == "__main__":
    main()
