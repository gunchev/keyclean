"""Fallback grabber — pygame fullscreen only, no OS-level suppression."""

from __future__ import annotations

import logging

from keyclean.input_grabber._base import AbstractGrabber

logger = logging.getLogger(__name__)


class FallbackGrabber(AbstractGrabber):
    """No-op grabber used when no native method is available.

    The app still runs fullscreen which prevents most accidental input, but
    system-level shortcuts (Alt+Tab, Super, etc.) may still escape.
    A warning banner is displayed to the user.
    """

    description = "pygame fullscreen (no OS-level suppression)"
    is_fallback = True

    def grab(self) -> None:
        self.active = True
        logger.warning(
            "Running in fallback mode: keyboard is NOT fully suppressed at the OS level. "
            "System shortcuts (Alt+Tab, Super, …) may still work."
        )

    def release(self) -> None:
        self.active = False
