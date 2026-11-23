import json
import tempfile
import unittest
from pathlib import Path

from profile_fixture import PROFILE_DATA, test_router

from low_resource_nlp import audit_code_switching, load_profiles
from low_resource_nlp.cli import main
from low_resource_nlp.routing import LanguageProfile, LexicalLanguageRouter


class ProfileTests(unittest.TestCase):
    def load(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return load_profiles(path)

    def test_valid_file(self):
        router = LexicalLanguageRouter(self.load(PROFILE_DATA))
        self.assertEqual(router.route("alpha").language_code, "a")

    def test_default_requires_explicit_profiles(self):
        with self.assertRaises(ValueError):
            LexicalLanguageRouter.default()

    def test_audit_requires_explicit_router(self):
        with self.assertRaises(ValueError):
            audit_code_switching("alpha")

    def test_empty_profiles_fail(self):
        with self.assertRaises(ValueError):
            LexicalLanguageRouter([])

    def test_duplicate_codes_fail(self):
        with self.assertRaises(ValueError):
            LexicalLanguageRouter([LanguageProfile("a", "A", keywords=("alpha",))] * 2)

    def test_invalid_profile_values_fail(self):
        profiles = [
            LanguageProfile("", "A", keywords=("alpha",)),
            LanguageProfile("a", ""),
            LanguageProfile("und", "A", keywords=("alpha",)),
            LanguageProfile("ambiguous", "A", keywords=("alpha",)),
            LanguageProfile("a", "A", keywords="alpha"),
            LanguageProfile("a", "A", keywords=("",)),
        ]
        for profile in profiles:
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                LexicalLanguageRouter([profile])

    def test_invalid_documents_fail(self):
        for data in (
            [],
            {},
            {"source": "", "profiles": []},
            {"source": "test", "profiles": []},
            {"source": "test", "profiles": [{"code": "a", "name": "A", "extra": 1}]},
            {"source": "test", "profiles": [{"code": "a", "name": "A", "keywords": "alpha"}]},
        ):
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.load(data)

    def test_malformed_json_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profiles(path)

    def test_unknown_text_has_no_english_bonus(self):
        router = LexicalLanguageRouter([LanguageProfile("eng", "English", keywords=("alpha",))])
        self.assertEqual(router.route("zzzzqqq").language_code, "und")

    def test_cli_requires_profile_file(self):
        for command in ("route", "audit"):
            with self.subTest(command=command), self.assertRaises(SystemExit):
                main([command, "alpha"])

    def test_direct_and_loaded_profiles_agree(self):
        loaded = LexicalLanguageRouter(self.load(PROFILE_DATA))
        self.assertEqual(loaded.route("alpha beta"), test_router().route("alpha beta"))

    def test_equal_evidence_abstains_at_positive_margin(self):
        decision = test_router().route_selectively("alpha beta", min_score_margin=0.75)
        self.assertFalse(decision.accepted)
        self.assertEqual(decision.abstention_reason, "narrow_score_margin")

    def test_example_profile_file_loads(self):
        path = Path(__file__).resolve().parents[1] / "examples" / "profiles.json"
        router = LexicalLanguageRouter(load_profiles(path))
        self.assertEqual(router.route("alpha amber").language_code, "a")
        self.assertEqual(router.route("beta bravo").language_code, "b")


if __name__ == "__main__":
    unittest.main()
