# Thorn Reliquary audit repair pass

This checklist records the corrective pass prompted by the independent visual
audit completed on 20 September 2026. The canonical face is not considered
repaired until its full-resolution image, upright and reversed thumbnails, and
contact sheet have all been regenerated and inspected.

## Failed cards

- [x] `wands_03_three`: exactly three planted wands; remove the held fourth.
- [x] `wands_04_four`: Arabic `4` in the medallion; remove the traveler's
  wand-like walking stick; retain exactly four canopy wands.
- [x] `wands_06_six`: third-pass redraw uses an explicit 3 + 1 + 2 layout:
  three companion wands on the left, the rider's central laurel wand, and two
  companion wands on the right. The extra sixth companion and all wand-like
  banners, poles, branches, and props were removed.
- [x] `wands_09_nine`: one held wand plus eight fence wands.
- [x] `swords_07_seven`: five carried swords plus two left at the tents.
- [x] `swords_08_eight`: add an eighth planted sword without closing the exit.
- [x] `pentacles_03_three`: Arabic `3` in the medallion; retain three coins.
- [x] `pentacles_06_six`: five displayed coins plus one distributed coin.
- [x] `pentacles_09_nine`: four left, one upper-center, and four right coins.
- [x] `major_17_the_star`: one great star plus seven smaller stars.

## Ambiguous cards

- [x] `wands_05_five`: exactly five continuously traceable practice wands,
  with all ten ends visible.
- [x] `swords_10_ten`: exactly ten continuously traceable broken swords and
  ten distinct hilts.
- [x] `major_12_the_hanged_man`: suspension by one ankle and crossed free leg
  must read immediately at card size.

## Acceptance checks

- [x] Full-resolution master is 1024 x 1536 PNG.
- [x] Top medallion follows the deck's numeral convention.
- [x] Suit objects are countable at full size and on the contact sheet.
- [x] Non-suit props cannot be mistaken for extra pips.
- [x] Border, rivets, knotwork, palette, print texture, and wear match the deck.
- [x] Upright and reversed 200 x 300 thumbnails were rebuilt.
- [x] The affected suit contact sheet was rebuilt.
- [x] `python -m unittest tests.test_artwork -v` passes.
- [ ] Full test discovery currently reports five pre-existing relationship-text
  errors in `app/interpretation.py`; these are outside the artwork audit.
