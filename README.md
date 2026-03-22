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

## License

This is free and unencumbered software released into the public domain.
See [LICENSE](LICENSE) or <https://unlicense.org>.
