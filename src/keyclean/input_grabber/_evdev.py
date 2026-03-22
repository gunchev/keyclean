"""Linux evdev grabber — kernel-level EVIOCGRAB via python-evdev.

Grabs all keyboard input devices directly at the kernel level, preventing
events from reaching the display server (X11 or Wayland).  This sidesteps
compositor-specific protocols entirely, which is why the Super key and
other system shortcuts are fully suppressed without any Wayland/X11 magic.

Events are read in per-device background threads and re-posted as synthetic
pygame KEYDOWN/KEYUP events so the rest of the application works unchanged.

Requires: evdev>=1.7.0, user must be in the 'input' group.
"""
from __future__ import annotations

import logging
import select
import threading
from typing import Dict, List, Tuple

import pygame

from keyclean.input_grabber._base import AbstractGrabber

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# evdev keycode  →  (pygame key constant, base unicode, shifted unicode)
# ---------------------------------------------------------------------------

def _build_map() -> Dict[int, Tuple[int, str, str]]:  # pylint: disable=too-many-branches
    """Build the mapping table; returns {} if evdev is not importable."""
    # pylint: disable=import-outside-toplevel
    try:
        from evdev import ecodes as e  # type: ignore[import-untyped]
    except ImportError:
        return {}

    m: Dict[int, Tuple[int, str, str]] = {}

    # Letters (a–z)
    for ch in "abcdefghijklmnopqrstuvwxyz":
        ev_name = f"KEY_{ch.upper()}"
        pg_name = f"K_{ch}"
        if hasattr(e, ev_name) and hasattr(pygame, pg_name):
            m[getattr(e, ev_name)] = (getattr(pygame, pg_name), ch, ch.upper())

    # Digit row
    for ev_name, pg_name, base, shifted in [
        ("KEY_1", "K_1", "1", "!"), ("KEY_2", "K_2", "2", "@"),
        ("KEY_3", "K_3", "3", "#"), ("KEY_4", "K_4", "4", "$"),
        ("KEY_5", "K_5", "5", "%"), ("KEY_6", "K_6", "6", "^"),
        ("KEY_7", "K_7", "7", "&"), ("KEY_8", "K_8", "8", "*"),
        ("KEY_9", "K_9", "9", "("), ("KEY_0", "K_0", "0", ")"),
    ]:
        if hasattr(e, ev_name) and hasattr(pygame, pg_name):
            m[getattr(e, ev_name)] = (getattr(pygame, pg_name), base, shifted)

    # Symbol keys
    for ev_name, pg_name, base, shifted in [
        ("KEY_MINUS",      "K_MINUS",        "-", "_"),
        ("KEY_EQUAL",      "K_EQUALS",       "=", "+"),
        ("KEY_LEFTBRACE",  "K_LEFTBRACKET",  "[", "{"),
        ("KEY_RIGHTBRACE", "K_RIGHTBRACKET", "]", "}"),
        ("KEY_BACKSLASH",  "K_BACKSLASH",    "\\", "|"),
        ("KEY_SEMICOLON",  "K_SEMICOLON",    ";", ":"),
        ("KEY_APOSTROPHE", "K_QUOTE",        "'", '"'),
        ("KEY_GRAVE",      "K_BACKQUOTE",    "`", "~"),
        ("KEY_COMMA",      "K_COMMA",        ",", "<"),
        ("KEY_DOT",        "K_PERIOD",       ".", ">"),
        ("KEY_SLASH",      "K_SLASH",        "/", "?"),
    ]:
        if hasattr(e, ev_name) and hasattr(pygame, pg_name):
            m[getattr(e, ev_name)] = (getattr(pygame, pg_name), base, shifted)

    # Special / navigation keys (no printable unicode)
    for ev_name, pg_name in [
        ("KEY_SPACE",     "K_SPACE"),
        ("KEY_ENTER",     "K_RETURN"),
        ("KEY_BACKSPACE", "K_BACKSPACE"),
        ("KEY_TAB",       "K_TAB"),
        ("KEY_ESC",       "K_ESCAPE"),
        ("KEY_CAPSLOCK",  "K_CAPSLOCK"),
        ("KEY_DELETE",    "K_DELETE"),
        ("KEY_INSERT",    "K_INSERT"),
        ("KEY_HOME",      "K_HOME"),
        ("KEY_END",       "K_END"),
        ("KEY_PAGEUP",    "K_PAGEUP"),
        ("KEY_PAGEDOWN",  "K_PAGEDOWN"),
        ("KEY_UP",        "K_UP"),
        ("KEY_DOWN",      "K_DOWN"),
        ("KEY_LEFT",      "K_LEFT"),
        ("KEY_RIGHT",     "K_RIGHT"),
        ("KEY_LEFTSHIFT",  "K_LSHIFT"),
        ("KEY_RIGHTSHIFT", "K_RSHIFT"),
        ("KEY_LEFTCTRL",   "K_LCTRL"),
        ("KEY_RIGHTCTRL",  "K_RCTRL"),
        ("KEY_LEFTALT",    "K_LALT"),
        ("KEY_RIGHTALT",   "K_RALT"),
        ("KEY_SCROLLLOCK", "K_SCROLLOCK"),
        ("KEY_SYSRQ",      "K_PRINT"),
        ("KEY_PAUSE",      "K_PAUSE"),
    ]:
        if hasattr(e, ev_name) and hasattr(pygame, pg_name):
            base = " " if pg_name == "K_SPACE" else ""
            m[getattr(e, ev_name)] = (getattr(pygame, pg_name), base, base)

    # Meta / GUI keys (Super / Windows key)
    for ev_name, pg_names in [
        ("KEY_LEFTMETA",  ["K_LGUI", "K_LMETA", "K_LSUPER"]),
        ("KEY_RIGHTMETA", ["K_RGUI", "K_RMETA", "K_RSUPER"]),
    ]:
        if hasattr(e, ev_name):
            for pg_name in pg_names:
                if hasattr(pygame, pg_name):
                    m[getattr(e, ev_name)] = (getattr(pygame, pg_name), "", "")
                    break

    # Function keys F1–F12
    for i in range(1, 13):
        ev_name, pg_name = f"KEY_F{i}", f"K_F{i}"
        if hasattr(e, ev_name) and hasattr(pygame, pg_name):
            m[getattr(e, ev_name)] = (getattr(pygame, pg_name), "", "")

    # Numpad
    for ev_name, pg_name, base in [
        ("KEY_NUMLOCK",    "K_NUMLOCK",    ""),
        ("KEY_KP0",        "K_KP0",        "0"),
        ("KEY_KP1",        "K_KP1",        "1"),
        ("KEY_KP2",        "K_KP2",        "2"),
        ("KEY_KP3",        "K_KP3",        "3"),
        ("KEY_KP4",        "K_KP4",        "4"),
        ("KEY_KP5",        "K_KP5",        "5"),
        ("KEY_KP6",        "K_KP6",        "6"),
        ("KEY_KP7",        "K_KP7",        "7"),
        ("KEY_KP8",        "K_KP8",        "8"),
        ("KEY_KP9",        "K_KP9",        "9"),
        ("KEY_KPENTER",    "K_KP_ENTER",   ""),
        ("KEY_KPPLUS",     "K_KP_PLUS",    "+"),
        ("KEY_KPMINUS",    "K_KP_MINUS",   "-"),
        ("KEY_KPASTERISK", "K_KP_MULTIPLY","*"),
        ("KEY_KPSLASH",    "K_KP_DIVIDE",  "/"),
        ("KEY_KPDOT",      "K_KP_PERIOD",  "."),
    ]:
        if hasattr(e, ev_name) and hasattr(pygame, pg_name):
            m[getattr(e, ev_name)] = (getattr(pygame, pg_name), base, base)

    return m


# ---------------------------------------------------------------------------
# Device discovery
# ---------------------------------------------------------------------------

def _is_keyboard(device: object) -> bool:
    """Return True if the evdev device looks like a full keyboard."""
    # pylint: disable=import-outside-toplevel
    from evdev import ecodes  # type: ignore[import-untyped]
    caps = device.capabilities()  # type: ignore[attr-defined]
    if ecodes.EV_KEY not in caps:
        return False
    keys = set(caps[ecodes.EV_KEY])
    required = {ecodes.KEY_A, ecodes.KEY_Z, ecodes.KEY_SPACE, ecodes.KEY_ENTER}
    return required.issubset(keys)


# ---------------------------------------------------------------------------
# Grabber
# ---------------------------------------------------------------------------

class EvdevGrabber(AbstractGrabber):
    """Kernel-level keyboard grab via EVIOCGRAB (evdev).

    Works on both X11 and Wayland because it operates entirely below the
    display server — no compositor protocol needed.
    """

    description = "Linux evdev EVIOCGRAB (kernel-level, display-server agnostic)"
    is_fallback = False

    def __init__(self) -> None:
        self._devices: List[object] = []
        self._threads: List[threading.Thread] = []
        self._stop = threading.Event()
        self._shift_held = False
        self._caps_lock = False
        self._mod_lock = threading.Lock()
        self._key_map: Dict[int, Tuple[int, str, str]] = {}
        self._shift_codes: frozenset[int] = frozenset()
        self._caps_code: int = -1

    def grab(self) -> None:
        # pylint: disable=import-outside-toplevel
        from evdev import InputDevice, ecodes, list_devices  # type: ignore[import-untyped]

        self._key_map = _build_map()
        self._shift_codes = frozenset({ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT})
        self._caps_code = ecodes.KEY_CAPSLOCK

        for path in list_devices():
            try:
                dev = InputDevice(path)
                if _is_keyboard(dev):
                    self._devices.append(dev)
                    logger.info("Found keyboard: %s (%s)", dev.name, path)
            except (PermissionError, OSError) as exc:
                logger.warning("Cannot open %s: %s", path, exc)

        if not self._devices:
            raise RuntimeError(
                "No keyboard devices found or accessible.  "
                "Ensure the user is in the 'input' group: "
                "sudo usermod -aG input $USER"
            )

        for dev in self._devices:
            dev.grab()  # type: ignore[attr-defined]
            logger.info("Grabbed %s", dev.name)  # type: ignore[attr-defined]

        self._stop.clear()
        for dev in self._devices:
            t = threading.Thread(
                target=self._reader,
                args=(dev,),
                daemon=True,
                name=f"evdev-{dev.name}",  # type: ignore[attr-defined]
            )
            t.start()
            self._threads.append(t)

        self.active = True
        logger.info(
            "evdev grab active (%d device(s)). "
            "All keys suppressed at kernel level.",
            len(self._devices),
        )

    def release(self) -> None:
        if not self.active:
            return
        self._stop.set()
        for t in self._threads:
            t.join(timeout=1.0)
        for dev in self._devices:
            try:
                dev.ungrab()  # type: ignore[attr-defined]
                dev.close()   # type: ignore[attr-defined]
            except OSError:
                pass
        self._devices.clear()
        self._threads.clear()
        self.active = False
        logger.info("evdev grab released.")

    # ------------------------------------------------------------------
    # Background reader
    # ------------------------------------------------------------------

    def _reader(self, device: object) -> None:
        """Read raw events from one device and post synthetic pygame events."""
        # pylint: disable=import-outside-toplevel
        from evdev import ecodes  # type: ignore[import-untyped]
        fd = device.fd  # type: ignore[attr-defined]
        while not self._stop.is_set():
            try:
                r, _, _ = select.select([fd], [], [], 0.05)
            except (OSError, ValueError):
                break
            if not r:
                continue
            try:
                for ev in device.read():  # type: ignore[attr-defined]
                    if ev.type == ecodes.EV_KEY:
                        if ev.value == 1:
                            self._post(pygame.KEYDOWN, ev.code)
                        elif ev.value == 0:
                            self._post(pygame.KEYUP, ev.code)
                        # value == 2 (auto-repeat): skip
            except OSError:
                break

    def _post(self, event_type: int, evcode: int) -> None:
        """Convert an evdev keycode to a pygame event and post it."""
        entry = self._key_map.get(evcode)
        if entry is None:
            return
        pg_key, base_char, shifted_char = entry

        with self._mod_lock:
            if evcode in self._shift_codes:
                self._shift_held = event_type == pygame.KEYDOWN
            if evcode == self._caps_code and event_type == pygame.KEYDOWN:
                self._caps_lock = not self._caps_lock
            shift = self._shift_held
            caps = self._caps_lock

        if base_char.isalpha():
            uni = base_char.upper() if (shift ^ caps) else base_char
        elif shift and shifted_char:
            uni = shifted_char
        else:
            uni = base_char

        mod = pygame.KMOD_SHIFT if shift else 0
        pygame.event.post(pygame.event.Event(event_type, {
            "key":      pg_key,
            "scancode": 0,
            "mod":      mod,
            "unicode":  uni,
        }))
