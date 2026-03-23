## 0.9.4 — 2026-03-23

### Changes since v0.9.3

- 4487ba5 Post-release dev bump in release.py
- fdb53e7 Show version in title header

## 0.9.3 — 2026-03-23

### Changes since v0.9.2

- 64a9dee Make evdev a core dependency on Linux

## 0.9.2 — 2026-03-23

### Changes since v0.9.1

- 8a8050a Make 'run' target cross-platform via uname OS detection
- c2cdad9 Add 'make run' target for development
- cc2488e A bit more detailed coverage.

## 0.9.1 — 2026-03-23

### Changes since v0.9.0

- 76ff654 Clean "make clean"
- 4ca712c Clean up the clean target in Makefile
- fdb2860 Make release.py executable, update prompts.
- abdfb80 Move release logic to release.py; simplify Makefile target
- 01f9e3f Add evdev kernel-level grabber; prefer it on Linux
- 6f6a379 Re-assert Wayland keyboard grab on focus regain
- 23aca20 Append vibe-coding session prompts to PROMPT.md

## 0.9.0 — 2026-03-22

### Changes since beginning

- f0a2b04 Add uv run keyclean to README usage examples
- 785119a Add app header above clock; make milliseconds optional
- 2e9f934 Show /dev/input hint in UI below exit-phrase help text
- b09c869 Add make release target
- d42cc72 Fix Enter key overlapping Del — shorten #~ and backslash, shift Enter left
- d71cb0d Fix Wayland Super key leak — explicit zwp_keyboard_shortcuts_inhibit_manager_v1
- 0c4fb12 Add Development section to README, fix uv dep groups, add py314 to tox
- 0703c7b Silence pygame setuptools related depecation warnings.
- bdd632d Initial implementation of KeyClean 0.1.0
- 47251bc Minor plan adjustment, .gitignore.
- 0154a64 Start.

# Changelog

## 0.1.0 — 2026-03-22

Initial implementation.

### Added

- `pyproject.toml` — build config using `hatchling`, `pygame-ce` as core dependency,
  `pynput` and `python-xlib` as optional extras, full dev toolchain
  (`autopep8`, `pylint`, `pytest`, `pytest-mock`, `pytest-cov`, `tox`, `twine`, `build`).
- `tox.ini` — cross-version test matrix for Python 3.9–3.13.
- `README.md` — installation, usage, exit methods, platform notes.
- `LICENSE` — Unlicense.
- `.gitignore` — Python, uv, build artifact, and editor ignores.

#### `src/keyclean/`

- `__init__.py` — version (`0.1.0`), author, license metadata.
- `__main__.py` — `python -m keyclean` entry point.
- `config.py` — all constants: colors, key sizes, FPS (60), exit phrase
  (`"keys are clean"`), datetime format, Done button geometry.
- `keyboard_layout.py` — full ISO 105-key layout: rows 0–5 (Esc/F-keys, number row,
  QWERTY, home row, bottom row with ISO extra key, space bar row), navigation cluster
  (Insert/Delete/Home/End/PgUp/PgDn/arrows), numpad (17 keys including tall Enter and
  Plus). `PYGAME_KEY_MAP` dict for O(1) keycode lookup.
- `renderer.py` — `Renderer` class: auto-scales layout to screen resolution;
  draws datetime top bar (`YYYY-MM-DD HH:MM:SS.mmm ±HHMM TZ`), ISO keyboard in the
  middle with pressed-key highlighting, keystroke counter (bottom-left), help text
  (bottom-center), Done button (bottom-right, hover highlight), warning banner.
- `safety_sequence.py` — `SafetySequence`: `collections.deque` ring buffer,
  case-insensitive match against the exit phrase; `feed(char) -> bool`.
- `app.py` — `App` class: fullscreen pygame init, 60 FPS loop that drains the full
  SDL event queue each frame, tracks `pressed_keys: set[int]` and `strike_count: int`,
  feeds printable characters to `SafetySequence`, handles Done button mouse click.

#### `src/keyclean/input_grabber/`

- `_base.py` — `AbstractGrabber` ABC with `grab()`, `release()`, context manager.
- `_fallback.py` — No-op grabber; sets `is_fallback=True` to trigger warning banner.
- `_wayland.py` — Best-effort Wayland grabber; relies on SDL2
  `zwp_keyboard_shortcuts_inhibit_manager_v1`; warns if SDL2 < 2.28.
- `_x11.py` — Full keyboard grab via `XGrabKeyboard` (python-xlib); logs window ID.
- `_pynput.py` — Global suppression via `pynput.keyboard.Listener(suppress=True)`;
  used on macOS (CGEventTap) and Windows (LowLevelHook).
- `__init__.py` — `get_grabber()` factory: dispatches on `sys.platform` and
  `$XDG_SESSION_TYPE`; gracefully falls back through X11 → pynput → fallback.

#### `tests/`

- `conftest.py` — shared fixtures.
- `test_safety_sequence.py` — 9 tests: exact phrase, case-insensitive, partial,
  wrong chars, sliding ring buffer, reset, edge cases.
- `test_keyboard_layout.py` — 12 tests: key count (~105), unique IDs, unique pygame
  keycodes, map consistency, no zero-size keys, all labels present, ISO extra key,
  numpad completeness, F1–F12, arrows, row/col bounds.
- `test_renderer.py` — 8 tests: instantiation, Done rect returned and within screen,
  pressed keys, warning banner, counter values, small and large resolutions.
- `test_input_grabber.py` — 11 tests: FallbackGrabber lifecycle, context manager,
  WaylandGrabber SDL version warning, factory dispatch for unknown/Wayland/X11/macOS/Windows.
- `test_app.py` — 9 tests: `_key_to_char` filtering, exit phrase detection,
  counter initial state.

#### `Makefile`

- Updated `test_upload` and `upload` targets from `termcolor_dg-*` to `keyclean-*`.

### Result

- **52/52 tests passing.**
- **pylint 10.00/10.**

● All done. Here's the final state:

52/52 tests passing  •  pylint 10.00/10

Files created:

┌─────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────┐
│                  File                   │                                   Purpose                                   │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ .gitignore                              │ Updated with full Python/uv/build ignores                                   │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ LICENSE                                 │ Already existed (Unlicense)                                                 │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ README.md                               │ Installation, usage, platform notes                                         │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ tox.ini                                 │ Python 3.9–3.13 test matrix                                                 │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ pyproject.toml                          │ Build config, deps, pylint/pytest/autopep8 settings                         │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/__init__.py                │ Version, author, license metadata                                           │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/__main__.py                │ python -m keyclean entry point                                              │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/config.py                  │ All constants: colors, sizes, FPS, exit phrase, datetime format             │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/keyboard_layout.py         │ Full ISO 105-key definitions (rows 0–5 + nav cluster + numpad)              │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/renderer.py                │ Datetime top bar, keyboard, counter, help text, Done button, warning banner │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/safety_sequence.py         │ Ring buffer matching "keys are clean" case-insensitively                    │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/app.py                     │ Main loop, event drain, key state, exit handling                            │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/input_grabber/__init__.py  │ Platform-dispatch factory                                                   │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/input_grabber/_base.py     │ AbstractGrabber ABC                                                         │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/input_grabber/_fallback.py │ Pygame-only no-op with warning                                              │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/input_grabber/_wayland.py  │ Best-effort (SDL2 shortcuts_inhibit)                                        │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/input_grabber/_x11.py      │ XGrabKeyboard via python-xlib                                               │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ src/keyclean/input_grabber/_pynput.py   │ pynput suppress=True (macOS/Windows)                                        │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ tests/                                  │ 52 tests across all modules                                                 │
└─────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────┘

The warnings in the test output are all from the system's pkg_resources (pygame's dependency) — not from our code.

✻ Sautéed for 18m 23s
