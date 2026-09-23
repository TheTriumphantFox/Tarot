# Signal Tarot

Signal Tarot is a completely local Windows desktop prototype. It combines a
session nonce with the values, ordering, direction, and high-resolution timing
of control movements. The resulting seed selects a Major Arcana card and its
upright or reversed orientation.

The deck contains all 78 Major and Minor Arcana cards, each with original
Thorn Reliquary artwork inspired by worn early-medieval illuminated
manuscripts. It has no networking, accounts, analytics, or runtime generative
AI. Optional narration uses the built-in Windows speech engine and remains
entirely local.

## Run it

Requirements: the python.org Windows build of Python 3.11 or newer with Tkinter.

- Double-click `run.bat`, or
- Open a terminal in this folder and run `python main.py`.

Move at least one dial or lever before the first draw. Then choose a pattern
from the spread selector and use the dynamically labeled `DRAW` button. Available patterns are One Card;
Situation and Advice; Past, Present, and Emerging; Mind, Body, and Spirit;
Four-Card Guidance; Five-Card Cross; and Seven-Card Horseshoe. The four-card
reading follows Present, Challenge, Guidance, and Outcome; the five-card
reading lands in a cross; and the seven-card reading lands in a traditional
horseshoe arc. Multi-card readings
present each card's theme, orientation, and meaning under its named position.
Cards do not repeat during a session. `RESET DECK`
returns all cards to the deck and creates a new session sigil.

Single-card readings display one illustrated face. Multi-card readings display
their named positions together, automatically scaling the artwork for larger
patterns. Reversed cards are shown upside-down as well as labeled, while the resting screen shows the
non-directional deck back. After each measurement, the selected cards are
dealt face down from the top of the window and revealed one at a time before
the interpretation appears. Full-resolution masters live in
`assets/deck/faces`; the application loads smaller local copies from
`assets/deck/thumbnails` to keep reveals responsive.

The `MEASUREMENT WINDOW` dial offers 1, 3, 5, 7, and 10 seconds. A draw captures
one sample immediately and another every 0.2 seconds, or five times per second.
Every sample receives a fresh 32-byte value from Windows in addition to the live
controls, rolling interaction digest, and high-resolution timing. Frequency,
Resonance, Drift, Direction, and Filter remain live during measurement. The
ordered sample seeds, final control state, interaction digest, draw sequence,
and timing are fused into the master seed used to select the card or spread.

| Measurement window | Sample seeds |
| ---: | ---: |
| 1 second | 6 |
| 3 seconds | 16 |
| 5 seconds | 26 |
| 7 seconds | 36 |
| 10 seconds | 51 |

While samples are being collected, the result panel is covered and displays
only `Concentrate on Your Question`. It returns when seed fusion begins.

`VOICE OFF / ON` enables or disables narration. Voice is off when the app
starts. Enabling it reads the current result, and later readings are narrated
after their reveal. Turning it off immediately stops active narration.

## Test it

```powershell
python -m unittest discover -s tests -v
```

The tests pin the session nonce and high-resolution clock, which makes the seed
protocol reproducible. They verify that changed interactions change the seed,
identical inputs reproduce the reading, repeat draws work with unchanged
controls, three-card spreads contain unique cards, cards do not repeat within
a session, and every card has its full-resolution face plus upright and
reversed display thumbnails.

## Privacy

The program deliberately makes no network requests and stores no readings or
interaction history. The rolling interaction digest stays in memory until the
application closes or the reading is reset.

Signal Tarot is a reflective spiritual tool. It does not claim to verify spirit
communication and should not replace medical, legal, financial, or mental-health
advice.
