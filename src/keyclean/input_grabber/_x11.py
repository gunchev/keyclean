"""X11 grabber — uses XGrabKeyboard via python-xlib.

Redirects all keyboard events to the pygame window, preventing them from
reaching any other application while the grab is active.
"""

from __future__ import annotations

import logging
import os

import pygame

from keyclean.input_grabber._base import AbstractGrabber

logger = logging.getLogger(__name__)


class X11Grabber(AbstractGrabber):
    """Full keyboard grab using XGrabKeyboard (X11 only)."""

    description = "XGrabKeyboard (X11)"
    is_fallback = False

    def __init__(self) -> None:
        self._display: object = None
        self._window: object = None

    def grab(self) -> None:
        # pylint: disable=import-outside-toplevel
        try:
            from Xlib import display as xdisplay  # type: ignore[import-untyped]
            from Xlib import X  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError(
                "python-xlib is required for X11 input suppression. "
                "Install it with: pip install python-xlib"
            ) from exc

        # Get the X11 window ID from the pygame/SDL window info.
        wm_info = pygame.display.get_wm_info()
        win_id: int = wm_info.get("window", 0)
        if not win_id:
            raise RuntimeError("Could not retrieve X11 window ID from pygame.")

        display_name = os.environ.get("DISPLAY", ":0")
        self._display = xdisplay.Display(display_name)
        self._window = self._display.create_resource_object("window", win_id)

        result = self._window.grab_keyboard(
            owner_events=True,
            pointer_mode=X.GrabModeAsync,
            keyboard_mode=X.GrabModeAsync,
            time=X.CurrentTime,
        )
        self._display.flush()

        if result != X.GrabSuccess:
            raise RuntimeError(f"XGrabKeyboard failed with status {result}.")

        self.active = True
        logger.info("X11 keyboard grab active (window id=0x%x).", win_id)

    def release(self) -> None:
        if self._display is not None and self.active:
            try:
                from Xlib import X  # type: ignore[import-untyped]  # pylint: disable=import-outside-toplevel
                self._display.ungrab_keyboard(X.CurrentTime)
                self._display.flush()
                logger.info("X11 keyboard grab released.")
            except Exception:  # pylint: disable=broad-except
                logger.exception("Error releasing X11 keyboard grab.")
            finally:
                self.active = False
                self._display = None
                self._window = None
