from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Card, OrientationMeaning


class CardDataError(ValueError):
    """Raised when the local tarot data is incomplete or malformed."""


def load_deck(data_directory: Path) -> tuple[Card, ...]:
    paths = tuple(
        data_directory / filename
        for filename in (
            "cards.json",
            "wands.json",
            "cups.json",
            "swords.json",
            "pentacles.json",
        )
    )
    cards = tuple(card for path in paths for card in load_cards(path))
    ids = [card.id for card in cards]
    if len(ids) != len(set(ids)):
        raise CardDataError("The combined deck contains duplicate card IDs.")
    if len(cards) != 78:
        raise CardDataError(f"The complete deck must contain 78 cards; found {len(cards)}.")
    return cards


def load_cards(path: Path) -> tuple[Card, ...]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CardDataError(f"Card data was not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CardDataError(f"Card data is not valid JSON: {exc}") from exc

    if not isinstance(raw, list):
        raise CardDataError("Card data must contain a JSON list.")

    cards: list[Card] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(raw):
        location = f"card entry {index + 1}"
        if not isinstance(item, dict):
            raise CardDataError(f"{location} must be an object.")

        required = {"id", "name", "arcana", "suit", "rank", "upright", "reversed"}
        missing = required - item.keys()
        if missing:
            raise CardDataError(f"{location} is missing: {', '.join(sorted(missing))}")

        card_id = _required_text(item["id"], f"{location}.id")
        if card_id in seen_ids:
            raise CardDataError(f"Duplicate card id: {card_id}")
        seen_ids.add(card_id)

        cards.append(
            Card(
                id=card_id,
                name=_required_text(item["name"], f"{location}.name"),
                arcana=_required_text(item["arcana"], f"{location}.arcana"),
                suit=_optional_text(item["suit"], f"{location}.suit"),
                rank=_optional_text(item["rank"], f"{location}.rank"),
                upright=_parse_meaning(item["upright"], f"{location}.upright"),
                reversed=_parse_meaning(item["reversed"], f"{location}.reversed"),
            )
        )

    if not cards:
        raise CardDataError("The deck contains no cards.")
    return tuple(cards)


def _parse_meaning(value: Any, location: str) -> OrientationMeaning:
    if not isinstance(value, dict):
        raise CardDataError(f"{location} must be an object.")
    if set(value) != {"keywords", "text"}:
        raise CardDataError(f"{location} must contain exactly 'keywords' and 'text'.")
    keywords = value["keywords"]
    if not isinstance(keywords, list) or not 2 <= len(keywords) <= 5:
        raise CardDataError(f"{location}.keywords must contain two to five entries.")
    parsed_keywords = tuple(
        _required_text(keyword, f"{location}.keywords") for keyword in keywords
    )
    return OrientationMeaning(
        keywords=parsed_keywords,
        text=_required_text(value["text"], f"{location}.text"),
    )


def _required_text(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CardDataError(f"{location} must be non-empty text.")
    return value.strip()


def _optional_text(value: Any, location: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, location)
