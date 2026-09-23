from __future__ import annotations

import unittest

from app.spreads import SPREADS, SPREADS_BY_LABEL
from app.ui import TarotApp


class SpreadCatalogTests(unittest.TestCase):
    def test_catalog_is_a_large_multi_size_library(self) -> None:
        self.assertGreaterEqual(len(SPREADS), 40)
        self.assertEqual(
            {1, 2, 3, 4, 5, 6, 7, 9, 10, 12},
            {len(spread.positions) for spread in SPREADS},
        )

    def test_original_spreads_remain_available(self) -> None:
        names = {spread.name for spread in SPREADS}
        self.assertTrue(
            {
                "One Card",
                "Situation and Advice",
                "Past, Present, and Emerging",
                "Mind, Body, and Spirit",
                "Four-Card Guidance",
                "Five-Card Cross",
                "Seven-Card Horseshoe",
            }.issubset(names)
        )

    def test_requested_spreads_are_available(self) -> None:
        names = {spread.name for spread in SPREADS}
        self.assertTrue(
            {
                "Situation, Advice, Avoid, and Outcome",
                "Inner Conflict",
                "Self-Love Check-In",
                "Shadow Work",
                "Career Path",
                "Relationship Mirror",
                "Two-Path Decision",
                "Chakra Alignment",
                "Nine-Card Portrait",
                "Year Ahead",
                "Four Elements",
            }.issubset(names)
        )

    def test_catalog_identifiers_and_positions_are_valid(self) -> None:
        names = [spread.name for spread in SPREADS]
        labels = [spread.selector_label for spread in SPREADS]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(labels), len(set(labels)))
        self.assertEqual(len(SPREADS), len(SPREADS_BY_LABEL))
        for spread in SPREADS:
            self.assertTrue(spread.name.strip())
            self.assertTrue(spread.selector_label.strip())
            self.assertTrue(all(position.strip() for position in spread.positions))
            self.assertLessEqual(len(spread.positions), 12)
            self.assertGreaterEqual(spread.image_divisor, 0)

    def test_every_layout_has_renderer_support(self) -> None:
        supported = {
            "row",
            "cross",
            "horseshoe",
            "grid",
            "mirror",
            "pyramid",
            "branches",
            "chakra",
            "compass",
            "celtic_cross",
            "tree",
            "wheel",
        }
        self.assertLessEqual({spread.layout for spread in SPREADS}, supported)

    def test_signature_layouts_are_assigned(self) -> None:
        spreads = {spread.name: spread for spread in SPREADS}
        self.assertEqual("cross", spreads["Five-Card Cross"].layout)
        self.assertEqual("horseshoe", spreads["Seven-Card Horseshoe"].layout)
        self.assertEqual("branches", spreads["Two-Path Decision"].layout)
        self.assertEqual("grid", spreads["Nine-Card Portrait"].layout)
        self.assertEqual("celtic_cross", spreads["Celtic Cross"].layout)
        self.assertEqual("wheel", spreads["Year Ahead"].layout)

    def test_spatial_layouts_place_every_card_inside_the_canvas(self) -> None:
        app = TarotApp.__new__(TarotApp)
        app.scale = 1.0
        for spread in SPREADS:
            coordinates, height = app._spread_geometry(spread, card_height=50)
            if spread.layout == "row":
                self.assertIsNone(coordinates)
                continue
            self.assertIsNotNone(coordinates)
            assert coordinates is not None
            self.assertEqual(len(spread.positions), len(coordinates), spread.name)
            self.assertGreater(height, 0)
            for relx, y in coordinates:
                self.assertGreaterEqual(relx, 0.0, spread.name)
                self.assertLessEqual(relx, 1.0, spread.name)
                self.assertGreaterEqual(y, 0, spread.name)
                self.assertLess(y, height, spread.name)


if __name__ == "__main__":
    unittest.main()
