"""Tests for SafetySequence."""

from __future__ import annotations

import pytest

from keyclean.safety_sequence import SafetySequence


PHRASE = "keys are clean"


class TestSafetySequence:
    def test_exact_phrase_triggers(self) -> None:
        seq = SafetySequence(PHRASE)
        for ch in PHRASE[:-1]:
            assert seq.feed(ch) is False
        assert seq.feed(PHRASE[-1]) is True

    def test_case_insensitive(self) -> None:
        seq = SafetySequence(PHRASE)
        for ch in PHRASE[:-1].upper():
            seq.feed(ch)
        assert seq.feed(PHRASE[-1].upper()) is True

    def test_partial_does_not_trigger(self) -> None:
        seq = SafetySequence(PHRASE)
        for ch in PHRASE[:5]:
            assert seq.feed(ch) is False

    def test_wrong_chars_no_trigger(self) -> None:
        seq = SafetySequence(PHRASE)
        for ch in "aaaaaaaaaaaaaaaaaaa":
            assert seq.feed(ch) is False

    def test_ring_buffer_slides(self) -> None:
        """Extra chars before the phrase should not prevent detection."""
        seq = SafetySequence(PHRASE)
        for ch in "zzz":
            seq.feed(ch)
        for ch in PHRASE[:-1]:
            seq.feed(ch)
        assert seq.feed(PHRASE[-1]) is True

    def test_reset_clears_buffer(self) -> None:
        seq = SafetySequence(PHRASE)
        for ch in PHRASE:
            seq.feed(ch)
        seq.reset()
        # After reset, feeding just the last char should not trigger.
        assert seq.feed(PHRASE[-1]) is False

    def test_empty_phrase_always_triggers(self) -> None:
        seq = SafetySequence("")
        # An empty phrase matches immediately with any (or no) input,
        # but feeding a char still returns True because buf matches "".
        assert seq.feed("x") is True

    def test_single_char_phrase(self) -> None:
        seq = SafetySequence("x")
        assert seq.feed("y") is False
        assert seq.feed("x") is True

    @pytest.mark.parametrize("phrase", ["keys are clean", "abc", "z"])
    def test_custom_phrases(self, phrase: str) -> None:
        seq = SafetySequence(phrase)
        for ch in phrase[:-1]:
            seq.feed(ch)
        assert seq.feed(phrase[-1]) is True
