"""Mechanical routing fixtures; these codes do not denote languages."""

from low_resource_nlp.routing import LanguageProfile, LexicalLanguageRouter

PROFILE_DATA = {
    "source": "Mechanical test vocabulary",
    "profiles": [
        {
            "code": "a",
            "name": "Test A",
            "keywords": ["alpha", "amber", "acorn"],
            "unique_chars": ["ẹ"],
        },
        {"code": "b", "name": "Test B", "keywords": ["beta", "bravo"]},
        {"code": "c", "name": "Test C", "keywords": ["gamma"]},
    ],
}


def test_router():
    return LexicalLanguageRouter(
        [
            LanguageProfile(
                item["code"],
                item["name"],
                keywords=tuple(item["keywords"]),
                unique_chars=tuple(item.get("unique_chars", [])),
            )
            for item in PROFILE_DATA["profiles"]
        ]
    )
