from __future__ import annotations

import unittest
from collections.abc import Iterator
from pathlib import Path

from app.deck import load_deck
from app.models import ControlState
from app.session import SignalSession


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CARDS = load_deck(PROJECT_ROOT / "data")


def fixed_nonce(size: int) -> bytes:
    return bytes.fromhex("3a" * size)


def fixed_sample_entropy(size: int) -> bytes:
    return bytes.fromhex("7b" * size)


def clock_from(values: list[int]):
    iterator: Iterator[int] = iter(values)
    return lambda: next(iterator)


class SignalSessionTests(unittest.TestCase):
    def test_duplicate_card_ids_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Every card must have a unique ID"):
            SignalSession((CARDS[0], CARDS[0]))

    def test_identical_inputs_produce_identical_reading(self) -> None:
        first = self._make_single_draw(440)
        second = self._make_single_draw(440)
        self.assertEqual(first.card.id, second.card.id)
        self.assertEqual(first.reversed, second.reversed)
        self.assertEqual(first.master_seed_hex, second.master_seed_hex)

    def test_changed_interaction_changes_master_seed(self) -> None:
        first = self._make_single_draw(440)
        second = self._make_single_draw(441)
        self.assertNotEqual(first.master_seed_hex, second.master_seed_hex)

    def test_same_final_state_different_path_changes_seed(self) -> None:
        state = ControlState(frequency=440)

        direct = SignalSession(
            CARDS,
            nonce_provider=fixed_nonce,
            sample_entropy_provider=fixed_sample_entropy,
            clock=clock_from([1_000, 1_100, 1_400]),
        )
        direct.record_event("frequency", 440, "up", state)
        direct_result = direct.draw(state)

        indirect = SignalSession(
            CARDS,
            nonce_provider=fixed_nonce,
            sample_entropy_provider=fixed_sample_entropy,
            clock=clock_from([1_000, 1_050, 1_100, 1_400]),
        )
        indirect.record_event("frequency", 430, "down", ControlState(frequency=430))
        indirect.record_event("frequency", 440, "up", state)
        indirect_result = indirect.draw(state)

        self.assertNotEqual(direct_result.master_seed_hex, indirect_result.master_seed_hex)

    def test_draw_again_works_without_retuning(self) -> None:
        clock = clock_from([1_000, 1_100, 1_200, 1_300])
        session = SignalSession(
            CARDS,
            nonce_provider=fixed_nonce,
            sample_entropy_provider=fixed_sample_entropy,
            clock=clock,
        )
        state = ControlState(frequency=440)
        session.record_event("frequency", 440, "up", state)
        first = session.draw(state)
        self.assertTrue(session.can_draw)
        second = session.draw(state)
        self.assertNotEqual(first.card.id, second.card.id)
        self.assertNotEqual(first.master_seed_hex, second.master_seed_hex)

    def test_three_card_draw_is_unique_and_uses_one_master_seed(self) -> None:
        session = SignalSession(
            CARDS,
            nonce_provider=fixed_nonce,
            sample_entropy_provider=fixed_sample_entropy,
            clock=clock_from([1_000, 1_100, 1_400]),
        )
        state = ControlState(frequency=440)
        session.record_event("frequency", 440, "up", state)
        results = session.draw_many(state, 3)
        self.assertEqual(3, len(results))
        self.assertEqual(3, len({result.card.id for result in results}))
        self.assertEqual(1, len({result.master_seed_hex for result in results}))
        self.assertEqual([1, 2, 3], [result.draw_number for result in results])
        self.assertEqual(75, session.remaining_count)

    def test_three_card_draw_requires_three_remaining_cards(self) -> None:
        ticks = [1_000]
        for index in range(76):
            ticks.extend([2_000 + index * 100, 2_050 + index * 100])
        session = SignalSession(
            CARDS,
            nonce_provider=fixed_nonce,
            sample_entropy_provider=fixed_sample_entropy,
            clock=clock_from(ticks),
        )
        state = ControlState(frequency=440)
        session.record_event("frequency", 440, "up", state)
        for _ in range(76):
            session.draw(state)
        self.assertFalse(session.can_draw_count(3))
        with self.assertRaisesRegex(RuntimeError, "Only 2 card"):
            session.draw_many(state, 3)

    def test_measurement_window_hashes_five_times_per_second(self) -> None:
        times = [1_000, 1_100]
        times.extend(1_200 + index * 200 for index in range(16))
        times.append(4_250)
        session = SignalSession(
            CARDS,
            nonce_provider=fixed_nonce,
            sample_entropy_provider=fixed_sample_entropy,
            clock=clock_from(times),
        )
        state = ControlState(frequency=440)
        session.record_event("frequency", 440, "up", state)
        samples = tuple(
            session.capture_seed_sample(state, index) for index in range(16)
        )
        self.assertEqual(16, len(set(samples)))
        result = session.draw_many_from_samples(state, 1, 3, samples)[0]
        self.assertEqual(64, len(result.master_seed_hex))
        self.assertEqual(77, session.remaining_count)

    def test_mid_window_control_change_changes_final_seed(self) -> None:
        unchanged = self._make_measured_draw(change_midway=False)
        changed = self._make_measured_draw(change_midway=True)
        self.assertNotEqual(unchanged.master_seed_hex, changed.master_seed_hex)

    def test_fresh_sample_entropy_changes_final_seed(self) -> None:
        first = self._make_measured_draw(change_midway=False, entropy_byte=0x31)
        second = self._make_measured_draw(change_midway=False, entropy_byte=0x32)
        self.assertNotEqual(first.master_seed_hex, second.master_seed_hex)

    def test_measurement_rejects_wrong_sample_count(self) -> None:
        session = SignalSession(
            CARDS,
            nonce_provider=fixed_nonce,
            sample_entropy_provider=fixed_sample_entropy,
            clock=clock_from([1_000, 1_100, 1_200]),
        )
        state = ControlState(frequency=440)
        session.record_event("frequency", 440, "up", state)
        sample = session.capture_seed_sample(state, 0)
        with self.assertRaisesRegex(ValueError, "requires 16 samples"):
            session.draw_many_from_samples(state, 1, 3, (sample,))

    def test_cards_do_not_repeat_within_session(self) -> None:
        ticks = [1_000]
        for index in range(78):
            ticks.extend([2_000 + index * 100, 2_050 + index * 100])
        session = SignalSession(
            CARDS,
            nonce_provider=fixed_nonce,
            sample_entropy_provider=fixed_sample_entropy,
            clock=clock_from(ticks),
        )
        results = []
        for index in range(78):
            state = ControlState(frequency=index)
            session.record_event("frequency", index, "up", state)
            results.append(session.draw(state).card.id)
        self.assertEqual(78, len(set(results)))
        self.assertEqual(0, session.remaining_count)
        self.assertFalse(session.can_draw)

    def _make_single_draw(self, frequency: int):
        session = SignalSession(
            CARDS,
            nonce_provider=fixed_nonce,
            sample_entropy_provider=fixed_sample_entropy,
            clock=clock_from([1_000, 1_100, 1_400]),
        )
        state = ControlState(frequency=frequency)
        session.record_event("frequency", frequency, "up", state)
        return session.draw(state)

    def _make_measured_draw(
        self,
        *,
        change_midway: bool,
        entropy_byte: int = 0x7B,
    ):
        times = [1_000, 1_100]
        for index in range(16):
            times.append(1_200 + index * 200)
            if change_midway and index == 7:
                times.append(2_700)
        times.append(4_250)
        session = SignalSession(
            CARDS,
            nonce_provider=fixed_nonce,
            sample_entropy_provider=lambda size: bytes([entropy_byte]) * size,
            clock=clock_from(times),
        )
        state = ControlState(frequency=440)
        session.record_event("frequency", 440, "up", state)
        samples = []
        for index in range(16):
            samples.append(session.capture_seed_sample(state, index))
            if change_midway and index == 7:
                state = ControlState(frequency=441)
                session.record_event("frequency", 441, "up", state)
        return session.draw_many_from_samples(state, 1, 3, tuple(samples))[0]


if __name__ == "__main__":
    unittest.main()
