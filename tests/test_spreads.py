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
                ("CHALLENGE", "STRENGTH", "GUIDANCE", "OUTCOME"),
                ("PRESENT", "CHALLENGE", "PAST", "FUTURE", "POTENTIAL"),
                (
                    "CURRENT STATE",
                    "INFLUENCE",
                    "OBSTACLE",
                    "PAST",
                    "POSSIBILITY",
                    "ADVICE",
                    "OUTCOME",
                ),
            },
            patterns,
        )

    def test_spread_selector_labels_are_unique(self) -> None:
        labels = [spread.selector_label for spread in SPREADS]
        self.assertEqual(len(labels), len(set(labels)))


if __name__ == "__main__":
    unittest.main()
