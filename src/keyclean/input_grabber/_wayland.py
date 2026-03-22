"""Wayland grabber — best-effort via SDL2 keyboard shortcuts inhibit protocol.

SDL2 ≥ 2.28 supports zwp_keyboard_shortcuts_inhibit_manager_v1 when the
window is fullscreen and focused.  This inhibits compositor-level shortcuts
(Super, Alt+Tab, etc.) on supporting compositors (GNOME/Mutter, KDE/KWin, Sway).

TTY-switching shortcuts (Ctrl+Alt+F*) are kernel-level and cannot be blocked.
"""

from __future__ import annotations

import logging

import pygame

from keyclean.input_grabber._base import AbstractGrabber

logger = logging.getLogger(__name__)

_MIN_SDL_VERSION = (2, 28, 0)


class WaylandGrabber(AbstractGrabber):
    """Best-effort Wayland keyboard suppression through SDL2."""

    description = "Wayland SDL2 shortcuts_inhibit (best-effort)"
    is_fallback = True  # Still considered fallback — not full suppression.

    def grab(self) -> None:
        self.active = True
        sdl_ver = pygame.get_sdl_version()
        if sdl_ver < _MIN_SDL_VERSION:
            logger.warning(
                "SDL2 version %s is older than %s; keyboard shortcuts inhibit "
                "may not work on Wayland.  Consider upgrading pygame-ce.",
                ".".join(str(v) for v in sdl_ver),
                ".".join(str(v) for v in _MIN_SDL_VERSION),
            )
        logger.info(
            "Wayland mode: relying on SDL2 shortcuts_inhibit protocol. "
            "Ctrl+Alt+F* (TTY switch) cannot be blocked."
        )

    def release(self) -> None:
        self.active = False
