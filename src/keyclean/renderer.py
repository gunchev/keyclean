"""Renderer — draws the full UI on a pygame Surface.

Layout (top → bottom):
  - Datetime bar     (top, full width)
  - Keyboard         (vertically centered in the remaining space)
  - Counter + help   (below keyboard)
  - Done button      (bottom-right corner)
  - Warning banner   (bottom, if needed)

No input logic here — only drawing.
"""

from __future__ import annotations

import datetime
from typing import Optional, Set, Tuple

import pygame

from keyclean import config
from keyclean.keyboard_layout import KEYS, PYGAME_KEY_MAP


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Fonts tried in order; all have good Unicode coverage (including arrow glyphs).
# match_font returns None when the font is absent, so we skip gracefully.
_FONT_CANDIDATES = [
    "DejaVu Sans Mono",   # Linux — usually pre-installed
    "Menlo",              # macOS — ships with the OS, full Unicode
    "Consolas",           # Windows — ships with the OS, full Unicode
    "Courier New",        # broad fallback
    "monospace",          # pygame generic alias
]


def _load_font(size: int) -> pygame.font.Font:
    for name in _FONT_CANDIDATES:
        path = pygame.font.match_font(name)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.SysFont("monospace", size)


def _scale(value: float, factor: float) -> int:
    return int(value * factor)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class Renderer:  # pylint: disable=too-few-public-methods
    """Stateless-ish renderer.  Recreated if the window is resized."""

    def __init__(self, screen_w: int, screen_h: int) -> None:
        self._sw = screen_w
        self._sh = screen_h

        # Compute scale factor so the keyboard fits horizontally with margin.
        # Total keyboard width in units:
        max_col_right = max(k.col + k.width for k in KEYS)
        max_row_bottom = max(k.row + k.height for k in KEYS)

        # Reserve top area for title + description + datetime, bottom for counter/help/done.
        top_reserve = int(screen_h * 0.18)
        bottom_reserve = int(screen_h * 0.15)
        kbd_area_h = screen_h - top_reserve - bottom_reserve

        h_scale = (screen_w * 0.95) / (max_col_right * (config.KEY_UNIT + config.KEY_GAP))
        v_scale = kbd_area_h / (max_row_bottom * (config.KEY_HEIGHT + config.KEY_GAP))
        self._scale = min(h_scale, v_scale)

        self._unit = config.KEY_UNIT * self._scale
        self._gap = config.KEY_GAP * self._scale
        self._key_h = config.KEY_HEIGHT * self._scale

        kbd_pixel_w = max_col_right * (self._unit + self._gap)
        kbd_pixel_h = max_row_bottom * (self._key_h + self._gap)

        self._kbd_x = (screen_w - kbd_pixel_w) / 2
        self._kbd_y = top_reserve + (kbd_area_h - kbd_pixel_h) / 2

        # Pre-compute pixel rects for each key
        self._key_rects: dict[str, pygame.Rect] = {}
        for key in KEYS:
            x = int(self._kbd_x + key.col * (self._unit + self._gap))
            y = int(self._kbd_y + key.row * (self._key_h + self._gap))
            w = int(key.width * (self._unit + self._gap) - self._gap)
            h = int(key.height * (self._key_h + self._gap) - self._gap)
            self._key_rects[key.key_id] = pygame.Rect(x, y, w, h)

        # Fonts (scaled relative to key size)
        s = self._scale
        self._font_key = _load_font(max(8, int(config.FONT_KEY_SIZE * s)))
        self._font_counter = _load_font(max(12, int(config.FONT_COUNTER_SIZE * s)))
        self._font_datetime = _load_font(max(12, int(config.FONT_DATETIME_SIZE * s)))
        self._font_title = _load_font(max(18, int(config.FONT_TITLE_SIZE * s)))
        self._font_desc = _load_font(max(10, int(config.FONT_DESC_SIZE * s)))
        self._font_help = _load_font(max(10, int(config.FONT_HELP_SIZE * s)))
        self._font_done = _load_font(max(12, int(config.FONT_DONE_SIZE * s)))

        # Done button rect (bottom-right)
        margin = int(config.DONE_BUTTON_MARGIN * s)
        btn_w = int(config.DONE_BUTTON_W * s)
        btn_h = int(config.DONE_BUTTON_H * s)
        self._done_rect = pygame.Rect(
            screen_w - btn_w - margin,
            screen_h - btn_h - margin,
            btn_w,
            btn_h,
        )

        # Pre-render key label surfaces for performance
        self._label_cache: dict[str, list[pygame.Surface]] = {}
        for key in KEYS:
            lines = key.label.split("\n")
            self._label_cache[key.key_id] = [
                self._font_key.render(line, True, config.COLOR_KEY_TEXT)
                for line in lines
                if line
            ]
        self._label_pressed_cache: dict[str, list[pygame.Surface]] = {}
        for key in KEYS:
            lines = key.label.split("\n")
            self._label_pressed_cache[key.key_id] = [
                self._font_key.render(line, True, config.COLOR_KEY_TEXT_PRESSED)
                for line in lines
                if line
            ]

    # ------------------------------------------------------------------
    # Main draw call
    # ------------------------------------------------------------------

    def draw(
        self,
        surface: pygame.Surface,
        pressed_keys: Set[int],
        strike_count: int,
        *,
        warning: Optional[str] = None,
        notice: Optional[str] = None,
        mouse_pos: Optional[Tuple[int, int]] = None,
    ) -> pygame.Rect:
        """Draw the full UI.  Returns the Done button Rect for hit-testing."""
        surface.fill(config.COLOR_BG)
        self._draw_header(surface)
        self._draw_keyboard(surface, pressed_keys)
        self._draw_counter(surface, strike_count)
        self._draw_help(surface, notice)
        self._draw_done_button(surface, mouse_pos)
        if warning:
            self._draw_warning(surface, warning)
        return self._done_rect

    # ------------------------------------------------------------------
    # Sub-draw helpers
    # ------------------------------------------------------------------

    def _draw_header(self, surface: pygame.Surface) -> None:
        # Title
        title_surf = self._font_title.render(config.APP_TITLE, True, config.COLOR_TITLE_TEXT)
        y = int(self._sh * 0.02)
        surface.blit(title_surf, ((self._sw - title_surf.get_width()) // 2, y))

        # Short description
        y += title_surf.get_height() + int(self._sh * 0.004)
        desc_surf = self._font_desc.render(config.APP_DESCRIPTION, True, config.COLOR_DESC_TEXT)
        surface.blit(desc_surf, ((self._sw - desc_surf.get_width()) // 2, y))

        # Datetime
        now = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()
        dt_str = now.strftime(config.DATETIME_FORMAT)
        if not config.DATETIME_SHOW_MS:
            dot_idx = dt_str.find(".")
            if dot_idx != -1:
                space_idx = dt_str.find(" ", dot_idx)
                dt_str = dt_str[:dot_idx] + (dt_str[space_idx:] if space_idx != -1 else "")
        elif "." in dt_str:
            # Show only milliseconds (3 digits) rather than all 6 microsecond digits
            dot_idx = dt_str.find(".")
            space_idx = dt_str.find(" ", dot_idx)
            dt_str = dt_str[:dot_idx + 4] + (dt_str[space_idx:] if space_idx != -1 else "")
        y += desc_surf.get_height() + int(self._sh * 0.006)
        dt_surf = self._font_datetime.render(dt_str, True, config.COLOR_DATETIME_TEXT)
        surface.blit(dt_surf, ((self._sw - dt_surf.get_width()) // 2, y))

    def _draw_keyboard(self, surface: pygame.Surface, pressed_keys: Set[int]) -> None:
        # Build set of key_ids that are currently pressed
        pressed_ids: Set[str] = set()
        for pk in pressed_keys:
            kd = PYGAME_KEY_MAP.get(pk)
            if kd:
                pressed_ids.add(kd.key_id)

        for key in KEYS:
            rect = self._key_rects[key.key_id]
            pressed = key.key_id in pressed_ids
            bg = config.COLOR_KEY_PRESSED if pressed else config.COLOR_KEY_NORMAL
            border = config.COLOR_KEY_BORDER

            pygame.draw.rect(surface, bg, rect, border_radius=4)
            pygame.draw.rect(surface, border, rect, width=1, border_radius=4)

            labels = (
                self._label_pressed_cache[key.key_id]
                if pressed
                else self._label_cache[key.key_id]
            )
            if labels:
                total_h = sum(s.get_height() for s in labels)
                y_start = rect.y + (rect.height - total_h) // 2
                for lbl_surf in labels:
                    lx = rect.x + (rect.width - lbl_surf.get_width()) // 2
                    surface.blit(lbl_surf, (lx, y_start))
                    y_start += lbl_surf.get_height()

    def _draw_counter(self, surface: pygame.Surface, count: int) -> None:
        text = f"Keys struck: {count:,}"
        surf = self._font_counter.render(text, True, config.COLOR_COUNTER_TEXT)
        x = int(self._sw * 0.02)
        # Place below the keyboard
        kbd_bottom = max(r.bottom for r in self._key_rects.values())
        y = kbd_bottom + int(self._key_h * 0.4)
        surface.blit(surf, (x, y))

    def _draw_help(self, surface: pygame.Surface, notice: Optional[str] = None) -> None:
        text = f'Type "{config.EXIT_PHRASE}" or click Done to exit'
        surf = self._font_help.render(text, True, config.COLOR_HELP_TEXT)
        kbd_bottom = max(r.bottom for r in self._key_rects.values())
        y = kbd_bottom + int(self._key_h * 0.4)
        surface.blit(surf, ((self._sw - surf.get_width()) // 2, y))
        if notice:
            nsurf = self._font_help.render(notice, True, config.COLOR_NOTICE_TEXT)
            y += surf.get_height() + int(self._key_h * 0.15)
            surface.blit(nsurf, ((self._sw - nsurf.get_width()) // 2, y))

    def _draw_done_button(
        self,
        surface: pygame.Surface,
        mouse_pos: Optional[Tuple[int, int]],
    ) -> None:
        hovered = mouse_pos is not None and self._done_rect.collidepoint(mouse_pos)
        bg = config.COLOR_DONE_BG_HOVER if hovered else config.COLOR_DONE_BG
        pygame.draw.rect(surface, bg, self._done_rect, border_radius=6)
        surf = self._font_done.render("Done", True, config.COLOR_DONE_TEXT)
        lx = self._done_rect.x + (self._done_rect.width - surf.get_width()) // 2
        ly = self._done_rect.y + (self._done_rect.height - surf.get_height()) // 2
        surface.blit(surf, (lx, ly))

    def _draw_warning(self, surface: pygame.Surface, message: str) -> None:
        padding = 8
        surf = self._font_help.render(message, True, config.COLOR_WARNING_TEXT)
        w = surf.get_width() + padding * 2
        h = surf.get_height() + padding * 2
        rect = pygame.Rect((self._sw - w) // 2, self._sh - h - 4, w, h)
        pygame.draw.rect(surface, config.COLOR_WARNING_BG, rect, border_radius=4)
        surface.blit(surf, (rect.x + padding, rect.y + padding))
