"""Constants: colors, sizes, FPS, exit phrase."""

from typing import Tuple

# --------------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------------- #
Color = Tuple[int, int, int]

# --------------------------------------------------------------------------- #
# Display
# --------------------------------------------------------------------------- #
TARGET_FPS: int = 60

# --------------------------------------------------------------------------- #
# Exit
# --------------------------------------------------------------------------- #
EXIT_PHRASE: str = "keys are clean"

# --------------------------------------------------------------------------- #
# Layout geometry
# --------------------------------------------------------------------------- #
# Base key size in pixels at reference resolution (1920×1080).
# The renderer scales these to fit the actual screen.
KEY_UNIT: int = 54          # width of one "1u" key
KEY_HEIGHT: int = 50        # height of all keys except tall Enter / numpad Enter
KEY_GAP: int = 4            # gap between keys

# --------------------------------------------------------------------------- #
# Colors  (R, G, B)
# --------------------------------------------------------------------------- #
COLOR_BG: Color = (18, 18, 18)
COLOR_KEY_NORMAL: Color = (55, 55, 60)
COLOR_KEY_PRESSED: Color = (80, 180, 255)
COLOR_KEY_BORDER: Color = (90, 90, 95)
COLOR_KEY_TEXT: Color = (220, 220, 220)
COLOR_KEY_TEXT_PRESSED: Color = (10, 10, 20)
COLOR_COUNTER_TEXT: Color = (200, 200, 200)
COLOR_DATETIME_TEXT: Color = (160, 200, 255)
COLOR_HELP_TEXT: Color = (130, 130, 140)
COLOR_NOTICE_TEXT: Color = (180, 140, 80)
COLOR_TITLE_TEXT: Color = (220, 220, 255)
COLOR_DESC_TEXT: Color = (140, 140, 160)
COLOR_DONE_BG: Color = (40, 140, 60)
COLOR_DONE_BG_HOVER: Color = (60, 200, 80)
COLOR_DONE_TEXT: Color = (255, 255, 255)
COLOR_WARNING_BG: Color = (160, 80, 0)
COLOR_WARNING_TEXT: Color = (255, 240, 180)

# --------------------------------------------------------------------------- #
# Typography
# --------------------------------------------------------------------------- #
FONT_KEY_SIZE: int = 13       # key label font size (scaled)
FONT_COUNTER_SIZE: int = 22
FONT_DATETIME_SIZE: int = 22
FONT_TITLE_SIZE: int = 36
FONT_DESC_SIZE: int = 16
FONT_HELP_SIZE: int = 16
FONT_DONE_SIZE: int = 20

# --------------------------------------------------------------------------- #
# Done button
# --------------------------------------------------------------------------- #
DONE_BUTTON_W: int = 120
DONE_BUTTON_H: int = 42
DONE_BUTTON_MARGIN: int = 20   # from bottom-right corner

# --------------------------------------------------------------------------- #
# Application header
# --------------------------------------------------------------------------- #
APP_TITLE: str = "KeyClean"
APP_DESCRIPTION: str = "Lock your keyboard, wipe it clean."

# --------------------------------------------------------------------------- #
# Datetime format  (strftime — %f is microseconds in Python; no %N)
# --------------------------------------------------------------------------- #
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f %z"
DATETIME_SHOW_MS: bool = False      # set True to show milliseconds
