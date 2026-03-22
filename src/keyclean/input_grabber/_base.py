"""Abstract base for input grabbers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class AbstractGrabber(ABC):
    """Grab (suppress) keyboard input at the OS level."""

    #: Human-readable description shown in logs / warning banner.
    description: str = "unknown"

    #: Set to True when grab is active.
    active: bool = False

    #: Set to True when the grabber operates in best-effort / fallback mode.
    is_fallback: bool = False

    #: Optional one-line notice to display in the UI after grab() is called.
    ui_notice: Optional[str] = None

    @abstractmethod
    def grab(self) -> None:
        """Activate input suppression."""

    @abstractmethod
    def release(self) -> None:
        """Deactivate input suppression."""

    def __enter__(self) -> "AbstractGrabber":
        self.grab()
        return self

    def __exit__(self, *_: object) -> None:
        self.release()
