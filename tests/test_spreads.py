from __future__ import annotations

import unittest

from app.ui import SPREADS


class SpreadCatalogTests(unittest.TestCase):
    def test_all_supported_draw_patterns_are_available(self) -> None:
        patterns = {spread.positions for spread in SPREADS}
        self.assertEqual(
            {
                ("FOCUS",),
                ("SITUATION", "ADVICE"),
                ("PAST", "PRESENT", "EMERGING"),
                ("MIND", "BODY", "SPIRIT"),
                ("PRESENT", "CHALLENGE", "GUIDANCE", "OUTCOME"),
                ("PRESENT", "CHALLENGE", "PAST", "FUTURE", "POTENTIAL"),
                (
                    "PAST",
                    "PRESENT",
                    "HIDDEN INFLUENCE",
                    "OBSTACLE",
                    "ENVIRONMENT",
                    "ADVICE",
                    "OUTCOME",
                ),
            },
            patterns,
        )

    def test_spread_selector_labels_are_unique(self) -> None:
        labels = [spread.selector_label for spread in SPREADS]
        self.assertEqual(len(labels), len(set(labels)))

    def test_cross_and_horseshoe_use_spatial_layouts(self) -> None:
        spreads = {spread.name: spread for spread in SPREADS}
        self.assertEqual("cross", spreads["Five-Card Cross"].layout)
        self.assertEqual("horseshoe", spreads["Seven-Card Horseshoe"].layout)


if __name__ == "__main__":
    unittest.main()
