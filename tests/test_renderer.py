"""Tests for the Renderer class."""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from keyclean.renderer import Renderer


@pytest.fixture(scope="module", autouse=True)
def pygame_init() -> None:  # type: ignore[return]
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture()
def surface() -> pygame.Surface:
    return pygame.Surface((1920, 1080))


@pytest.fixture()
def renderer() -> Renderer:
    return Renderer(1920, 1080)


class TestRenderer:
    def test_instantiates(self, renderer: Renderer) -> None:
        assert renderer is not None

    def test_draw_returns_done_rect(
        self, renderer: Renderer, surface: pygame.Surface
    ) -> None:
        done_rect = renderer.draw(surface, set(), 0)
        assert isinstance(done_rect, pygame.Rect)
        assert done_rect.width > 0
        assert done_rect.height > 0

    def test_done_rect_inside_screen(
        self, renderer: Renderer, surface: pygame.Surface
    ) -> None:
        done_rect = renderer.draw(surface, set(), 0)
        screen_rect = surface.get_rect()
        assert screen_rect.contains(done_rect)

    def test_draw_with_pressed_keys_does_not_crash(
        self, renderer: Renderer, surface: pygame.Surface
    ) -> None:
        pressed = {pygame.K_a, pygame.K_SPACE, pygame.K_RETURN}
        renderer.draw(surface, pressed, 42)

    def test_draw_with_warning(
        self, renderer: Renderer, surface: pygame.Surface
    ) -> None:
        renderer.draw(surface, set(), 0, warning="Test warning message")

    def test_counter_text_rendered(
        self, renderer: Renderer, surface: pygame.Surface
    ) -> None:
        # We can't easily inspect rendered pixels in a unit test, but we can
        # verify draw() completes without exception for various counts.
        for count in (0, 1, 999, 1_000_000):
            renderer.draw(surface, set(), count)

    def test_small_screen_does_not_crash(self) -> None:
        small = Renderer(800, 600)
        surf = pygame.Surface((800, 600))
        small.draw(surf, set(), 0)

    def test_large_screen_does_not_crash(self) -> None:
        large = Renderer(3840, 2160)
        surf = pygame.Surface((3840, 2160))
        large.draw(surf, set(), 0)
