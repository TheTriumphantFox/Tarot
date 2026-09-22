from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from collections.abc import Callable, Sequence

from .models import Card, ControlState, ReadingResult


NonceProvider = Callable[[int], bytes]
EntropyProvider = Callable[[int], bytes]
Clock = Callable[[], int]


class SignalSession:
    """Owns one local reading session and its interaction-derived seed state."""

    PROTOCOL = "signal-tarot-seed-v4"
    SAMPLE_PROTOCOL = "signal-tarot-sample-v2"
    SAMPLES_PER_SECOND = 5
    SAMPLE_INTERVAL_MS = 200
    _SIGIL_WORDS = (
        "ASH",
        "BELL",
        "CROW",
        "DUSK",
        "EMBER",
        "FERN",
        "GLASS",
        "HOLLOW",
        "IVY",
        "LANTERN",
        "MOTH",
        "NIGHT",
        "ORCHARD",
        "RIVER",
        "SABLE",
        "THORN",
    )

    def __init__(
        self,
        cards: Sequence[Card],
        *,
        nonce_provider: NonceProvider = secrets.token_bytes,
        sample_entropy_provider: EntropyProvider = secrets.token_bytes,
        clock: Clock = time.perf_counter_ns,
    ) -> None:
        if not cards:
            raise ValueError("A session requires at least one card.")
        card_ids = [card.id for card in cards]
        if len(card_ids) != len(set(card_ids)):
            raise ValueError("Every card must have a unique ID.")
        self._all_cards = tuple(cards)
        self._remaining = list(cards)
        self._clock = clock
        self._sample_entropy_provider = sample_entropy_provider
        self._nonce = nonce_provider(32)
        if len(self._nonce) != 32:
            raise ValueError("The nonce provider must return exactly 32 bytes.")
        self._started_ns = clock()
        self._interaction_digest = hashlib.sha256(
            b"signal-tarot-interaction-v1\x00" + self._nonce
        ).digest()
        self._interaction_count = 0
        self._draw_number = 0
        self._last_state = ControlState()

    @property
    def sigil(self) -> str:
        digest = hashlib.sha256(b"signal-tarot-sigil-v1\x00" + self._nonce).digest()
        first = self._SIGIL_WORDS[digest[0] % len(self._SIGIL_WORDS)]
        second = self._SIGIL_WORDS[digest[1] % len(self._SIGIL_WORDS)]
        number = int.from_bytes(digest[2:4], "big") % 100
        return f"{first}-{second}-{number:02d}"

    @property
    def can_draw(self) -> bool:
        return bool(self._remaining) and self._interaction_count > 0

    def can_draw_count(self, count: int) -> bool:
        return self._interaction_count > 0 and len(self._remaining) >= count

    @property
    def remaining_count(self) -> int:
        return len(self._remaining)

    @property
    def interaction_count(self) -> int:
        return self._interaction_count

    @property
    def draw_number(self) -> int:
        return self._draw_number

    def record_event(
        self,
        control_name: str,
        value: int | str,
        direction: str,
        state: ControlState,
    ) -> None:
        self._interaction_count += 1
        self._last_state = state
        event = {
            "control": control_name,
            "direction": direction,
            "elapsed_ns": self._clock() - self._started_ns,
            "event_number": self._interaction_count,
            "value": value,
        }
        encoded = _canonical_json(event)
        self._interaction_digest = hashlib.sha256(
            self._interaction_digest + encoded
        ).digest()

    def draw(self, state: ControlState) -> ReadingResult:
        return self.draw_many(state, 1)[0]

    def draw_many(self, state: ControlState, count: int) -> tuple[ReadingResult, ...]:
        """Perform an immediate draw for headless callers and deterministic tests."""
        elapsed_ns = self._clock() - self._started_ns
        sample = self._make_seed_sample(
            state,
            sample_index=0,
            elapsed_ns=elapsed_ns,
            fresh_entropy=self._fresh_sample_entropy(),
        )
        return self._complete_draw(
            state,
            count,
            duration_seconds=0,
            sample_seeds=(sample,),
            final_elapsed_ns=elapsed_ns,
        )

    def capture_seed_sample(self, state: ControlState, sample_index: int) -> bytes:
        if self._interaction_count == 0:
            raise RuntimeError("Tune at least one control before measuring the signal.")
        if sample_index < 0:
            raise ValueError("A sample index cannot be negative.")
        elapsed_ns = self._clock() - self._started_ns
        return self._make_seed_sample(
            state,
            sample_index,
            elapsed_ns,
            self._fresh_sample_entropy(),
        )

    def draw_many_from_samples(
        self,
        state: ControlState,
        count: int,
        duration_seconds: int,
        sample_seeds: Sequence[bytes],
    ) -> tuple[ReadingResult, ...]:
        if duration_seconds not in {1, 3, 5, 7, 10}:
            raise ValueError("Measurement duration must be 1, 3, 5, 7, or 10 seconds.")
        expected_samples = duration_seconds * self.SAMPLES_PER_SECOND + 1
        if len(sample_seeds) != expected_samples:
            raise ValueError(
                f"A {duration_seconds}-second window requires {expected_samples} samples."
            )
        if any(len(seed) != 32 for seed in sample_seeds):
            raise ValueError("Every sample seed must contain exactly 32 bytes.")
        return self._complete_draw(
            state,
            count,
            duration_seconds=duration_seconds,
            sample_seeds=sample_seeds,
            final_elapsed_ns=self._clock() - self._started_ns,
        )

    def _make_seed_sample(
        self,
        state: ControlState,
        sample_index: int,
        elapsed_ns: int,
        fresh_entropy: bytes,
    ) -> bytes:
        payload = {
            "control_state": state.as_seed_data(),
            "draw_number_start": self._draw_number + 1,
            "elapsed_ns": elapsed_ns,
            "interaction_count": self._interaction_count,
            "interaction_digest": self._interaction_digest.hex(),
            "fresh_os_entropy": fresh_entropy.hex(),
            "nonce": self._nonce.hex(),
            "protocol": self.SAMPLE_PROTOCOL,
            "sample_index": sample_index,
        }
        return hashlib.sha256(_canonical_json(payload)).digest()

    def _fresh_sample_entropy(self) -> bytes:
        entropy = self._sample_entropy_provider(32)
        if len(entropy) != 32:
            raise ValueError("The sample entropy provider must return exactly 32 bytes.")
        return entropy

    def _complete_draw(
        self,
        state: ControlState,
        count: int,
        *,
        duration_seconds: int,
        sample_seeds: Sequence[bytes],
        final_elapsed_ns: int,
    ) -> tuple[ReadingResult, ...]:
        if count < 1:
            raise ValueError("A draw must contain at least one card.")
        if not self._remaining:
            raise RuntimeError("The deck is empty. Reset the reading to continue.")
        if self._interaction_count == 0:
            raise RuntimeError("Tune at least one control before the first draw.")
        if len(self._remaining) < count:
            raise RuntimeError(
                f"Only {len(self._remaining)} card(s) remain; this draw requires {count}."
            )

        next_draw = self._draw_number + 1
        payload = {
            "card_count": count,
            "duration_seconds": duration_seconds,
            "final_control_state": state.as_seed_data(),
            "final_elapsed_ns": final_elapsed_ns,
            "final_interaction_count": self._interaction_count,
            "final_interaction_digest": self._interaction_digest.hex(),
            "draw_number_start": next_draw,
            "nonce": self._nonce.hex(),
            "protocol": self.PROTOCOL,
            "sample_count": len(sample_seeds),
            "sample_seeds": [seed.hex() for seed in sample_seeds],
        }
        master_seed = hashlib.sha256(_canonical_json(payload)).digest()
        card_seed = hmac.digest(master_seed, b"card-selection", "sha256")
        orientation_seed = hmac.digest(master_seed, b"orientation", "sha256")

        ordered = sorted(
            self._remaining,
            key=lambda card: (
                hmac.digest(card_seed, card.id.encode("utf-8"), "sha256"),
                card.id,
            ),
        )
        selected_cards = ordered[:count]
        results: list[ReadingResult] = []
        for position, selected in enumerate(selected_cards):
            orientation_message = (
                f"position:{position}\x00{selected.id}"
            ).encode("utf-8")
            is_reversed = hmac.digest(
                orientation_seed, orientation_message, "sha256"
            )[0] < 128
            meaning = selected.reversed if is_reversed else selected.upright
            results.append(
                ReadingResult(
                    card=selected,
                    reversed=is_reversed,
                    meaning=meaning,
                    draw_number=next_draw + position,
                    master_seed_hex=master_seed.hex(),
                    interaction_digest_hex=self._interaction_digest.hex(),
                )
            )

        for selected in selected_cards:
            self._remaining.remove(selected)
        self._draw_number += count
        self._last_state = state
        return tuple(results)


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
