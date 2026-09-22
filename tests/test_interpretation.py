from __future__ import annotations

import unittest
from pathlib import Path

from app.deck import load_deck
from app.interpretation import (
    explain_relationship,
    format_spread_reading,
    format_spread_speech,
    format_three_card_reading,
    format_three_card_speech,
)
from app.models import ReadingResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CARDS = load_deck(PROJECT_ROOT / "data")


def reading(card_index: int, *, reversed: bool = False) -> ReadingResult:
    card = CARDS[card_index]
    return ReadingResult(
        card=card,
        reversed=reversed,
        meaning=card.reversed if reversed else card.upright,
        draw_number=card_index + 1,
        master_seed_hex="ab" * 32,
        interaction_digest_hex="cd" * 32,
    )


class InterpretationTests(unittest.TestCase):
    def test_formatted_spread_contains_positions_and_cards(self) -> None:
        results = (reading(9), reading(13, reversed=True), reading(17))
        text = format_three_card_reading(results)
        self.assertIn("PAST — THE HERMIT (UPRIGHT)", text)
        self.assertIn("PRESENT — DEATH (REVERSED)", text)
        self.assertIn("EMERGING — THE STAR (UPRIGHT)", text)
        self.assertNotIn("RELATIONSHIP OF THE CARDS", text)
        self.assertIn("not a fixed prediction", text)

    def test_relationship_identifies_single_reversal_as_pressure_point(self) -> None:
        text = explain_relationship((reading(1), reading(2, reversed=True), reading(7)))
        self.assertIn("single reversal in the Present position", text)
        self.assertIn("hinge of the spread", text)

    def test_relationship_handles_all_upright(self) -> None:
        text = explain_relationship((reading(13), reading(17), reading(21)))
        self.assertIn("All three cards are upright", text)
        self.assertIn("disruption is opening into repair", text)

    def test_narration_uses_spoken_position_labels_without_relationship_section(self) -> None:
        results = (reading(22), reading(36, reversed=True), reading(50))
        text = format_three_card_speech(results)
        self.assertIn("Past. Ace of Wands, upright", text)
        self.assertIn("Present. Ace of Cups, reversed", text)
        self.assertNotIn("Relationship of the cards", text)

    def test_minor_suits_participate_in_relationship_archetypes(self) -> None:
        text = explain_relationship((reading(50), reading(22), reading(36)))
        self.assertIn("hard-won understanding is becoming a decision", text)

    def test_two_card_spread_uses_custom_positions(self) -> None:
        results = (reading(3), reading(7, reversed=True))
        positions = ("SITUATION", "ADVICE")
        text = format_spread_reading(results, positions)
        speech = format_spread_speech(results, positions)
        self.assertIn("SITUATION — THE EMPRESS (UPRIGHT)", text)
        self.assertIn("ADVICE — THE CHARIOT (REVERSED)", text)
        self.assertIn("Situation. The Empress, upright", speech)
        self.assertIn("Advice. The Chariot, reversed", speech)

    def test_seven_card_spread_includes_every_position(self) -> None:
        results = tuple(reading(index) for index in range(7))
        positions = (
            "CURRENT STATE",
            "INFLUENCE",
            "OBSTACLE",
            "PAST",
            "POSSIBILITY",
            "ADVICE",
            "OUTCOME",
        )
        text = format_spread_reading(results, positions)
        for position in positions:
            self.assertIn(f"{position} —", text)
        self.assertIn("not a fixed prediction", text)

    def test_spread_requires_one_position_per_card(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one position"):
            format_spread_reading((reading(1), reading(2)), ("SITUATION",))


if __name__ == "__main__":
    unittest.main()
