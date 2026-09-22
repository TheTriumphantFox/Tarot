from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.deck import CardDataError, load_cards, load_deck


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DeckDataTests(unittest.TestCase):
    def test_prototype_contains_complete_major_arcana(self) -> None:
        cards = load_cards(PROJECT_ROOT / "data" / "cards.json")
        self.assertEqual(22, len(cards))
        self.assertEqual(22, len({card.id for card in cards}))
        self.assertEqual({str(number) for number in range(22)}, {card.rank for card in cards})
        self.assertTrue(all(card.arcana == "major" for card in cards))
        self.assertTrue(all(card.suit is None for card in cards))

    def test_every_orientation_has_keywords_and_meaning(self) -> None:
        cards = load_deck(PROJECT_ROOT / "data")
        for card in cards:
            for meaning in (card.upright, card.reversed):
                self.assertGreaterEqual(len(meaning.keywords), 2)
                self.assertGreaterEqual(len(meaning.text.split()), 20)

    def test_complete_deck_contains_78_unique_cards(self) -> None:
        cards = load_deck(PROJECT_ROOT / "data")
        self.assertEqual(78, len(cards))
        self.assertEqual(78, len({card.id for card in cards}))
        self.assertEqual(22, sum(card.arcana == "major" for card in cards))
        expected_ranks = {
            "Ace", "Two", "Three", "Four", "Five", "Six", "Seven",
            "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King",
        }
        for suit in ("wands", "cups", "swords", "pentacles"):
            suited_cards = [card for card in cards if card.suit == suit]
            self.assertEqual(14, len(suited_cards))
            self.assertEqual(expected_ranks, {card.rank for card in suited_cards})

    def test_missing_required_key_is_rejected(self) -> None:
        malformed = [
            {
                "id": "test",
                "name": "Test",
                "arcana": "major",
                "suit": None,
                "rank": "0",
                "upright": {"keywords": ["one", "two"], "text": "Meaning"},
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cards.json"
            path.write_text(json.dumps(malformed), encoding="utf-8")
            with self.assertRaisesRegex(CardDataError, "missing: reversed"):
                load_cards(path)


if __name__ == "__main__":
    unittest.main()
