"""Tests for input_grabber factory and implementations."""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pygame
import pytest

from keyclean.input_grabber._base import AbstractGrabber
from keyclean.input_grabber._evdev import EvdevGrabber
from keyclean.input_grabber._fallback import FallbackGrabber
from keyclean.input_grabber._wayland import WaylandGrabber


class TestFallbackGrabber:
    def test_grab_sets_active(self) -> None:
        g = FallbackGrabber()
        assert not g.active
        g.grab()
        assert g.active

    def test_release_clears_active(self) -> None:
        g = FallbackGrabber()
        g.grab()
        g.release()
        assert not g.active

    def test_is_fallback(self) -> None:
        assert FallbackGrabber().is_fallback is True

    def test_context_manager(self) -> None:
        g = FallbackGrabber()
        with g:
            assert g.active
        assert not g.active


def _mock_pygame_window() -> MagicMock:
    """Return a mock window instance (return value of from_display_module())."""
    mock_win = MagicMock()
    mock_win.keyboard_grab = False
    return mock_win


def _mock_window_class(mock_win: MagicMock) -> MagicMock:
    """Return a mock Window class whose from_display_module() returns mock_win."""
    cls = MagicMock()
    cls.from_display_module.return_value = mock_win
    return cls


class TestWaylandGrabber:
    def test_grab_sets_active(self) -> None:
        mock_win = _mock_pygame_window()
        with (
            patch("pygame.get_sdl_version", return_value=(2, 28, 0)),
            patch("keyclean.input_grabber._wayland._probe_compositor_support", return_value=True),
            patch("keyclean.input_grabber._wayland._check_dev_input_access"),
            patch.object(pygame, "Window", _mock_window_class(mock_win), create=True),
        ):
            g = WaylandGrabber()
            g.grab()
            assert g.active

    def test_release_clears_active(self) -> None:
        mock_win = _mock_pygame_window()
        with (
            patch("pygame.get_sdl_version", return_value=(2, 28, 0)),
            patch("keyclean.input_grabber._wayland._probe_compositor_support", return_value=True),
            patch("keyclean.input_grabber._wayland._check_dev_input_access"),
            patch.object(pygame, "Window", _mock_window_class(mock_win), create=True),
        ):
            g = WaylandGrabber()
            g.grab()
            g.release()
            assert not g.active

    def test_is_not_fallback(self) -> None:
        assert WaylandGrabber().is_fallback is False

    def test_old_sdl_warns(self, caplog: pytest.LogCaptureFixture) -> None:
        import logging
        mock_win = _mock_pygame_window()
        with (
            patch("pygame.get_sdl_version", return_value=(2, 0, 5)),
            patch("keyclean.input_grabber._wayland._probe_compositor_support", return_value=True),
            patch("keyclean.input_grabber._wayland._check_dev_input_access"),
            patch.object(pygame, "Window", _mock_window_class(mock_win), create=True),
        ):
            g = WaylandGrabber()
            with caplog.at_level(logging.WARNING):
                g.grab()
        assert "older than" in caplog.text

    def test_no_compositor_support_warns(self, caplog: pytest.LogCaptureFixture) -> None:
        import logging
        mock_win = _mock_pygame_window()
        with (
            patch("pygame.get_sdl_version", return_value=(2, 28, 0)),
            patch("keyclean.input_grabber._wayland._probe_compositor_support", return_value=False),
            patch("keyclean.input_grabber._wayland._check_dev_input_access"),
            patch.object(pygame, "Window", _mock_window_class(mock_win), create=True),
        ):
            g = WaylandGrabber()
            with caplog.at_level(logging.WARNING):
                g.grab()
        assert "does not advertise" in caplog.text

    def test_keyboard_grab_called(self) -> None:
        mock_win = _mock_pygame_window()
        with (
            patch("pygame.get_sdl_version", return_value=(2, 28, 0)),
            patch("keyclean.input_grabber._wayland._probe_compositor_support", return_value=True),
            patch("keyclean.input_grabber._wayland._check_dev_input_access"),
            patch.object(pygame, "Window", _mock_window_class(mock_win), create=True),
        ):
            WaylandGrabber().grab()
        assert mock_win.keyboard_grab is True

    def test_dev_input_notice_when_no_access(self, caplog: pytest.LogCaptureFixture) -> None:
        import logging
        mock_win = _mock_pygame_window()
        with (
            patch("pygame.get_sdl_version", return_value=(2, 28, 0)),
            patch("keyclean.input_grabber._wayland._probe_compositor_support", return_value=True),
            patch("keyclean.input_grabber._wayland.glob.glob", return_value=["/dev/input/event0"]),
            patch("keyclean.input_grabber._wayland.os.access", return_value=False),
            patch.object(pygame, "Window", _mock_window_class(mock_win), create=True),
        ):
            g = WaylandGrabber()
            with caplog.at_level(logging.INFO):
                g.grab()
        assert "usermod" in caplog.text
        assert g.ui_notice is not None and "usermod" in g.ui_notice


class TestGetGrabberFactory:
    """Test the platform-dispatch logic in get_grabber()."""

    def _patch_platform(self, platform: str, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "platform", platform)

    def test_unknown_platform_returns_fallback(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch_platform("freebsd12", monkeypatch)
        from keyclean.input_grabber import get_grabber
        # Reload to pick up monkeypatched sys.platform
        with patch("keyclean.input_grabber.sys.platform", "freebsd12"):
            grabber = get_grabber()
        assert isinstance(grabber, FallbackGrabber)

    def test_linux_wayland_evdev_preferred(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """evdev is chosen over WaylandGrabber when /dev/input is accessible."""
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        with patch("keyclean.input_grabber.sys.platform", "linux"), \
             patch("keyclean.input_grabber._evdev_available", return_value=True):
            from keyclean.input_grabber import get_grabber
            grabber = get_grabber()
        assert isinstance(grabber, EvdevGrabber)

    def test_linux_wayland_no_evdev_returns_wayland_grabber(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Falls back to WaylandGrabber when evdev is unavailable."""
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        with patch("keyclean.input_grabber.sys.platform", "linux"), \
             patch("keyclean.input_grabber._evdev_available", return_value=False):
            from keyclean.input_grabber import get_grabber
            grabber = get_grabber()
        assert isinstance(grabber, WaylandGrabber)

    def test_linux_no_evdev_no_xlib_no_pynput_returns_fallback(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
        monkeypatch.setenv("DISPLAY", ":0")
        with patch("keyclean.input_grabber.sys.platform", "linux"), \
             patch("keyclean.input_grabber._evdev_available", return_value=False), \
             patch("importlib.import_module", side_effect=ModuleNotFoundError):
            from keyclean.input_grabber import get_grabber
            grabber = get_grabber()
        assert isinstance(grabber, FallbackGrabber)

    def test_darwin_no_pynput_returns_fallback(self) -> None:
        with patch("keyclean.input_grabber.sys.platform", "darwin"), \
             patch("importlib.import_module", side_effect=ModuleNotFoundError):
            from keyclean.input_grabber import get_grabber
            grabber = get_grabber()
        assert isinstance(grabber, FallbackGrabber)

    def test_win32_no_pynput_returns_fallback(self) -> None:
        with patch("keyclean.input_grabber.sys.platform", "win32"), \
             patch("importlib.import_module", side_effect=ModuleNotFoundError):
            from keyclean.input_grabber import get_grabber
            grabber = get_grabber()
        assert isinstance(grabber, FallbackGrabber)
