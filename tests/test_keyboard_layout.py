"""Tests for keyboard_layout module."""

from __future__ import annotations

import os
import sys
from typing import List

# Ensure pygame does not try to open a display during import.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.display.init()

import pytest

from keyclean.keyboard_layout import KEYS, PYGAME_KEY_MAP, KeyDef


class TestKeyboardLayout:
    def test_total_key_count(self) -> None:
        """ISO 105-key board — allow a few ± for implementation variance."""
        assert 100 <= len(KEYS) <= 115, f"Expected ~105 keys, got {len(KEYS)}"

    def test_all_key_ids_unique(self) -> None:
        ids = [k.key_id for k in KEYS]
        assert len(ids) == len(set(ids)), "Duplicate key_id detected"

    def test_all_pygame_keys_unique(self) -> None:
        """No two keys should map to the same pygame keycode."""
        codes = [k.pygame_key for k in KEYS if k.pygame_key is not None]
        assert len(codes) == len(set(codes)), "Duplicate pygame_key detected"

    def test_pygame_key_map_consistency(self) -> None:
        """PYGAME_KEY_MAP must cover all keys that have a pygame_key."""
        for key in KEYS:
            if key.pygame_key is not None:
                assert key.pygame_key in PYGAME_KEY_MAP
                assert PYGAME_KEY_MAP[key.pygame_key] is key

    def test_no_zero_size_keys(self) -> None:
        for key in KEYS:
            assert key.width > 0, f"{key.key_id} has width=0"
            assert key.height > 0, f"{key.key_id} has height=0"

    def test_all_keys_have_labels(self) -> None:
        for key in KEYS:
            # Space bar is allowed to have an empty label
            if key.key_id != "space":
                assert key.label.strip(), f"{key.key_id} has an empty label"

    def test_lshift_wider_than_one_unit(self) -> None:
        lshift = next(k for k in KEYS if k.key_id == "lshift")
        assert lshift.width >= 2.0, "Left Shift should be at least 2u wide"

    def test_numpad_keys_present(self) -> None:
        np_ids = {k.key_id for k in KEYS if k.key_id.startswith("np_")}
        expected = {"np_0", "np_1", "np_2", "np_3", "np_4", "np_5", "np_6",
                    "np_7", "np_8", "np_9", "np_dot", "np_enter",
                    "np_plus", "np_minus", "np_star", "np_slash", "np_lock"}
        missing = expected - np_ids
        assert not missing, f"Missing numpad keys: {missing}"

    def test_function_keys_f1_f12(self) -> None:
        ids = {k.key_id for k in KEYS}
        for i in range(1, 13):
            assert f"f{i}" in ids, f"F{i} key missing"

    def test_arrow_keys_present(self) -> None:
        ids = {k.key_id for k in KEYS}
        for arrow in ("up", "down", "left", "right"):
            assert arrow in ids, f"Arrow key '{arrow}' missing"

    def test_key_rows_in_valid_range(self) -> None:
        for key in KEYS:
            assert 0 <= key.row <= 6, f"{key.key_id} has invalid row {key.row}"

    def test_key_cols_non_negative(self) -> None:
        for key in KEYS:
            assert key.col >= 0, f"{key.key_id} has negative col {key.col}"
