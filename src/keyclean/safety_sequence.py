"""Safety sequence detector.

Tracks typed characters in a ring buffer and signals when the user
has typed the full exit phrase (case-insensitive).
"""

from __future__ import annotations

from collections import deque

from keyclean import config


class SafetySequence:
    """Ring buffer that detects when the exit phrase has been typed."""

    def __init__(self, phrase: str = config.EXIT_PHRASE) -> None:
        self._phrase = phrase.lower()
        self._length = len(self._phrase)
        self._buf: deque[str] = deque(maxlen=self._length)

    def feed(self, char: str) -> bool:
        """Feed one character.  Returns True if the exit phrase is complete."""
        self._buf.append(char.lower())
        if len(self._buf) < self._length:
            return False
        return "".join(self._buf) == self._phrase

    def reset(self) -> None:
        """Clear the buffer."""
        self._buf.clear()
