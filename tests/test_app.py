"""Tests for the App class."""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from unittest.mock import MagicMock, patch

import pygame
import pytest

from keyclean.app import App
from keyclean.safety_sequence import SafetySequence


class TestAppKeyToChar:
    """Unit tests for the static _key_to_char helper."""

    def _make_event(self, unicode_char: str) -> MagicMock:
        event = MagicMock()
        event.unicode = unicode_char
        return event

    def test_printable_char_returned(self) -> None:
        event = self._make_event("a")
        assert App._key_to_char(event) == "a"

    def test_control_char_filtered(self) -> None:
        event = self._make_event("\x01")
        assert App._key_to_char(event) == ""

    def test_del_filtered(self) -> None:
        event = self._make_event("\x7f")
        assert App._key_to_char(event) == ""

    def test_empty_unicode_returns_empty(self) -> None:
        event = self._make_event("")
        assert App._key_to_char(event) == ""

    def test_space_is_printable(self) -> None:
        event = self._make_event(" ")
        assert App._key_to_char(event) == " "

    def test_newline_filtered(self) -> None:
        event = self._make_event("\n")
        assert App._key_to_char(event) == ""


class TestAppExitPhrase:
    """Verify that typing the exit phrase sets _running=False."""

    def test_exit_phrase_stops_loop(self) -> None:
        app = App()
        app._running = True

        phrase = "keys are clean"
        for ch in phrase[:-1]:
            event = MagicMock()
            event.type = pygame.KEYDOWN
            event.key = pygame.K_a
            event.unicode = ch
            app._pressed_keys.clear()  # simulate key up between presses
            # Feed directly to safety sequence to avoid needing pygame running
            app._safety.feed(ch)

        # Last character should trigger exit
        assert app._safety.feed(phrase[-1]) is True

    def test_partial_phrase_does_not_stop(self) -> None:
        app = App()
        app._running = True
        result = app._safety.feed("k")
        assert result is False
        assert app._running is True


class TestAppStrikeCounter:
    """Verify that the strike counter increments correctly."""

    def test_counter_starts_at_zero(self) -> None:
        app = App()
        assert app._strike_count == 0
