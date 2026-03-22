"""Tests for input_grabber factory and implementations."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from keyclean.input_grabber._base import AbstractGrabber
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


class TestWaylandGrabber:
    def test_grab_sets_active(self) -> None:
        with patch("pygame.get_sdl_version", return_value=(2, 28, 0)):
            g = WaylandGrabber()
            g.grab()
            assert g.active

    def test_release_clears_active(self) -> None:
        with patch("pygame.get_sdl_version", return_value=(2, 28, 0)):
            g = WaylandGrabber()
            g.grab()
            g.release()
            assert not g.active

    def test_old_sdl_warns(self, caplog: pytest.LogCaptureFixture) -> None:
        import logging
        with patch("pygame.get_sdl_version", return_value=(2, 0, 5)):
            g = WaylandGrabber()
            with caplog.at_level(logging.WARNING):
                g.grab()
        assert "older than" in caplog.text


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

    def test_linux_wayland_returns_wayland_grabber(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        with patch("keyclean.input_grabber.sys.platform", "linux"):
            from keyclean.input_grabber import get_grabber
            grabber = get_grabber()
        assert isinstance(grabber, WaylandGrabber)

    def test_linux_no_xlib_no_pynput_returns_fallback(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
        monkeypatch.setenv("DISPLAY", ":0")
        with patch("keyclean.input_grabber.sys.platform", "linux"), \
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
