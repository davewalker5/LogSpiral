import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from morphological_similarity import ShellPreset, compare_presets, display_names


class MorphologicalSimilarityTests(unittest.TestCase):
    def test_identical_values_score_full_similarity(self):
        left = ShellPreset(
            filename="left",
            name="Left",
            classification={"family": "ammonoid", "geometry": "log-spiral"},
        )
        right = ShellPreset(
            filename="right",
            name="Right",
            classification={"family": "ammonoid", "geometry": "log-spiral"},
        )

        comparison = compare_presets(left, right, {"family": 1.0, "geometry": 1.0})

        self.assertEqual(comparison.score, 1.0)
        self.assertEqual(comparison.matched_weight, 2.0)
        self.assertEqual(comparison.compared_weight, 2.0)

    def test_absent_from_both_fields_are_excluded(self):
        left = ShellPreset("left", "Left", {"family": "ammonoid"})
        right = ShellPreset("right", "Right", {"family": "ammonoid"})

        comparison = compare_presets(
            left,
            right,
            {"family": 1.0, "umbilicus": 10.0},
        )

        self.assertEqual(comparison.score, 1.0)
        self.assertEqual(comparison.compared_weight, 1.0)
        self.assertEqual([field.field for field in comparison.fields], ["family"])

    def test_absent_from_one_shell_counts_as_difference(self):
        left = ShellPreset("left", "Left", {"family": "ammonoid", "umbilicus": "wide"})
        right = ShellPreset("right", "Right", {"family": "ammonoid"})

        comparison = compare_presets(
            left,
            right,
            {"family": 1.0, "umbilicus": 1.0},
        )

        self.assertEqual(comparison.score, 0.5)
        self.assertEqual(
            [field.field for field in comparison.differing_fields],
            ["umbilicus"],
        )

    def test_weights_change_relative_score(self):
        left = ShellPreset(
            "left",
            "Left",
            {"family": "ammonoid", "geometry": "log-spiral"},
        )
        right = ShellPreset(
            "right",
            "Right",
            {"family": "gastropod", "geometry": "log-spiral"},
        )

        comparison = compare_presets(left, right, {"family": 3.0, "geometry": 1.0})

        self.assertEqual(comparison.score, 0.25)

    def test_duplicate_display_names_include_filename(self):
        presets = [
            ShellPreset("orthocone", "Orthocone-Like Shell", {}),
            ShellPreset("cyrtocone", "Orthocone-Like Shell", {}),
            ShellPreset("ammonite", "Ammonite-Like Shell", {}),
        ]

        names = display_names(presets)

        self.assertEqual(names["orthocone"], "Orthocone-Like Shell (orthocone)")
        self.assertEqual(names["cyrtocone"], "Orthocone-Like Shell (cyrtocone)")
        self.assertEqual(names["ammonite"], "Ammonite-Like Shell")


if __name__ == "__main__":
    unittest.main()
