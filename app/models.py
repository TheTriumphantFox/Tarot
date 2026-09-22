from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrientationMeaning:
    keywords: tuple[str, ...]
    text: str


@dataclass(frozen=True)
class Card:
    id: str
    name: str
    arcana: str
    suit: str | None
    rank: str | None
    upright: OrientationMeaning
    reversed: OrientationMeaning


@dataclass(frozen=True)
class ControlState:
    frequency: int = 437
    resonance: int = 50
    drift: int = 0
    direction: str = "forward"
    filter_mode: str = "low"

    def as_seed_data(self) -> dict[str, int | str]:
        return {
            "direction": self.direction,
            "drift": self.drift,
            "filter_mode": self.filter_mode,
            "frequency": self.frequency,
            "resonance": self.resonance,
        }


@dataclass(frozen=True)
class ReadingResult:
    card: Card
    reversed: bool
    meaning: OrientationMeaning
    draw_number: int
    master_seed_hex: str
    interaction_digest_hex: str

