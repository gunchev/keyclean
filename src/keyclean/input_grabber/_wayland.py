"""Wayland grabber — explicit zwp_keyboard_shortcuts_inhibit_manager_v1.

Inhibit flow:
  1. pywayland opens a probe connection to verify the compositor exports
     zwp_keyboard_shortcuts_inhibit_manager_v1 and logs the result.
  2. pygame.Window.keyboard_grab = True tells SDL2 to call
     SDL_SetWindowKeyboardGrab, which in SDL2's Wayland backend requests
     zwp_keyboard_shortcuts_inhibit_manager_v1_inhibit_shortcuts on the
     window surface that actually has keyboard focus.

Why split?  Wayland protocol objects are connection-scoped — objects from
our pywayland probe connection cannot be passed to SDL2's wl_surface (a
different connection).  SDL2 must make the inhibit call itself using its
own connection; pywayland gives us the diagnostic / verification layer.

TTY-switching shortcuts (Ctrl+Alt+F*) are kernel-level and cannot be
blocked from userspace regardless of which method is used.
"""

from __future__ import annotations

import glob
import logging
import os

import pygame

from keyclean.input_grabber._base import AbstractGrabber

logger = logging.getLogger(__name__)

_MIN_SDL_VERSION = (2, 28, 0)
_INHIBIT_IFACE = "zwp_keyboard_shortcuts_inhibit_manager_v1"


def _probe_compositor_support() -> bool:
    """Return True if the compositor advertises the shortcuts-inhibit protocol.

    Opens a short-lived pywayland connection, collects the global registry,
    then disconnects.  Does not affect SDL2's connection.
    """
    # pylint: disable=import-outside-toplevel
    try:
        from pywayland.client import Display as WlDisplay  # type: ignore[import-untyped]
    except ImportError:
        logger.debug("pywayland not installed; skipping compositor protocol probe.")
        return False

    found = False
    try:
        display = WlDisplay()
        display.connect()
        registry = display.get_registry()

        @registry.dispatcher["global"]  # type: ignore[misc]
        def _on_global(
            _registry: object, _name: int, interface: str, _version: int
        ) -> None:
            nonlocal found
            if interface == _INHIBIT_IFACE:
                found = True

        display.roundtrip()
        display.disconnect()
    except Exception:  # pylint: disable=broad-except
        logger.debug("pywayland probe failed.", exc_info=True)
        return False

    return found


def _check_dev_input_access() -> str | None:
    """Return a UI notice (and log it) if /dev/input/* is not readable.

    Readability of /dev/input/ is not required for the current
    (SDL2-based) grab method, but it enables a stronger evdev-level
    grab (Option B).  Returns the notice string so the caller can
    surface it in the UI, or None when no notice is needed.
    """
    devices = glob.glob("/dev/input/event*")
    if not devices:
        return None  # No input devices found — unusual, skip.

    if not os.access(devices[0], os.R_OK):
        user = os.environ.get("USER", "$USER")
        notice = f"For stronger Wayland key suppression: sudo usermod -aG input {user}"
        logger.info(
            "Your user cannot read /dev/input/event* devices. "
            "For stronger Wayland input suppression (evdev-level) add yourself "
            "to the 'input' group and log out/in:\n"
            "    sudo usermod -aG input %s",
            user,
        )
        return notice
    return None


class WaylandGrabber(AbstractGrabber):
    """Wayland keyboard-shortcuts inhibit via SDL2 + pywayland verification."""

    description = "Wayland zwp_keyboard_shortcuts_inhibit_manager_v1 (via SDL2)"
    is_fallback = False

    def grab(self) -> None:
        # ------------------------------------------------------------------ #
        # 1. SDL version check
        # ------------------------------------------------------------------ #
        sdl_ver = pygame.get_sdl_version()
        if sdl_ver < _MIN_SDL_VERSION:
            logger.warning(
                "SDL2 version %s is older than %s; keyboard shortcuts inhibit "
                "may not work on Wayland.  Consider upgrading pygame-ce.",
                ".".join(str(v) for v in sdl_ver),
                ".".join(str(v) for v in _MIN_SDL_VERSION),
            )

        # ------------------------------------------------------------------ #
        # 2. Verify compositor supports the protocol (pywayland probe)
        # ------------------------------------------------------------------ #
        if _probe_compositor_support():
            logger.info("Compositor supports %s.", _INHIBIT_IFACE)
        else:
            logger.warning(
                "Compositor does not advertise %s; "
                "compositor shortcuts (Super, Alt+Tab, …) will NOT be suppressed.",
                _INHIBIT_IFACE,
            )

        # ------------------------------------------------------------------ #
        # 3. Request inhibit via SDL2's Wayland backend
        #    pygame.Window.keyboard_grab = True  →
        #      SDL_SetWindowKeyboardGrab(window, SDL_TRUE)  →
        #        zwp_keyboard_shortcuts_inhibit_manager_v1_inhibit_shortcuts(…)
        # ------------------------------------------------------------------ #
        try:
            win = pygame.Window.from_display_module()  # type: ignore[attr-defined]
            win.keyboard_grab = True  # type: ignore[attr-defined]
            logger.info("Keyboard shortcuts inhibit requested (keyboard_grab=True).")
        except AttributeError:
            # Older pygame-ce without pygame.Window.keyboard_grab — fall back
            # to the combined mouse+keyboard grab.
            pygame.event.set_grab(True)
            logger.info(
                "pygame.Window.keyboard_grab unavailable; "
                "using pygame.event.set_grab(True) instead."
            )

        # ------------------------------------------------------------------ #
        # 4. Inform the user about /dev/input access for Option B
        # ------------------------------------------------------------------ #
        self.ui_notice = _check_dev_input_access()

        self.active = True
        logger.info(
            "Wayland grab active. Ctrl+Alt+F* (TTY switch) cannot be blocked."
        )

    def release(self) -> None:
        if self.active:
            try:
                win = pygame.Window.from_display_module()  # type: ignore[attr-defined]
                win.keyboard_grab = False  # type: ignore[attr-defined]
            except AttributeError:
                pygame.event.set_grab(False)
            self.active = False
            logger.info("Wayland keyboard grab released.")
