from __future__ import annotations

import struct
import unittest
from pathlib import Path

from app.deck import load_deck


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FACES = PROJECT_ROOT / "assets" / "deck" / "faces"
THUMBNAILS = PROJECT_ROOT / "assets" / "deck" / "thumbnails"
DECK_ASSETS = PROJECT_ROOT / "assets" / "deck"


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        header = image.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"Not a PNG file: {path}")
    return struct.unpack(">II", header[16:24])


class ArtworkAssetTests(unittest.TestCase):
    def test_every_card_has_full_resolution_artwork(self) -> None:
        cards = load_deck(PROJECT_ROOT / "data")
        for card in cards:
            path = FACES / f"{card.id}.png"
            self.assertTrue(path.is_file(), card.id)
            width, height = png_dimensions(path)
            self.assertEqual((1024, 1536), (width, height), card.id)

    def test_every_card_has_upright_and_reversed_thumbnail(self) -> None:
        cards = load_deck(PROJECT_ROOT / "data")
        for card in cards:
            for suffix in ("", "-reversed"):
                path = THUMBNAILS / f"{card.id}{suffix}.png"
                self.assertTrue(path.is_file(), path.name)
                self.assertEqual((200, 300), png_dimensions(path), path.name)

    def test_card_back_thumbnail_exists(self) -> None:
        path = THUMBNAILS / "card-back.png"
        self.assertTrue(path.is_file())
        self.assertEqual((200, 300), png_dimensions(path))

    def test_contact_sheets_exist_at_review_dimensions(self) -> None:
        expected = {
            "contact-cups.png": (1120, 1600),
            "contact-majors.png": (1120, 2400),
            "contact-pentacles.png": (1120, 1600),
            "contact-swords.png": (1120, 1600),
            "contact-wands.png": (1120, 1600),
        }
        for name, dimensions in expected.items():
            path = DECK_ASSETS / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(dimensions, png_dimensions(path), name)


if __name__ == "__main__":
    unittest.main()
