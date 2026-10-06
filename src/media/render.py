from __future__ import annotations

import os

import pygame

from src.media import constants

CacheKey = tuple[tuple[int, int, int, int], tuple[int, int] | None]
ColorRGBA = tuple[int, int, int] | tuple[int, int, int, int]


class ImageLoader:
    """Loads a whole image file and scales it (no caching)."""

    @staticmethod
    def load_by_width(path: str, width: int) -> pygame.Surface:
        """Load an image and smooth-scale it to the given width, keeping aspect
        ratio."""
        image = pygame.image.load(path).convert_alpha()
        height = max(1, round(image.get_height() * width / image.get_width()))
        return pygame.transform.smoothscale(image, (width, height))

    @staticmethod
    def load_by_height(path: str, height: int) -> pygame.Surface:
        """Load an image and smooth-scale it to the given height, keeping
        aspect ratio."""
        image = pygame.image.load(path).convert_alpha()
        width = max(1, round(image.get_width() * height / image.get_height()))
        return pygame.transform.smoothscale(image, (width, height))


class FontCache:
    """Creates, caches and measures fonts."""

    def __init__(self) -> None:
        """Create an empty cache of fonts keyed by size."""
        self._cache: dict[int, pygame.font.Font] = {}

    @staticmethod
    def load(size: int) -> pygame.font.Font:
        """Build a new font (not cached)."""
        size = max(constants.MIN_FONT_SIZE, int(size))
        if os.path.exists(constants.FONT_FILE):
            font = pygame.font.Font(constants.FONT_FILE, size)
        else:
            font = pygame.font.SysFont(constants.FALLBACK_FONT_NAME, size)
        font.set_bold(constants.FONT_BOLD)
        return font

    def get(self, size: int) -> pygame.font.Font:
        """Return a cached font of this size."""
        size = max(constants.MIN_FONT_SIZE, int(size))
        font = self._cache.get(size)
        if font is None:
            font = self.load(size)
            self._cache[size] = font
        return font

    def fit_font(
        self, label: str, base_size: int, max_width: int
    ) -> pygame.font.Font:
        """Return the largest font, up to base_size, whose rendered label fits
        max_width."""
        for size in range(int(base_size), constants.MIN_FONT_SIZE, -1):
            font = self.get(size)
            if font.size(label)[0] <= max_width:
                return font
        return self.get(constants.MIN_FONT_SIZE)

    def fit_text(
        self,
        label: str,
        base_size: int,
        color: tuple[int, int, int],
        max_width: int,
    ) -> pygame.Surface:
        """Render the label with the largest font that fits max_width and
        return the surface."""
        font = self.fit_font(label, base_size, max_width)
        return font.render(label, True, color)

    @staticmethod
    def wrap_text(
        text: str, font: pygame.font.Font, max_width: int
    ) -> list[str]:
        """Split text into lines that each fit within max_width for the given
        font."""
        lines: list[str] = []
        current = ""
        for word in text.split():
            candidate = word if not current else f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = word
        if current:
            lines.append(current)
        return lines


class IconSheet:
    """A sprite sheet: cuts, scales and caches icons from one image."""

    def __init__(self, path: str) -> None:
        """Store the sheet path; the image loads lazily."""
        self.path: str = path
        self._sheet: pygame.Surface | None = None
        self._cache: dict[CacheKey, pygame.Surface] = {}

    def _load(self) -> pygame.Surface:
        """Load the sprite sheet on first use and return it."""
        if self._sheet is None:
            self._sheet = pygame.image.load(self.path).convert_alpha()
        return self._sheet

    def get(
        self, rect: pygame.Rect, size: tuple[int, int] | None = None
    ) -> pygame.Surface:
        """Return a cached copy of the rect, optionally scaled to the given
        size."""
        key = ((rect.x, rect.y, rect.width, rect.height), size)
        icon = self._cache.get(key)
        if icon is None:
            icon = self._load().subsurface(rect).copy()
            if size is not None:
                icon = pygame.transform.scale(icon, size)
            self._cache[key] = icon
        return icon

    def scaled_to_height(
        self, rect: pygame.Rect, height: int
    ) -> pygame.Surface:
        """Return the rect scaled to the given height, keeping aspect ratio."""
        width = max(1, round(rect.width * height / rect.height))
        return self.get(rect, (width, height))

    def scaled_by(self, rect: pygame.Rect, scale: float) -> pygame.Surface:
        """Return the rect scaled by a factor."""
        width = max(1, int(rect.width * scale))
        height = max(1, int(rect.height * scale))
        return self.get(rect, (width, height))


class Painter:
    """Drawing helpers: text, panels and the key-hint bar."""

    @staticmethod
    def text(
        screen: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        color: tuple[int, int, int],
        anchor_point: str,
        anchor_pos: tuple[int, int],
        shadow: tuple[int, int] | None = constants.SHADOW_OFFSET,
        clip_bottom: int | None = None,
        alpha: int | None = None,
    ) -> pygame.Rect:
        """Draw text (with optional shadow and alpha) at an anchor point and
        return its rect."""
        surface = font.render(text, True, color)
        if alpha is not None:
            surface.set_alpha(alpha)
        rect = surface.get_rect()
        setattr(rect, anchor_point, anchor_pos)

        if clip_bottom is not None and rect.bottom > clip_bottom:
            return rect

        if shadow is not None:
            shadow_surface = font.render(text, True, constants.SHADOW_COLOR)
            screen.blit(shadow_surface, rect.move(*shadow))
        screen.blit(surface, rect)
        return rect

    @staticmethod
    def panel(
        screen: pygame.Surface,
        rect: pygame.Rect,
        radius: int = 12,
        fill_alpha: int | None = None,
        border_color: ColorRGBA | None = None,
        border_width: int = 2,
        border_alpha: int = 255,
    ) -> None:
        """Draw a translucent rounded panel with an optional border onto the
        screen."""
        if fill_alpha is None:
            fill_alpha = constants.PANEL_ALPHA
        if border_color is None:
            border_color = constants.ACCENT_COLOR

        final_border_color: tuple[int, ...]
        if len(border_color) == 4:
            final_border_color = border_color
        else:
            final_border_color = (*border_color, border_alpha)

        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            surface,
            (0, 0, 0, fill_alpha),
            surface.get_rect(),
            border_radius=radius,
        )
        if border_width > 0:
            pygame.draw.rect(
                surface,
                final_border_color,
                surface.get_rect(),
                width=border_width,
                border_radius=radius,
            )
        screen.blit(surface, rect.topleft)

    @staticmethod
    def hint_bar(
        keys: list[tuple[str, str]], font: pygame.font.Font
    ) -> pygame.Surface:
        """Build a surface of key chips with action labels, used for the footer
        hints."""
        padx = constants.FOOTER_KEY_PADDING_X
        pady = constants.FOOTER_KEY_PADDING_Y

        pairs = [
            (
                font.render(key, True, constants.ACCENT_COLOR),
                font.render(action, True, constants.BODY_TEXT_COLOR),
            )
            for key, action in keys
        ]
        chip_h = font.get_height() + pady * 2
        widths = [
            key.get_width() + padx * 2
            + constants.FOOTER_LABEL_GAP + action.get_width()
            for key, action in pairs
        ]
        total = sum(widths) + constants.FOOTER_ITEM_GAP * (len(pairs) - 1)

        surface = pygame.Surface((total, chip_h), pygame.SRCALPHA)
        x = 0
        for (key, action), width in zip(pairs, widths):
            chip = pygame.Rect(x, 0, key.get_width() + padx * 2, chip_h)
            Painter.panel(
                surface, chip,
                radius=constants.FOOTER_KEY_RADIUS,
                fill_alpha=constants.FOOTER_KEY_ALPHA,
                border_color=constants.ACCENT_COLOR,
            )
            surface.blit(key, key.get_rect(center=chip.center))
            action_pos = (chip.right + constants.FOOTER_LABEL_GAP, chip_h // 2)
            surface.blit(action, action.get_rect(midleft=action_pos))
            x += width + constants.FOOTER_ITEM_GAP

        surface.set_alpha(min(255, constants.FOOTER_ALPHA))
        return surface


images = ImageLoader()
fonts = FontCache()
paint = Painter()

buttons = IconSheet(constants.BUTTON_SPRITE_FILE)
icons = IconSheet(constants.ICONS2_FILE)
more_icons = IconSheet(constants.MORE_ICONS_FILE)
us_sheet = IconSheet(constants.US_FILE)
social_sheet = IconSheet(constants.SOCIAL_FILE)

score_img = IconSheet(constants.SCORE_IMG)

ghosts = IconSheet(constants.GHOST_FILE)
gums = IconSheet(constants.GUMS_FILE)
eyes = IconSheet(constants.EYES_FILE)
timer = IconSheet(constants.TIMER_IMG)

gameover_icons = IconSheet(constants.GAMEOVER_ICONS_FILE)
key_icon = IconSheet(constants.KEY_FILE)

expressions = IconSheet(constants.EXPRESSIONS_FILE)

skin_border = IconSheet(constants.SKIN_BORDER_FILE)

SKINS_ICONSHEETS = [
    IconSheet(constants.SKINS[i]) for i in range(0, 12)
]

cheat_icons = IconSheet(constants.CHEAT_ICONS_FILE)

pause_icon = IconSheet(constants.PAUSE_BUTTON_FILE)

skins_sheet = IconSheet(constants.SKINS_SHEET_FILE)
