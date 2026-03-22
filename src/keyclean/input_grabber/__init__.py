"""Input grabber factory.

Call ``get_grabber()`` to obtain the best available grabber for the current
platform and display server.
"""

from __future__ import annotations

import logging
import os
import sys

from keyclean.input_grabber._base import AbstractGrabber

logger = logging.getLogger(__name__)


# Grabber sub-modules are imported lazily so that missing optional dependencies
# (python-xlib, pynput) only raise errors when that grabber is actually selected,
# not at package import time.
# pylint: disable=import-outside-toplevel
def get_grabber() -> AbstractGrabber:
    """Return the most capable grabber for the current environment."""
    platform = sys.platform

    if platform.startswith("linux"):
        return _get_linux_grabber()
    if platform == "darwin":
        return _get_pynput_grabber()
    if platform == "win32":
        return _get_pynput_grabber()

    logger.warning("Unknown platform %r — using fallback grabber.", platform)
    return _get_fallback()


# ---------------------------------------------------------------------------
# Platform-specific helpers
# ---------------------------------------------------------------------------

def _get_linux_grabber() -> AbstractGrabber:
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()

    if session == "wayland":
        from keyclean.input_grabber._wayland import WaylandGrabber
        return WaylandGrabber()

    # X11 (or unknown — try X11 first, fall back to pynput, then fallback).
    if session in ("x11", "mir", "") and os.environ.get("DISPLAY"):
        try:
            from keyclean.input_grabber._x11 import X11Grabber
            # Probe that python-xlib is importable before committing.
            import importlib
            importlib.import_module("Xlib")
            return X11Grabber()
        except (ImportError, ModuleNotFoundError):
            logger.info("python-xlib not available; trying pynput.")

    # pynput fallback on Linux (X11 sessions without python-xlib, or Mir).
    try:
        from keyclean.input_grabber._pynput import PynputGrabber
        import importlib
        importlib.import_module("pynput")
        return PynputGrabber()
    except (ImportError, ModuleNotFoundError):
        logger.info("pynput not available; using fallback grabber.")

    return _get_fallback()


def _get_pynput_grabber() -> AbstractGrabber:
    try:
        from keyclean.input_grabber._pynput import PynputGrabber
        import importlib
        importlib.import_module("pynput")
        return PynputGrabber()
    except (ImportError, ModuleNotFoundError):
        logger.warning("pynput not available; using fallback grabber.")
        return _get_fallback()


def _get_fallback() -> AbstractGrabber:
    from keyclean.input_grabber._fallback import FallbackGrabber
    return FallbackGrabber()
