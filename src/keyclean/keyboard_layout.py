"""ISO 105-key keyboard layout definitions.

Each KeyDef describes one physical key:
  - key_id:   unique string identifier used internally
  - label:    text shown on the key (may be multi-line with '\\n')
  - col:      left edge in key-units (1u = KEY_UNIT px, gap not included here —
              positions are in abstract grid units)
  - row:      top edge in key-units
  - width:    key width in units  (1.0 = standard key)
  - height:   key height in units (1.0 = standard key)
  - pygame_key: pygame.locals K_* constant, or None for keys pygame doesn't map
  - highlight_key: if set, this pygame key triggers the pressed highlight instead of
              pygame_key.  Used for multi-rect keys (e.g. ISO Enter extension).

The layout is rendered at runtime scaled to the actual screen resolution.
Column and row values are in *units* where 1 unit = KEY_UNIT + KEY_GAP pixels.

ISO specifics vs ANSI:
  - Backslash key is 1.5u wide (col 13.5–15.0), right-aligned with Backspace.
  - Left Shift is 2.25u (ISO extra key omitted — no standard keycode).
  - Enter is drawn as a single rect in row 3 only ('enter_ext', col 12.75–15.0).
    The row-2 top stem is omitted; backslash fills that space to the right edge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pygame


@dataclass(frozen=True)
class KeyDef:
    """Definition of a single physical key."""
    key_id: str
    label: str
    col: float          # left edge in grid units
    row: float          # top edge in grid units
    width: float = 1.0  # width in grid units
    height: float = 1.0
    pygame_key: Optional[int] = None
    highlight_key: Optional[int] = None  # overrides pygame_key for pressed highlight


# Nav/numpad column offset — defined here so _ROW0 can reference it for
# PrtSc/ScrLk/Pause alignment above the Ins/Home/PgUp column.
_NAV_OFFSET: float = 15.5

# ---------------------------------------------------------------------------
# Row 0 — Escape + F-keys + system keys
# Sits 0.5u above row 1, creating a visible gap matching real keyboards.
# PrtSc/ScrLk/Pause are aligned with Ins/Home/PgUp below them.
# ---------------------------------------------------------------------------
_ROW0: List[KeyDef] = [
    KeyDef("esc",    "Esc",      0.0,  0, 1.0, 1.0, pygame.K_ESCAPE),
    # gap of 1.0u between Esc and F1
    KeyDef("f1",     "F1",       2.0,  0, 1.0, 1.0, pygame.K_F1),
    KeyDef("f2",     "F2",       3.0,  0, 1.0, 1.0, pygame.K_F2),
    KeyDef("f3",     "F3",       4.0,  0, 1.0, 1.0, pygame.K_F3),
    KeyDef("f4",     "F4",       5.0,  0, 1.0, 1.0, pygame.K_F4),
    # gap of 0.5u between F4 and F5
    KeyDef("f5",     "F5",       6.5,  0, 1.0, 1.0, pygame.K_F5),
    KeyDef("f6",     "F6",       7.5,  0, 1.0, 1.0, pygame.K_F6),
    KeyDef("f7",     "F7",       8.5,  0, 1.0, 1.0, pygame.K_F7),
    KeyDef("f8",     "F8",       9.5,  0, 1.0, 1.0, pygame.K_F8),
    # gap of 0.5u between F8 and F9
    KeyDef("f9",     "F9",       11.0, 0, 1.0, 1.0, pygame.K_F9),
    KeyDef("f10",    "F10",      12.0, 0, 1.0, 1.0, pygame.K_F10),
    KeyDef("f11",    "F11",      13.0, 0, 1.0, 1.0, pygame.K_F11),
    KeyDef("f12",    "F12",      14.0, 0, 1.0, 1.0, pygame.K_F12),
    # Aligned with Ins/Home/PgUp in the nav cluster below
    KeyDef("prtsc",  "Prt\nSc",  _NAV_OFFSET + 0.0, 0, 1.0, 1.0, pygame.K_PRINTSCREEN),
    KeyDef("scrlk",  "Scr\nLk",  _NAV_OFFSET + 1.0, 0, 1.0, 1.0, pygame.K_SCROLLLOCK),
    KeyDef("pause",  "Pause",    _NAV_OFFSET + 2.0, 0, 1.0, 1.0, pygame.K_PAUSE),
]

# ---------------------------------------------------------------------------
# Row 1 — Number row  (` 1 2 3 4 5 6 7 8 9 0 - = Backspace)
# ---------------------------------------------------------------------------
_ROW1: List[KeyDef] = [
    KeyDef("grave",  "`\n~",     0.0,  1.5, 1.0, 1.0, pygame.K_BACKQUOTE),
    KeyDef("1",      "1\n!",     1.0,  1.5, 1.0, 1.0, pygame.K_1),
    KeyDef("2",      "2\n@",     2.0,  1.5, 1.0, 1.0, pygame.K_2),
    KeyDef("3",      "3\n#",     3.0,  1.5, 1.0, 1.0, pygame.K_3),
    KeyDef("4",      "4\n$",     4.0,  1.5, 1.0, 1.0, pygame.K_4),
    KeyDef("5",      "5\n%",     5.0,  1.5, 1.0, 1.0, pygame.K_5),
    KeyDef("6",      "6\n^",     6.0,  1.5, 1.0, 1.0, pygame.K_6),
    KeyDef("7",      "7\n&",     7.0,  1.5, 1.0, 1.0, pygame.K_7),
    KeyDef("8",      "8\n*",     8.0,  1.5, 1.0, 1.0, pygame.K_8),
    KeyDef("9",      "9\n(",     9.0,  1.5, 1.0, 1.0, pygame.K_9),
    KeyDef("0",      "0\n)",     10.0, 1.5, 1.0, 1.0, pygame.K_0),
    KeyDef("minus",  "-\n_",     11.0, 1.5, 1.0, 1.0, pygame.K_MINUS),
    KeyDef("equals", "=\n+",     12.0, 1.5, 1.0, 1.0, pygame.K_EQUALS),
    KeyDef("bspace", "Backspace", 13.0, 1.5, 2.0, 1.0, pygame.K_BACKSPACE),
]

# ---------------------------------------------------------------------------
# Row 2 — QWERTY row  (Tab Q W E R T Y U I O P [ ] \|)
# ISO: Backslash is 1.5u (col 13.5–15.0), right-aligned with Backspace.
# ---------------------------------------------------------------------------
_ROW2: List[KeyDef] = [
    KeyDef("tab",    "Tab",      0.0,  2.5, 1.5, 1.0, pygame.K_TAB),
    KeyDef("q",      "Q",        1.5,  2.5, 1.0, 1.0, pygame.K_q),
    KeyDef("w",      "W",        2.5,  2.5, 1.0, 1.0, pygame.K_w),
    KeyDef("e",      "E",        3.5,  2.5, 1.0, 1.0, pygame.K_e),
    KeyDef("r",      "R",        4.5,  2.5, 1.0, 1.0, pygame.K_r),
    KeyDef("t",      "T",        5.5,  2.5, 1.0, 1.0, pygame.K_t),
    KeyDef("y",      "Y",        6.5,  2.5, 1.0, 1.0, pygame.K_y),
    KeyDef("u",      "U",        7.5,  2.5, 1.0, 1.0, pygame.K_u),
    KeyDef("i",      "I",        8.5,  2.5, 1.0, 1.0, pygame.K_i),
    KeyDef("o",      "O",        9.5,  2.5, 1.0, 1.0, pygame.K_o),
    KeyDef("p",      "P",        10.5, 2.5, 1.0, 1.0, pygame.K_p),
    KeyDef("lbrace", "[\n{",     11.5, 2.5, 1.0, 1.0, pygame.K_LEFTBRACKET),
    KeyDef("rbrace", "]\n}",     12.5, 2.5, 1.0, 1.0, pygame.K_RIGHTBRACKET),
    # ISO backslash — starts after ]}, extends right to align with Backspace (col 15.0)
    KeyDef("backslash", "\\\n|", 13.5, 2.5, 1.5, 1.0, pygame.K_BACKSLASH),
]

# ---------------------------------------------------------------------------
# Row 3 — Home row  (Caps A S D F G H J K L ; ' Enter)
# Enter occupies cols 12.75–15.0 (right-aligned with Backspace and RShift).
# ---------------------------------------------------------------------------
_ROW3: List[KeyDef] = [
    KeyDef("caps",   "Caps",     0.0,  3.5, 1.75, 1.0, pygame.K_CAPSLOCK),
    KeyDef("a",      "A",        1.75, 3.5, 1.0,  1.0, pygame.K_a),
    KeyDef("s",      "S",        2.75, 3.5, 1.0,  1.0, pygame.K_s),
    KeyDef("d",      "D",        3.75, 3.5, 1.0,  1.0, pygame.K_d),
    KeyDef("f",      "F",        4.75, 3.5, 1.0,  1.0, pygame.K_f),
    KeyDef("g",      "G",        5.75, 3.5, 1.0,  1.0, pygame.K_g),
    KeyDef("h",      "H",        6.75, 3.5, 1.0,  1.0, pygame.K_h),
    KeyDef("j",      "J",        7.75, 3.5, 1.0,  1.0, pygame.K_j),
    KeyDef("k",      "K",        8.75, 3.5, 1.0,  1.0, pygame.K_k),
    KeyDef("l",      "L",        9.75, 3.5, 1.0,  1.0, pygame.K_l),
    KeyDef("semi",   ";\n:",     10.75, 3.5, 1.0, 1.0, pygame.K_SEMICOLON),
    KeyDef("quote",  "'\n\"",    11.75, 3.5, 1.0, 1.0, pygame.K_QUOTE),
    # ISO Enter — occupies the full bottom body of the L-shape.
    KeyDef("enter_ext", "Enter", 12.75, 3.5, 2.25, 1.0, pygame.K_RETURN),
]

# ---------------------------------------------------------------------------
# Row 4 — Bottom row  (LShift Z X C V B N M , . / RShift)
# ---------------------------------------------------------------------------
_ROW4: List[KeyDef] = [
    KeyDef("lshift", "Shift",    0.0,  4.5, 2.25, 1.0, pygame.K_LSHIFT),
    KeyDef("z",      "Z",        2.25, 4.5, 1.0,  1.0, pygame.K_z),
    KeyDef("x",      "X",        3.25, 4.5, 1.0,  1.0, pygame.K_x),
    KeyDef("c",      "C",        4.25, 4.5, 1.0,  1.0, pygame.K_c),
    KeyDef("v",      "V",        5.25, 4.5, 1.0,  1.0, pygame.K_v),
    KeyDef("b",      "B",        6.25, 4.5, 1.0,  1.0, pygame.K_b),
    KeyDef("n",      "N",        7.25, 4.5, 1.0,  1.0, pygame.K_n),
    KeyDef("m",      "M",        8.25, 4.5, 1.0,  1.0, pygame.K_m),
    KeyDef("comma",  ",\n<",     9.25, 4.5, 1.0,  1.0, pygame.K_COMMA),
    KeyDef("period", ".\n>",     10.25, 4.5, 1.0, 1.0, pygame.K_PERIOD),
    KeyDef("slash",  "/\n?",     11.25, 4.5, 1.0, 1.0, pygame.K_SLASH),
    KeyDef("rshift", "Shift",    12.25, 4.5, 2.75, 1.0, pygame.K_RSHIFT),
]

# ---------------------------------------------------------------------------
# Row 5 — Space bar row  (LCtrl LMeta LAlt Space RAlt RMeta Menu RCtrl)
# ---------------------------------------------------------------------------
_ROW5: List[KeyDef] = [
    KeyDef("lctrl",  "Ctrl",     0.0,  5.5, 1.25, 1.0, pygame.K_LCTRL),
    KeyDef("lmeta",  "Meta",     1.25, 5.5, 1.25, 1.0, pygame.K_LMETA),
    KeyDef("lalt",   "Alt",      2.5,  5.5, 1.25, 1.0, pygame.K_LALT),
    KeyDef("space",  "",         3.75, 5.5, 6.25, 1.0, pygame.K_SPACE),
    KeyDef("ralt",   "Alt",      10.0, 5.5, 1.25, 1.0, pygame.K_RALT),
    KeyDef("rmeta",  "Meta",     11.25, 5.5, 1.25, 1.0, pygame.K_RMETA),
    KeyDef("menu",   "Menu",     12.5, 5.5, 1.25, 1.0, pygame.K_MENU),
    KeyDef("rctrl",  "Ctrl",     13.75, 5.5, 1.25, 1.0, pygame.K_RCTRL),
]

# ---------------------------------------------------------------------------
# Navigation cluster  (Insert Delete | Home End | PgUp PgDn | Up | Left Down Right)
# Col offset = _NAV_OFFSET (15.5u).  PrtSc/ScrLk/Pause in row 0 align above.
# ---------------------------------------------------------------------------
_NAV: List[KeyDef] = [
    # Row 1.5
    KeyDef("insert", "Ins",     _NAV_OFFSET + 0.0, 1.5, 1.0, 1.0, pygame.K_INSERT),
    KeyDef("home",   "Home",    _NAV_OFFSET + 1.0, 1.5, 1.0, 1.0, pygame.K_HOME),
    KeyDef("pgup",   "Pg\nUp",  _NAV_OFFSET + 2.0, 1.5, 1.0, 1.0, pygame.K_PAGEUP),
    # Row 2.5
    KeyDef("delete", "Del",     _NAV_OFFSET + 0.0, 2.5, 1.0, 1.0, pygame.K_DELETE),
    KeyDef("end",    "End",     _NAV_OFFSET + 1.0, 2.5, 1.0, 1.0, pygame.K_END),
    KeyDef("pgdn",   "Pg\nDn",  _NAV_OFFSET + 2.0, 2.5, 1.0, 1.0, pygame.K_PAGEDOWN),
    # Arrow keys — Up alone at row 4.5, Left/Down/Right at row 5.5
    KeyDef("up",     "↑",       _NAV_OFFSET + 1.0, 4.5, 1.0, 1.0, pygame.K_UP),
    KeyDef("left",   "←",       _NAV_OFFSET + 0.0, 5.5, 1.0, 1.0, pygame.K_LEFT),
    KeyDef("down",   "↓",       _NAV_OFFSET + 1.0, 5.5, 1.0, 1.0, pygame.K_DOWN),
    KeyDef("right",  "→",       _NAV_OFFSET + 2.0, 5.5, 1.0, 1.0, pygame.K_RIGHT),
]

# ---------------------------------------------------------------------------
# Numpad  — placed to the right of the nav cluster.
# Col offset = 19.0u from left.
# ---------------------------------------------------------------------------
_NP_OFFSET: float = 19.0

_NUMPAD: List[KeyDef] = [
    # Row 1.5
    KeyDef("np_lock",  "Num\nLk",  _NP_OFFSET + 0.0, 1.5, 1.0, 1.0, pygame.K_NUMLOCKCLEAR),
    KeyDef("np_slash", "/",        _NP_OFFSET + 1.0, 1.5, 1.0, 1.0, pygame.K_KP_DIVIDE),
    KeyDef("np_star",  "*",        _NP_OFFSET + 2.0, 1.5, 1.0, 1.0, pygame.K_KP_MULTIPLY),
    KeyDef("np_minus", "-",        _NP_OFFSET + 3.0, 1.5, 1.0, 1.0, pygame.K_KP_MINUS),
    # Row 2.5
    KeyDef("np_7",     "7",        _NP_OFFSET + 0.0, 2.5, 1.0, 1.0, pygame.K_KP7),
    KeyDef("np_8",     "8",        _NP_OFFSET + 1.0, 2.5, 1.0, 1.0, pygame.K_KP8),
    KeyDef("np_9",     "9",        _NP_OFFSET + 2.0, 2.5, 1.0, 1.0, pygame.K_KP9),
    KeyDef("np_plus",  "+",        _NP_OFFSET + 3.0, 2.5, 1.0, 2.0, pygame.K_KP_PLUS),
    # Row 3.5
    KeyDef("np_4",     "4",        _NP_OFFSET + 0.0, 3.5, 1.0, 1.0, pygame.K_KP4),
    KeyDef("np_5",     "5",        _NP_OFFSET + 1.0, 3.5, 1.0, 1.0, pygame.K_KP5),
    KeyDef("np_6",     "6",        _NP_OFFSET + 2.0, 3.5, 1.0, 1.0, pygame.K_KP6),
    # Row 4.5
    KeyDef("np_1",     "1",        _NP_OFFSET + 0.0, 4.5, 1.0, 1.0, pygame.K_KP1),
    KeyDef("np_2",     "2",        _NP_OFFSET + 1.0, 4.5, 1.0, 1.0, pygame.K_KP2),
    KeyDef("np_3",     "3",        _NP_OFFSET + 2.0, 4.5, 1.0, 1.0, pygame.K_KP3),
    KeyDef("np_enter", "Enter",    _NP_OFFSET + 3.0, 4.5, 1.0, 2.0, pygame.K_KP_ENTER),
    # Row 5.5
    KeyDef("np_0",     "0",        _NP_OFFSET + 0.0, 5.5, 2.0, 1.0, pygame.K_KP0),
    KeyDef("np_dot",   ".",        _NP_OFFSET + 2.0, 5.5, 1.0, 1.0, pygame.K_KP_PERIOD),
]

# ---------------------------------------------------------------------------
# Full layout
# ---------------------------------------------------------------------------
KEYS: List[KeyDef] = _ROW0 + _ROW1 + _ROW2 + _ROW3 + _ROW4 + _ROW5 + _NAV + _NUMPAD

# Mapping from pygame key constant → KeyDef (for fast lookup at runtime)
PYGAME_KEY_MAP: dict[int, KeyDef] = {
    key.pygame_key: key
    for key in KEYS
    if key.pygame_key is not None
}
