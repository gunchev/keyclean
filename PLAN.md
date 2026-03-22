# KeyClean — Implementation Plan

Cross-platform keyboard cleaning utility: locks the keyboard, visualizes keypresses on a
virtual ISO 105-key layout, and suppresses input to the OS so the user can wipe their
physical keyboard without triggering commands.

## 1. Global Input Suppression — Feasibility

### Linux (X11)

**Feasible with `XGrabKeyboard`.**  Any X11 client can call `XGrabKeyboard` to redirect all
keyboard events to its own window. This is the same mechanism screen lockers use.

- Library: `python-xlib` (optional dependency).
- Privilege: none required.
- Caveat: Alt+F4 may be intercepted by the WM before the grab takes effect if the window is
  not fullscreen or `override_redirect`. Running fullscreen via pygame solves this.

### Linux (Wayland)

**Best-effort only.**  Wayland's security model prevents clients from grabbing global input.
SDL2 (≥ 2.28) supports `zwp_keyboard_shortcuts_inhibit_manager_v1`, which inhibits
compositor shortcuts (Super, Alt+Tab, etc.) while the window is focused and fullscreen on
supporting compositors (GNOME/Mutter, KDE/KWin, Sway).

- Kernel-level shortcuts (Ctrl+Alt+F*) cannot be blocked from userspace.
- The app will detect Wayland via `$XDG_SESSION_TYPE` and print a warning about limitations.

### macOS

**Feasible with `pynput`.**  Under the hood `pynput` uses `CGEventTap` from the Quartz
framework to intercept and suppress keyboard events system-wide.

- Privilege: Accessibility permission required (System Preferences → Privacy → Accessibility).
  The app will prompt the user on first launch.
- Touch Bar events are not covered; physical and external keyboards are.

### Windows

**Feasible with `pynput`.**  `pynput` uses `SetWindowsHookEx(WH_KEYBOARD_LL)` to install a
low-level keyboard hook that intercepts and can suppress all keystrokes.

- Privilege: no admin rights required.
- Caveat: `Ctrl+Alt+Del` (Secure Attention Sequence) always reaches the OS. Documented as
  expected behavior.

### Fallback

If native grabbing fails or `pynput` is unavailable, the app falls back to "pygame-only" mode
(fullscreen + SDL event capture). A warning banner is displayed in this mode since Alt+Tab
could still escape.

## 2. Handling High-Frequency Input (Keyboard Mashing)

USB HID keyboards poll at 125–1000 Hz. Mashing 10 keys generates up to ~20,000 events/sec
on a 1000 Hz keyboard.

**Strategy — decouple input from rendering:**

1. The event loop drains the **entire** `pygame.event.get()` queue every frame.
2. Rendering is capped at **60 FPS** (one render pass per frame).
3. Key state is a `set[int]` of currently-pressed scancodes; updated per event, rendered once.
4. A key that is pressed and released between two frames simply increments the counter without
   ever being visually highlighted — this is correct and acceptable.
5. SDL2's internal event queue holds up to 65,535 events. At 60 FPS we drain it every ~16 ms.
   Even at 20,000 events/sec that is ~333 events per frame — well within the buffer.
6. The strike counter is a plain `int` (Python ints are arbitrary precision).

**No throttling or debouncing is needed.**  The architecture is inherently safe.

## 3. Directory Structure

```
keyclean/
├── .editorconfig              # existing
├── .gitignore                 # new
├── LICENSE                    # new — Unlicense
├── Makefile                   # existing — updated
├── PLAN.md                    # this file
├── README.md                  # new — brief usage docs
├── pyproject.toml             # new — uv/pip build config
├── tox.ini                    # new — cross-version testing
├── src/
│   └── keyclean/
│       ├── __init__.py        # version string, package metadata
│       ├── __main__.py        # entry point: python -m keyclean
│       ├── app.py             # main App class, game loop, exit handling
│       ├── config.py          # constants: colors, sizes, exit phrase, FPS
│       ├── keyboard_layout.py # ISO 105-key definitions: positions, sizes, labels, keycodes
│       ├── renderer.py        # draws date and time on top "+%Y-%m-%d %H:%M:%S.%N %z %Z", keyboard in the middle, highlights, counter, help text, "Done" button
│       ├── safety_sequence.py # ring buffer of typed chars, checks for "keys are clean"
│       └── input_grabber/
│           ├── __init__.py    # get_grabber() factory
│           ├── _base.py       # AbstractGrabber (Protocol / ABC)
│           ├── _pynput.py     # pynput-based grabber (macOS + Windows + Linux/X11 fallback)
│           ├── _x11.py        # XGrabKeyboard via python-xlib
│           ├── _wayland.py    # best-effort: rely on SDL2 shortcuts_inhibit, warn user
│           └── _fallback.py   # pygame-only mode with warning banner
└── tests/
    ├── conftest.py
    ├── test_app.py
    ├── test_keyboard_layout.py
    ├── test_renderer.py
    ├── test_safety_sequence.py
    └── test_input_grabber.py
```

## 4. Key Design Decisions

| Decision                          | Choice                      | Rationale                                                                                               |
|-----------------------------------|-----------------------------|---------------------------------------------------------------------------------------------------------|
| UI library                        | `pygame-ce`                 | Actively maintained, SDL2-backed, Wayland `shortcuts_inhibit` support                                   |
| Input suppression (macOS/Windows) | `pynput`                    | Unified API, well-maintained, avoids raw `ctypes`/`pyobjc`                                              |
| Input suppression (Linux X11)     | `python-xlib`               | `XGrabKeyboard` is the correct tool; `pynput` on X11 uses `Xlib` under the hood but doesn't expose grab |
| Input suppression (Linux Wayland) | SDL2 built-in               | Only option from userspace; document limitations                                                        |
| Keyboard layout                   | ISO 105-key                 | User requirement                                                                                        |
| Window mode                       | Fullscreen                  | Better input suppression, user requirement                                                              |
| Exit phrase                       | `keys are clean`            | User requirement — typed literally to exit                                                              |
| Exit button                       | "Done" button (mouse click) | Secondary exit method                                                                                   |
| Build backend                     | `hatchling`                 | Lightweight, modern, works with `uv`                                                                    |
| Python version                    | 3.9+                        | Broad compatibility                                                                                     |

## 5. Implementation Phases

### Phase 1 — Project Scaffold

- Create `pyproject.toml` with all dependencies and metadata.
- Create `src/keyclean/__init__.py` (version string).
- Create `src/keyclean/__main__.py` (`python -m keyclean` entry point).
- Create `tox.ini` for Python 3.9–3.13 testing.
- Create `.gitignore` (Python + pygame + build artifacts).
- Create `LICENSE` (Unlicense text).
- Update `Makefile`: fix `test_upload`/`upload` targets to use `keyclean-*`.
- Verify `uv sync` and `uv run python -m keyclean` work (app starts and immediately exits).

### Phase 2 — Keyboard Layout Data

- Define the ISO 105-key layout in `keyboard_layout.py`:
    - Each key: `(row, col, width, height, label, pygame_keycode, scancode)`.
    - Rows: Esc/F-keys, number row, QWERTY, home row, bottom row, space bar row.
    - Include: numpad, arrows, Insert/Delete/Home/End/PgUp/PgDn block.
    - The extra ISO key (between left Shift and Z).
- Define visual constants in `config.py`: key size in pixels, gap, colors, font sizes.

### Phase 3 — Renderer

- `renderer.py`: pure rendering module, no input logic.
    - `draw_keyboard(surface, layout, pressed_keys)` — draws all keys; pressed keys highlighted.
    - `draw_counter(surface, count)` — persistent strike counter, top-right corner.
    - `draw_done_button(surface)` — clickable rectangle, returns its `Rect` for hit-testing.
    - `draw_warning_banner(surface, message)` — for fallback/Wayland mode warnings.
- Auto-scale the layout to fit the screen resolution.

### Phase 4 — Core App Loop

- `app.py`: `App` class and `main()` function.
- Flow:
    1. Initialize pygame, go fullscreen, hide mouse cursor (or keep for "Done" button).
    2. Acquire input grabber via `get_grabber()`.
    3. Main loop (60 FPS):
        - Drain all events from `pygame.event.get()`.
        - On `KEYDOWN`: add to `pressed_keys`, increment counter, feed char to safety sequence.
        - On `KEYUP`: remove from `pressed_keys`.
        - On `MOUSEBUTTONDOWN`: check hit on "Done" button → exit.
        - Render: keyboard, counter, button, optional warning banner.
    4. On exit: release grabber, quit pygame.

### Phase 5 — Safety Sequence

- `safety_sequence.py`:
    - `SafetySequence` class holding the target phrase (`"keys are clean"`).
    - Internal ring buffer (collections.deque with maxlen = len(phrase)).
    - `feed(char: str) -> bool`: appends char, returns `True` if buffer matches phrase.
    - Case-insensitive matching (so Caps Lock doesn't break it).
- Wire into `app.py`: on `KEYDOWN`, if the key maps to a printable char, feed it.

### Phase 6 — Input Grabbers

- `_base.py`: `AbstractGrabber` with `grab()` and `release()` methods.
- `_fallback.py`: no-op implementation; sets a flag for the warning banner.
- `_x11.py`: `XGrabKeyboard` on the pygame window's X11 window ID.
- `_pynput.py`: `pynput.keyboard.Listener` with `suppress=True` on macOS/Windows.
- `_wayland.py`: no-op (SDL2 handles it); sets a flag for the Wayland warning.
- `__init__.py` factory:
  ```
  platform → session type → try native grabber → fallback
  Linux + X11     → _x11.py (python-xlib)
  Linux + Wayland → _wayland.py (best-effort)
  macOS           → _pynput.py
  Windows         → _pynput.py
  any failure     → _fallback.py
  ```

### Phase 7 — Tests

- `test_safety_sequence.py`: feed exact phrase, partial, wrong chars, case variations.
- `test_keyboard_layout.py`: all 105 keys defined, no overlapping positions, all keycodes unique.
- `test_renderer.py`: mock `pygame.Surface`, verify `draw_*` functions call `blit`/`draw.rect`.
- `test_input_grabber.py`: factory returns correct grabber type per platform (mock `sys.platform`
  and env vars); grab/release lifecycle.
- `test_app.py`: simulate a sequence of `KEYDOWN`/`KEYUP` events, verify counter increments
  and exit on safety sequence.

### Phase 8 — Polish

- `tox.ini`: test matrix for Python 3.9–3.13.
- Verify `pylint` passes with the configured `max-line-length = 120`.
- Verify `autopep8` formatting.
- Write a brief `README.md` (installation, usage, exit methods, platform notes).
- Final `Makefile` cleanup.

## 6. Dependency Summary

| Package              | Required | Platform       | Purpose                     |
|----------------------|----------|----------------|-----------------------------|
| `pygame-ce` ≥ 2.4.0  | always   | all            | UI, event loop, rendering   |
| `pynput` ≥ 1.7.6     | optional | macOS, Windows | global keyboard suppression |
| `python-xlib` ≥ 0.33 | optional | Linux (X11)    | `XGrabKeyboard`             |
| `autopep8`           | dev      | all            | code formatting             |
| `pylint`             | dev      | all            | linting                     |
| `pytest`             | dev      | all            | testing                     |
| `pytest-mock`        | dev      | all            | input simulation in tests   |
| `pytest-cov`         | dev      | all            | coverage reporting          |
| `tox`                | dev      | all            | cross-version test runner   |
| `twine`              | dev      | all            | PyPI upload                 |
| `build`              | dev      | all            | wheel/sdist building        |

## 7. Open Risks & Mitigations

| Risk                                                                | Mitigation                                                                                      |
|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| Wayland compositor doesn't support `shortcuts_inhibit`              | Warning banner; document known compositors                                                      |
| `pynput` `suppress=True` conflicts with pygame's own event handling | `pynput` listener runs in its own thread; pygame only reads its internal SDL queue; no conflict |
| macOS Accessibility permission not granted                          | Detect failure, fall back to pygame-only mode with warning                                      |
| SDL2 version too old for Wayland inhibit                            | Check `pygame.get_sdl_version()` at startup; warn if < 2.28                                     |
| User types exit phrase accidentally during cleaning                 | Phrase `"keys are clean"` is 14 chars, highly unlikely from random mashing                      |
