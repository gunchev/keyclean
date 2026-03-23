"""Main application — event loop, state management, and exit handling."""

from __future__ import annotations

import logging
import sys
from typing import Optional, Set

import pygame

from keyclean import config
from keyclean.input_grabber import AbstractGrabber, get_grabber
from keyclean.renderer import Renderer
from keyclean.safety_sequence import SafetySequence

logger = logging.getLogger(__name__)


class App:  # pylint: disable=too-few-public-methods
    """KeyClean application.

    Lifecycle::

        app = App()
        app.run()
    """

    def __init__(self) -> None:
        self._pressed_keys: Set[int] = set()
        self._strike_count: int = 0
        self._safety: SafetySequence = SafetySequence()
        self._running: bool = False
        self._renderer: Optional[Renderer] = None
        self._grabber: Optional[AbstractGrabber] = None

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Initialize pygame, acquire grab, run the loop, then clean up."""
        pygame.init()
        pygame.font.init()

        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("KeyClean")
        pygame.mouse.set_visible(True)  # keep visible for Done button

        sw, sh = screen.get_size()
        self._renderer = Renderer(sw, sh)

        self._grabber = get_grabber()
        warning: Optional[str] = None
        if self._grabber.is_fallback:
            warning = (
                "Warning: OS-level keyboard suppression is unavailable. "
                "Some system shortcuts may still work."
            )

        clock = pygame.time.Clock()

        with self._grabber:
            notice = self._grabber.ui_notice
            self._running = True
            while self._running:
                mouse_pos = pygame.mouse.get_pos()
                self._process_events()
                done_rect = self._renderer.draw(
                    screen,
                    self._pressed_keys,
                    self._strike_count,
                    warning=warning,
                    notice=notice,
                    mouse_pos=mouse_pos,
                )
                _ = done_rect   # used for hit-testing in _process_events via stored ref
                pygame.display.flip()
                clock.tick(config.TARGET_FPS)

        pygame.quit()

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _process_events(self) -> None:
        """Drain the full SDL event queue this frame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            elif event.type == pygame.KEYDOWN:
                self._pressed_keys.add(event.key)
                self._strike_count += 1
                char = self._key_to_char(event)
                if char and self._safety.feed(char):
                    logger.info("Exit phrase typed — exiting.")
                    self._running = False

            elif event.type == pygame.KEYUP:
                self._pressed_keys.discard(event.key)

            elif event.type == pygame.WINDOWFOCUSGAINED:
                if self._grabber is not None:
                    self._grabber.regrab()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self._renderer is not None:
                    # Re-draw is already scheduled; check Done button hit.
                    mouse_pos = pygame.mouse.get_pos()
                    # Renderer exposes done_rect through draw(); we access last computed rect.
                    done_rect = self._renderer.draw(
                        pygame.display.get_surface(),
                        self._pressed_keys,
                        self._strike_count,
                        mouse_pos=mouse_pos,
                    )
                    if done_rect.collidepoint(mouse_pos):
                        logger.info("Done button clicked — exiting.")
                        self._running = False

    @staticmethod
    def _key_to_char(event: pygame.event.Event) -> str:
        """Extract a printable character from a KEYDOWN event, or empty string."""
        char: str = event.unicode or ""
        # Filter control characters (ord < 32) and DEL.
        if char and (ord(char) < 32 or ord(char) == 127):
            return ""
        return char


def main() -> None:
    """Entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        App().run()
    except KeyboardInterrupt:
        pass
    sys.exit(0)
