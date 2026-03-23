"""pynput-based grabber — used on macOS and Windows.

Uses pynput's Listener with suppress=True to intercept all keyboard events
before they reach other applications.  Events are still delivered to pygame
via its SDL event queue because pygame reads from the OS input layer above
the pynput hook (SDL processes them first on these platforms).

macOS: Uses CGEventTap (requires Accessibility permission).
Windows: Uses SetWindowsHookEx(WH_KEYBOARD_LL).
"""

from __future__ import annotations

import logging
from typing import Optional

from keyclean.input_grabber._base import AbstractGrabber

logger = logging.getLogger(__name__)


class PynputGrabber(AbstractGrabber):
    """Global keyboard suppression via pynput."""

    description = "pynput global hook (suppress=True)"
    is_fallback = False

    def __init__(self) -> None:
        self._listener: Optional[object] = None

    def grab(self) -> None:
        # pylint: disable=import-outside-toplevel
        try:
            from pynput import keyboard  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError(
                "pynput is required for global input suppression on macOS/Windows. "
                "Install it with: pip install pynput"
            ) from exc

        # suppress=True prevents events from reaching other apps.
        # We use a no-op on_press/on_release because pygame already handles
        # its own event queue independently; we only want the suppression side-effect.
        self._listener = keyboard.Listener(
            on_press=lambda _key: None,
            on_release=lambda _key: None,
            suppress=True,
        )
        try:
            self._listener.start()  # type: ignore[union-attr]
        except Exception as exc:  # pylint: disable=broad-except
            # On macOS, CGEventTap creation fails if Accessibility permission
            # has not been granted in System Preferences → Privacy & Security →
            # Accessibility.  Degrade gracefully rather than crashing.
            logger.warning(
                "pynput listener failed to start (%s). "
                "On macOS, grant Accessibility permission to the terminal "
                "or app that launched keyclean, then restart. "
                "Falling back: keyboard suppression is disabled.",
                exc,
            )
            self._listener = None
            self.is_fallback = True
            return
        self.active = True
        logger.info("pynput keyboard listener started (suppress=True).")

    def release(self) -> None:
        if self._listener is not None and self.active:
            try:
                self._listener.stop()  # type: ignore[union-attr]
                self._listener = None
                logger.info("pynput keyboard listener stopped.")
            except Exception:  # pylint: disable=broad-except
                logger.exception("Error stopping pynput listener.")
            finally:
                self.active = False
