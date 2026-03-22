# KeyClean

Cross-platform keyboard cleaning utility. Locks the keyboard, visualizes keypresses on a
full ISO 105-key layout, and suppresses input to the OS — so you can wipe your physical
keyboard without triggering commands.

> Vibe-coded using [Claude Sonnet 4.6](https://www.anthropic.com/claude).

## Installation

```bash
pip install keyclean
```

Platform extras for stronger input suppression:

```bash
pip install "keyclean[grab]"        # pynput (macOS / Windows)
pip install "keyclean[grab,linux]"  # pynput + python-xlib (Linux X11)
```

## Usage

```bash
keyclean
# or
python -m keyclean
# or from the dev tree
uv run keyclean
```

The application launches fullscreen. All keypresses are shown on the virtual keyboard and
counted but have no effect on the OS.

### Exit

- Type **`keys are clean`** on the physical keyboard, or
- Click the **Done** button with the mouse.

## Platform Notes

| Platform        | Suppression method       | Notes                                      |
|-----------------|--------------------------|--------------------------------------------|
| Linux (X11)     | `XGrabKeyboard`          | Full suppression while window is focused   |
| Linux (Wayland) | SDL2 `shortcuts_inhibit` | Best-effort; Ctrl+Alt+F* cannot be blocked |
| macOS           | `pynput` / CGEventTap    | Requires Accessibility permission          |
| Windows         | `pynput` / LowLevelHook  | Ctrl+Alt+Del cannot be blocked (by design) |

Without the optional extras the app falls back to pygame-only mode (fullscreen), which prevents
most accidental input but a warning banner is displayed.

## Development

Clone and set up the dev environment with [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/gunchev/keyclean
cd keyclean
uv sync --group dev              # core dev tools + pynput
uv sync --group dev --extra linux  # also install python-xlib (Linux X11)
```

Run the test suite:

```bash
uv run pytest
# or via make
make test

```

Lint and format:

```bash
make lint        # pylint
make pep8format  # autopep8
```

Build a wheel:

```bash
make build
```

Publish to PyPI / TestPyPI:

```bash
make upload       # PyPI
make test_upload  # TestPyPI
```

Dependency groups:

| Command                 | Installs                                                     |
|-------------------------|--------------------------------------------------------------|
| `uv sync --group dev`   | dev toolchain (pytest, pylint, autopep8, tox, twine, pynput) |
| `uv sync --extra grab`  | `pynput` (runtime, macOS/Windows suppression)                |
| `uv sync --extra linux` | `python-xlib` (runtime, Linux X11 suppression)               |
| `uv sync --extra macos` | `pyobjc-framework-Quartz` (runtime, macOS)                   |

## License

This is free and unencumbered software released into the public domain.
See [LICENSE](LICENSE) or <https://unlicense.org>.
