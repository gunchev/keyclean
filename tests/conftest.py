"""Shared pytest fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def no_pygame_display(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent any test from actually opening a display window."""
    # We mock at the module level where pygame is imported by each module.
    # Individual tests that need deeper pygame mocking do so themselves.
