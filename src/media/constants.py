from __future__ import annotations

import os
from src.media.paths import resource_path
import pygame

# Asset directories
ASSETS_DIR: str = resource_path("assets")
VIDEO_DIR: str = os.path.join(ASSETS_DIR, "backgrounds")
MUSIC_DIR: str = os.path.join(ASSETS_DIR, "sounds", "music")
SFX_DIR: str = os.path.join(ASSETS_DIR, "sounds", "sfx")
EMOTE_SOUND_DIR: str = os.path.join(ASSETS_DIR, "sounds", "emote_sounds")
DIALOGUE_SOUND_DIR: str = os.path.join(ASSETS_DIR, "sounds", "dialogue")
MOUSE_DIR: str = os.path.join(ASSETS_DIR, "mouse")

# Fonts
FONT_FILE: str = os.path.join(ASSETS_DIR, "fonts/CornerD-Regular.ttf")
FALLBACK_FONT_NAME: str = "Courier New"
FONT_BOLD: bool = True
MIN_FONT_SIZE: int = 9
BASE_FONT_RATIO: float = 0.42
GUI_FONT_SIZE = 30

# Colors and text shadows
ACCENT_COLOR: tuple[int, int, int] = (196, 154, 108)
TITLE_COLOR: tuple[int, int, int] = (243, 244, 231)
BODY_TEXT_COLOR: tuple[int, int, int] = (244, 240, 225)
SHADOW_COLOR: tuple[int, int, int] = (0, 0, 0)
SHADOW_OFFSET: tuple[int, int] = (2, 2)
TITLE_SHADOW_OFFSET: tuple[int, int] = (3, 3)

# Generic panel
PANEL_ALPHA: int = 90

# Themes: background videos and blur
DEFAULT_THEME: int = 1
THEME_COUNT: int = 5
THEME_VIDEOS: dict[int, str] = {
    i: os.path.join(VIDEO_DIR, f"vid{i}.mp4")
    for i in range(1, THEME_COUNT + 1)
}
BLUR_LEVEL: float = 0.6
BLUR_MAX_KERNEL: int = 41

# Audio: music, sound effects and volumes
MUSIC_FILES: dict[int, str] = {
    i: os.path.join(MUSIC_DIR, f"music{i}.wav")
    for i in range(1, THEME_COUNT + 1)
}

SFX_FILES: dict[str, str] = {
    # menu
    "move": os.path.join(SFX_DIR, "sfx_move.wav"),
    "confirm": os.path.join(SFX_DIR, "sfx_confirm.wav"),
    "back": os.path.join(SFX_DIR, "sfx_back.wav"),
    # gameplay
    "gum": os.path.join(SFX_DIR, "gum.wav"),
    "super_gum": os.path.join(SFX_DIR, "super_gum.wav"),
    "ghost_eaten": os.path.join(SFX_DIR, "ghost_eaten.wav"),
    "key": os.path.join(SFX_DIR, "key.wav"),
    "countdown": os.path.join(SFX_DIR, "countdown.wav"),
    "level_win": os.path.join(SFX_DIR, "level_win.wav"),
    "level_lost": os.path.join(SFX_DIR, "level_lost.wav"),
    # cheats
    "invisible": os.path.join(SFX_DIR, "invisibility.wav"),
    "god_mode": os.path.join(SFX_DIR, "god_mode.wav"),
    "freeze": os.path.join(SFX_DIR, "freeze.wav"),
    # emote
    "emote_hover": os.path.join(EMOTE_SOUND_DIR, "hover.wav"),
    "emote_afk": os.path.join(EMOTE_SOUND_DIR, "afk.wav"),
    # instructions dialogue voices
    "finn_talks": os.path.join(DIALOGUE_SOUND_DIR, "finn_talks.wav"),
    "eyomi_talks": os.path.join(DIALOGUE_SOUND_DIR, "eyomi_talks.wav"),
    # door
    "door": os.path.join(SFX_DIR, "door.wav"),
    # timer
    "time_warning": os.path.join(SFX_DIR, "time_warning.wav"),
}

# emote mode
EMOTE_SOUNDS: dict[str, str] = {
    "hover": "emote_hover",
    "afk": "emote_afk",
}

MUSIC_VOLUME = 0.2
PLAYING_MUSIC_VOLUME = 0.12
SFX_VOLUME = 1.0

# Main menu: items, submenus and actions
MENU_ITEMS: list[str] = [
    "PLAY",
    "SETTINGS",
    "SCOREBOARD",
    "INSTRUCTIONS",
    "CREDITS",
    "EXIT",
]

SUBMENU_DEFS: dict[str, list[str]] = {
    "PLAY": ["1 PLAYER", "2 PLAYERS", "BACK"],
    "SETTINGS": ["THEMES", "SOUND", "BACK"],
    "THEMES": [f"THEME {i}" for i in range(1, THEME_COUNT + 1)] + ["BACK"],
}

THEME_LABEL_TO_NUMBER: dict[str, int] = {
    f"THEME {i}": i for i in range(1, THEME_COUNT + 1)
}

MENU_ACTIONS: dict[tuple[str, str], tuple[str, str | int | None]] = {
    ("MAIN", "EXIT"): ("quit", None),
    ("MAIN", "SCOREBOARD"): ("scoreboard_page", None),
    ("MAIN", "INSTRUCTIONS"): ("info_page", "INSTRUCTIONS"),
    ("MAIN", "CREDITS"): ("info_page", "CREDITS"),
    ("PLAY", "1 PLAYER"): ("skin_1p", None),
    ("PLAY", "2 PLAYERS"): ("skin_2p", None),
    ("SETTINGS", "SOUND"): ("sound_page", None),
}

# Menu buttons and icons: sprite sheets and rects
BUTTON_SPRITE_FILE: str = os.path.join(ASSETS_DIR, "sprites/buttons.png")
BUTTON_RECT: pygame.Rect = pygame.Rect(3, 2, 90, 27)
BUTTON_PRESSED_RECT: pygame.Rect = pygame.Rect(99, 4, 90, 25)

ICONS2_FILE: str = os.path.join(ASSETS_DIR, "sprites/icons2.png")
ICON_RECTS: dict[str, dict[str, pygame.Rect]] = {
    "PLAY": {
        "normal": pygame.Rect(645, 100, 22, 24),
        "pressed": pygame.Rect(677, 102, 22, 22),
    },
    "SETTINGS": {
        "normal": pygame.Rect(645, 68, 22, 24),
        "pressed": pygame.Rect(677, 70, 22, 22),
    },
    "SCOREBOARD": {
        "normal": pygame.Rect(773, 36, 22, 24),
        "pressed": pygame.Rect(805, 38, 22, 22),
    },
    "INSTRUCTIONS": {
        "normal": pygame.Rect(709, 132, 22, 24),
        "pressed": pygame.Rect(741, 134, 22, 22),
    },
    "CREDITS": {
        "normal": pygame.Rect(837, 36, 22, 24),
        "pressed": pygame.Rect(869, 38, 22, 22),
    },
    "EXIT": {
        "normal": pygame.Rect(837, 100, 22, 24),
        "pressed": pygame.Rect(869, 102, 22, 22),
    },
    "BACK": {
        "normal": pygame.Rect(773, 68, 22, 24),
        "pressed": pygame.Rect(805, 70, 22, 22),
    },
}

MORE_ICONS_FILE: str = os.path.join(ASSETS_DIR, "sprites/more_icons.png")
SUBMENU_ICON_RECTS: dict[str, dict[str, pygame.Rect]] = {
    "THEMES": {
        "normal": pygame.Rect(90, 65, 248, 273),
        "pressed": pygame.Rect(362, 65, 250, 273),
    },
    "1 PLAYER": {
        "normal": pygame.Rect(1537, 70, 255, 268),
        "pressed": pygame.Rect(1834, 69, 258, 271),
    },
    "2 PLAYERS": {
        "normal": pygame.Rect(103, 400, 253, 262),
        "pressed": pygame.Rect(379, 399, 265, 265),
    },
    "SOUND": {
        "normal": pygame.Rect(835, 401, 257, 260),
        "pressed": pygame.Rect(1124, 400, 248, 262),
    },
}

for _i in range(1, THEME_COUNT + 1):
    SUBMENU_ICON_RECTS[f"THEME {_i}"] = SUBMENU_ICON_RECTS["THEMES"]

# Menu carousel: arrows and layout
CAROUSEL_UP_ARROW: pygame.Rect = pygame.Rect(275, 36, 10, 9)
CAROUSEL_UP_ARROW_PRESSED: pygame.Rect = pygame.Rect(291, 36, 10, 9)
CAROUSEL_DOWN_ARROW: pygame.Rect = pygame.Rect(275, 52, 10, 9)
CAROUSEL_DOWN_ARROW_PRESSED: pygame.Rect = pygame.Rect(291, 52, 10, 9)

MAIN_BUTTON_HEIGHT: int = 89
SIDE_BUTTON_HEIGHT: int = 59
SIDE_ALPHA: int = 130
ICON_BUTTON_GAP: int = 10
CAROUSEL_GAP: int = 20
CAROUSEL_ARROW_SCALE: int = 3
CAROUSEL_ARROW_GAP: int = 14
CAROUSEL_ARROW_FLASH_MS: int = 150
CAROUSEL_TOP_GAP: int = 10
PRESS_FLASH_MS: int = 130

MAX_STRETCH_RATIO: float = 1.15
TEXT_PADDING_RATIO: float = 0.45

# Menu logo
LOGO_FILE: str = os.path.join(ASSETS_DIR, "sprites/logo.png")
LOGO_WIDTH_RATIO: float = 0.35
LOGO_TOP_OFFSET: int = 110

# Footer: key hints and styling
FOOTER_KEYS: list[tuple[str, str]] = [
    ("UP / DOWN", "MOVE"),
    ("ENTER", "SELECT"),
    ("ESC", "BACK"),
]

FOOTER_KEY_PADDING_X: int = 17
FOOTER_KEY_PADDING_Y: int = 6
FOOTER_KEY_RADIUS: int = 8
FOOTER_KEY_ALPHA: int = 140
FOOTER_LABEL_GAP: int = 10
FOOTER_ITEM_GAP: int = 40


FOOTER_ALPHA: int = 300
FOOTER_SIZE_RATIO: float = 0.016
FOOTER_BOTTOM_MARGIN: int = 14

# Dialogue box and emote (main menu mascot)
DIALOGUE_BOX: str = os.path.join(ASSETS_DIR, "sprites/dialogue.png")
EMOTES_FILE: str = os.path.join(ASSETS_DIR, "sprites/emotes.png")

DIALOGUE_WIDTH_RATIO: float = 0.25
DIALOGUE_PADDING: int = 10
DIALOGUE_SIZE_TEXT: str = "Welcome to PacMan"

DIALOGUE_TEXTS: list[str] = [
    "Welcome to PacMan",
    "Ready to eat?",
    "Snack time, hero!",
    "Waka waka waka!",
    "Grab all pellets!",
    "Pellets? Yes please",
    "Chomp chomp!",
    "Watch the ghosts!",
    "Blinky says boo!",
    "Pinky wants a hug",
    "Clyde is lost again",
    "Inky is plotting...",
    "Ghost? What ghost?",
    "Don't feed ghosts!",
    "Power up, player!",
    "Run! Then chomp!",
    "Revenge is sweet!",
    "Cherries = bonus!",
    "Tunnels are fun!",
    "Eat. Dodge. Win!",
    "Chase the score!",
    "Highscore hunter!",
    "Insert coin... jk",
    "Feeling hungry?",
    "Let's go, Pac!",
    "You got this!",
    "Good luck!",
]

DIALOGUE_HOVER_TEXTS: list[str] = [
    "Hey there!",
    "Hi hi hi!",
    "Want a snack?",
    "Pick me, pick me!",
    "Ooh, that tickles!",
    "Boo! Just kidding",
]

DIALOGUE_CLICK_TEXTS: list[str] = [
    "Ouch! Stop it!",
    "Hey, that hurts!",
    "Quit poking me!",
    "I'm not a button!",
    "Stop! I'm dizzy!",
    "Hands off, human!",
]

DIALOGUE_AFK_TEXTS: list[str] = [
    "Zzzzz...",
    "Zzz... Zzz...",
    "Zzzzz... waka...",
    "Snoring softly...",
]

DIALOGUE_TEXT_WIDTH_RATIO: float = 0.7
DIALOGUE_TEXT_PADDING_X: int = 113
DIALOGUE_TEXT_PADDING_Y: int = 65
DIALOGUE_EMOTE_BOTTOM_GAP: int = 103

TYPE_CHAR_MS: int = 90
TYPE_END_PAUSE_MS: int = 2000

EMOTE_RECTS: list[pygame.Rect] = [
    pygame.Rect(5, 2, 23, 30), pygame.Rect(5, 34, 23, 30),
    pygame.Rect(37, 34, 23, 30), pygame.Rect(5, 66, 25, 30),
    pygame.Rect(37, 66, 25, 30), pygame.Rect(69, 66, 25, 30),
    pygame.Rect(101, 66, 23, 30), pygame.Rect(133, 66, 23, 30),
    pygame.Rect(5, 98, 23, 30), pygame.Rect(37, 98, 23, 30),
    pygame.Rect(69, 98, 23, 30), pygame.Rect(101, 98, 23, 30),
]

EMOTE_HOVER_RECTS: list[pygame.Rect] = [
    pygame.Rect(5, 130, 26, 30), pygame.Rect(37, 130, 26, 30),
    pygame.Rect(5, 162, 26, 30), pygame.Rect(37, 162, 26, 30),
    pygame.Rect(3, 194, 26, 30), pygame.Rect(34, 193, 28, 31),
    pygame.Rect(3, 226, 26, 30), pygame.Rect(34, 225, 28, 31),
]
EMOTE_CLICK_RECTS: list[pygame.Rect] = [
    pygame.Rect(5, 290, 23, 30), pygame.Rect(37, 290, 23, 30),
    pygame.Rect(5, 322, 23, 30), pygame.Rect(37, 322, 23, 30),
]
EMOTE_AFK_RECTS: list[pygame.Rect] = [
    pygame.Rect(5, 386, 23, 30),
    pygame.Rect(5, 418, 26, 30), pygame.Rect(37, 418, 26, 30),
]

EMOTE_CLICK_IDLE_MS: int = 1500
EMOTE_AFK_MS: int = 10000
EMOTE_CLICKS_NEEDED: int = 3
EMOTE_CLICK_WINDOW_MS: int = 2000

EMOTE_FRAME_MS: int = 180
EMOTE_SIZE: int = 40
EMOTE_X_GAP: int = 35

# Info pages (shared layout) and back-to-menu button
INFO_TITLE_SIZE: int = 44
INFO_QUAD_TEXT_SIZE: int = 23
INFO_TOP_GAP: int = 55
INFO_BOTTOM_PADDING: int = 45
INFO_QUAD_GAP: int = 30
INFO_QUAD_PADDING: int = 70

INFO_NAV_BUTTON_HEIGHT: int = 70
INFO_NAV_BUTTON_BOTTOM_PADDING: int = 40
INFO_NAV_BUTTON_FONT_SIZE: int = 30
INFO_NAV_BUTTON_TEXT_COLOR: tuple[int, int, int] = ACCENT_COLOR

BACK_TO_MENU_OFFSET_X = INFO_QUAD_PADDING
BACK_TO_MENU_OFFSET_Y = 30
BACK_TO_MENU_ICON_HEIGHT = 70

# Instructions page: expressions sheet and conversation
EXPRESSIONS_FILE: str = os.path.join(ASSETS_DIR, "sprites/expressions.png")

RIGHT_EXPRESSION_RECTS: dict[str, pygame.Rect] = {
    "wondering": pygame.Rect(23, 223, 277, 259),
    "understanding": pygame.Rect(319, 225, 291, 257),
    "disappointed": pygame.Rect(625, 232, 271, 250),
    "happy": pygame.Rect(927, 232, 279, 250),
    "thinking": pygame.Rect(1230, 228, 290, 256),
}

LEFT_EXPRESSION_RECTS: dict[str, pygame.Rect] = {
    "wondering": pygame.Rect(13, 607, 291, 259),
    "understanding": pygame.Rect(315, 607, 296, 259),
    "disappointed": pygame.Rect(625, 605, 272, 261),
    "happy": pygame.Rect(923, 607, 296, 259),
    "thinking": pygame.Rect(1227, 606, 293, 260),
}

INSTRUCTIONS_DIALOGUE: list[tuple[str, str, str]] = [
    (
        "left",
        "wondering",
        "Uh... what even is this game? "
        "A yellow circle running from... ghosts?",
    ),
    (
        "right",
        "happy",
        "That's PAC-MAN! You're the yellow circle, "
        "and yes, four ghosts want you gone.",
    ),
    (
        "left",
        "thinking",
        "Okay... so how do I move this poor guy around?",
    ),
    (
        "right",
        "understanding",
        "Arrow keys or WASD. Up, down, left, right - simple as that.",
    ),
    (
        "left",
        "wondering",
        "And those little dots everywhere? Are they decoration?",
    ),
    (
        "right",
        "happy",
        "Those are gums! Walk over them to eat them and rack up points.",
    ),
    (
        "left",
        "disappointed",
        "Ugh, and the ghosts just... catch me eventually, don't they?",
    ),
    (
        "right",
        "understanding",
        "Not if you grab a super gum first! Those big ones in the corners.",
    ),
    (
        "left",
        "thinking",
        "What do those even do?",
    ),
    (
        "right",
        "happy",
        "They turn the ghosts blue and scared! "
        "Eat them for bonus points while they run.",
    ),
    (
        "left",
        "wondering",
        "Wait, there's also a key floating around somewhere?",
    ),
    (
        "right",
        "understanding",
        "Grab it to unlock the side tunnel - "
        "handy for a quick escape from ghosts!",
    ),
    (
        "left",
        "disappointed",
        "So what happens if a normal ghost touches me?",
    ),
    (
        "right",
        "thinking",
        "You lose a heart. Lose all three and it's game over, "
        "so watch those hearts up top.",
    ),
    (
        "left",
        "wondering",
        "And the clock in the corner - is it just for show?",
    ),
    (
        "right",
        "disappointed",
        "Nope, it's your timer! "
        "Clear the maze before it hits zero, or you lose the level.",
    ),
    (
        "left",
        "thinking",
        "There are like... a bunch of levels, right?",
    ),
    (
        "right",
        "happy",
        "Twenty in total! Level 10 is a checkpoint - "
        "lose after that and you only fall back to level 11.",
    ),
    (
        "left",
        "disappointed",
        "And if I lose before level 10?",
    ),
    (
        "right",
        "thinking",
        "Back to square one, level 1. So play it safe early on!",
    ),
    (
        "left",
        "wondering",
        "Oh hey, what do F1 through F4 do? "
        "I noticed they're not moving me.",
    ),
    (
        "right",
        "understanding",
        "Those are cheat keys! "
        "F1 makes you invisible to ghosts, they can't see you at all.",
    ),
    (
        "left",
        "thinking",
        "And the others?",
    ),
    (
        "right",
        "happy",
        "F2 freezes every ghost in place, "
        "F3 turns on god mode so you can't lose a life, "
        "and F4 instantly clears the level.",
    ),
    (
        "left",
        "disappointed",
        "That feels like cheating...",
    ),
    (
        "right",
        "thinking",
        "It literally is! "
        "Press the same key again to turn each one back off.",
    ),
    (
        "left",
        "happy",
        "Alright, I think I actually get it now. Let's eat some gums!",
    ),
    (
        "right",
        "happy",
        "That's the spirit! Good luck out there, waka waka!",
    ),
]

DIALOGUE_PAGE_TEXT_PADDING_X: int = 40
DIALOGUE_PAGE_TEXT_PADDING_Y: int = 22
DIALOGUE_PAGE_TEXT_LINE_GAP: int = 8
DIALOGUE_PAGE_TEXT_SIZE: int = 26
DIALOGUE_PAGE_TEXT_COLOR: tuple[int, int, int] = ACCENT_COLOR
DIALOGUE_PAGE_TYPE_CHAR_MS: int = 35
DIALOGUE_PAGE_BUBBLE_GAP: int = 30
DIALOGUE_PAGE_TEXT_WIDTH_RATIO: float = 0.38
CONV_FRAME_IMG: str = os.path.join(ASSETS_DIR, "sprites/conv_frame.png")
CONV_FRAME_SIZE: int = 325

LEFT_CHAR_OFFSET_X: int = 5
LEFT_CHAR_OFFSET_Y: int = -23
RIGHT_CHAR_OFFSET_X: int = -5
RIGHT_CHAR_OFFSET_Y: int = -23

DIALOGUE_PAGE_NAME_LEFT_TEXT: str = "FINN"
DIALOGUE_PAGE_NAME_RIGHT_TEXT: str = "EYOMI"
DIALOGUE_PAGE_NAME_SIZE: int = 30
DIALOGUE_PAGE_NAME_COLOR: tuple[int, int, int] = ACCENT_COLOR

LEFT_NAME_OFFSET_X: int = 0
LEFT_NAME_OFFSET_Y: int = -74
RIGHT_NAME_OFFSET_X: int = 0
RIGHT_NAME_OFFSET_Y: int = -74

DIALOGUE_PAGE_LEFT_IMAGE_SCALE: float = 0.5
DIALOGUE_PAGE_RIGHT_IMAGE_SCALE: float = 0.5

# Credits page: sprites, socials and layout
US_FILE: str = os.path.join(ASSETS_DIR, "sprites/us.png")
SOCIAL_FILE: str = os.path.join(ASSETS_DIR, "sprites/social.png")

US_LEFT_RECT: pygame.Rect = pygame.Rect(1167, 544, 287, 464)
US_RIGHT_RECT: pygame.Rect = pygame.Rect(1195, 78, 293, 442)
LINKEDIN_ICON_RECT: pygame.Rect = pygame.Rect(453, 209, 408, 408)
GITHUB_ICON_RECT: pygame.Rect = pygame.Rect(1332, 209, 408, 404)

CREDITS_LINE_GAP: int = 8

SOCIAL_ICON_TEXT_GAP: int = 16
SOCIAL_ROW_GAP: int = 14

CREDITS_NAME_SIZE: int = 40
CREDITS_TAGLINE_SIZE: int = 22
CREDITS_TAGLINE_GAP: int = 14
CREDITS_SPRITE_HEIGHT_RATIO: float = 0.42

CREDITS_TAGLINES: dict[str, str] = {
    "Finn": "Design, visuals & ideas.",
    "Eyomi": "Code, logic & bug slaying.",
}


SOCIAL_ENTRIES: list[tuple[pygame.Rect, str, str]] = [
    (LINKEDIN_ICON_RECT, "Finn", "Redouane Hssayn"),
    (LINKEDIN_ICON_RECT, "Eyomi", "Oumaima Bakri"),
    (GITHUB_ICON_RECT, "Eyomi", "8-hao"),
    (GITHUB_ICON_RECT, "Finn", "SupFinn"),
]

CREDITS_PEOPLE: list[tuple[pygame.Rect, str, str]] = [
    (US_LEFT_RECT, "Finn", "Redouane Hssayn"),
    (US_RIGHT_RECT, "Eyomi", "Oumaima Bakri"),
]

CREDITS_SOCIAL_ICON_SIZE: int = 32
CREDITS_PERSON_SOCIALS_GAP: int = 16

CREDITS_PERSON_PADDING: int = 24
CREDITS_PERSON_TEXT_GAP: int = 28

CREDITS_FLOAT_AMPLITUDE: int = 6
CREDITS_FLOAT_SPEED: float = 0.003

# Sound settings page
SOUND_METER_ICON_RECTS: dict[str, pygame.Rect] = {
    "MUSIC": pygame.Rect(54, 194, 4, 12),
    "SFX": pygame.Rect(54, 226, 4, 12),
}

SOUND_HINT_KEYS: list[tuple[str, str]] = [
    ("UP DOWN / W S", "SELECT"),
    ("LEFT RIGHT / A D", "CHANGE"),
    ("ESC", "BACK"),
]

SOUND_TITLE: str = "SOUND"
SOUND_STEP: float = 0.05
SLIDER_HINT_SIZE: int = 19
SOUND_LABEL_SIZE: int = 32
SOUND_PERCENT_SIZE: int = 25
SOUND_LABEL_GAP: int = 260
SOUND_METER_START_X: int = 190
SOUND_METER_MAX_TICKS: int = 20
SOUND_METER_TICK_SCALE: int = 4
SOUND_METER_TICK_GAP: int = 4
SOUND_METER_EMPTY_ALPHA: int = 45
SOUND_METER_HIGHLIGHT_PAD: int = 8
SOUND_METER_ROW_GAP: int = 110
SOUND_PERCENT_GAP: int = 16

SOUND_PANEL_WIDTH: int = 850
SOUND_PANEL_HEIGHT: int = 450
SOUND_PANEL_RADIUS: int = 20
SOUND_PANEL_FILL_ALPHA: int = 140

# Skin selection pages (1 player and 2 players)
SKIN_HINT_KEYS: list[tuple[str, str]] = [
    ("ARROWS / WASD", "MOVE"),
    ("ENTER", "PLAY"),
    ("ESC", "BACK"),
]

SKIN_2P_HINT_KEYS_1: list[tuple[str, str]] = [
    ("P1 WASD", "MOVE"),
    ("SPACE", "READY"),
]
SKIN_2P_HINT_KEYS_2: list[tuple[str, str]] = [
    ("P2 ARROWS", "MOVE"),
    ("ENTER", "READY"),
]

SKIN_HINT_SIZE: int = 19
SKIN_2P_HINT_SIZE: int = 15

READY_ICON_RECTS: dict[str, pygame.Rect] = {
    "ready": pygame.Rect(434, 71, 28, 18),
    "not_ready": pygame.Rect(498, 103, 28, 18),
}

SKIN_READY_GAP_2P: int = 80
READY_ICON_SCALE_2P: float = 2.2
SKIN_HINT_BOTTOM: int = 24
SKIN_2P_HINT_BOTTOM: int = 20
SKIN_2P_DIVIDER_TOP: int = 150
SKIN_2P_DIVIDER_BOTTOM: int = 56

SKIN_TITLE_TEXT: str = "CHOOSE YOUR SKIN"
SKIN_TITLE_TEXT_2P: str = "CHOOSE YOUR SKINS"
SKIN_TITLE_SIZE: int = 52
SKIN_TITLE_TOP: int = 60

SKIN_PLAYER_LABELS_2P: tuple[str, str] = ("PLAYER 1", "PLAYER 2")
SKIN_PLAYER_LABEL_SIZE: int = 30
SKIN_PLAYER_LABEL_GAP: int = 50

# Skin selection: border and carousel
SKIN_BORDER_FILE: str = os.path.join(ASSETS_DIR, "sprites/skin_border.png")
SKIN_BORDER_SIDE_RECT: pygame.Rect = pygame.Rect(99, 98, 42, 44)
SKIN_BORDER_MAIN_RECT: pygame.Rect = pygame.Rect(51, 98, 42, 44)

SKIN_BORDER_INNER_WIDTH_RATIO: float = 0.78
SKIN_BORDER_INNER_HEIGHT_RATIO: float = 0.74
SKIN_BORDER_INNER_OFFSET_X: int = 0
SKIN_BORDER_INNER_OFFSET_Y: int = -2

SKIN_CAROUSEL_LEFT_ARROW_RECT: pygame.Rect = pygame.Rect(276, 18, 7, 12)
SKIN_CAROUSEL_LEFT_ARROW_PRESSED_RECT: pygame.Rect = pygame.Rect(
    292, 18, 7, 12
)
SKIN_CAROUSEL_RIGHT_ARROW_RECT: pygame.Rect = pygame.Rect(277, 2, 7, 12)
SKIN_CAROUSEL_RIGHT_ARROW_PRESSED_RECT: pygame.Rect = pygame.Rect(
    293, 2, 7, 12
)

SKIN_CAROUSEL_MAIN_HEIGHT_RATIO: float = 0.22
SKIN_CAROUSEL_SIDE_HEIGHT_RATIO: float = 0.14
SKIN_CAROUSEL_MAIN_HEIGHT_RATIO_2P: float = 0.16
SKIN_CAROUSEL_SIDE_HEIGHT_RATIO_2P: float = 0.10

SKIN_CAROUSEL_GAP: int = 40
SKIN_CAROUSEL_GAP_2P: int = 24
SKIN_CAROUSEL_ARROW_GAP: int = 30
SKIN_CAROUSEL_ARROW_SCALE: int = 4
SKIN_CAROUSEL_ARROW_SCALE_2P: int = 3
SKIN_CAROUSEL_SIDE_ALPHA: int = 150

SKIN_CAROUSEL_BOB_AMPLITUDE: int = 6
SKIN_CAROUSEL_BOB_SPEED: float = 0.004

SKIN_NAMES: list[str] = [
    "Link",
    "SKIN 2",
    "Emilia",
    "SKIN 4",
    "SKIN 5",
    "SKIN 6",
    "Sans",
    "Sailor Moon",
    "Doraemon",
    "Son Goku",
    "Vegeta",
    "Minato Namikaze",
]

SKIN_NAME_SIZE: int = 26
SKIN_NAME_SIZE_2P: int = 18
SKIN_NAME_GAP: int = 18
SKIN_NAME_COLOR: tuple[int, int, int] = (255, 255, 255)

SKINS_SHEET_FILE: str = os.path.join(ASSETS_DIR, "skins/skins.png")

SKIN_PROFILE_RECTS: list[pygame.Rect] = [
    pygame.Rect(1167, 37, 319, 300),
    pygame.Rect(798, 682, 317, 297),
    pygame.Rect(1166, 682, 320, 296),
    pygame.Rect(417, 675, 319, 303),
    pygame.Rect(51, 680, 317, 300),
    pygame.Rect(419, 360, 319, 300),
    pygame.Rect(1166, 359, 316, 299),
    pygame.Rect(798, 360, 323, 298),
    pygame.Rect(49, 40, 319, 298),
    pygame.Rect(417, 40, 320, 298),
    pygame.Rect(795, 40, 319, 299),
    pygame.Rect(48, 355, 320, 304),
]

SKINS = [
    os.path.join(ASSETS_DIR, "skins", f"skin{i}.png")
    for i in range(1, 13)
]

SKIN_ICON_SCALE: float = 0.9


# Sprite frame helper (used by ghost and player skin animations)
def create_frames(
    right: list[pygame.Rect],
    up: list[pygame.Rect],
    left: list[pygame.Rect],
    down: list[pygame.Rect],
) -> dict[str, list[pygame.Rect]]:
    """Build a direction-keyed dict of frame rects (E, N, W, S) from the four
    lists."""
    return {
        "E": [pygame.Rect(rect) for rect in right],
        "N": [pygame.Rect(rect) for rect in up],
        "W": [pygame.Rect(rect) for rect in left],
        "S": [pygame.Rect(rect) for rect in down],
    }


# Player skin animation frames
SKIN1_FRAMES = create_frames(
    right=[
        pygame.Rect(135, 925, 95, 110),
        pygame.Rect(980, 930, 95, 105),
    ],
    up=[
        pygame.Rect(375, 780, 90, 120),
        pygame.Rect(975, 785, 90, 120),
    ],
    left=[
        pygame.Rect(130, 670, 95, 105),
        pygame.Rect(975, 665, 95, 105),
    ],
    down=[
        pygame.Rect(495, 530, 90, 120),
        pygame.Rect(975, 530, 90, 120),
    ],
)

###############################################################

SKIN2_FRAMES = create_frames(
    right=[
        pygame.Rect(6, 97, 29, 46),
        pygame.Rect(55, 97, 29, 45),
        pygame.Rect(102, 96, 29, 46),
        pygame.Rect(150, 97, 29, 45),
    ],
    up=[
        pygame.Rect(2, 145, 43, 46),
        pygame.Rect(49, 146, 43, 46),
        pygame.Rect(97, 145, 43, 46),
        pygame.Rect(145, 146, 43, 46),
    ],
    left=[
        pygame.Rect(13, 48, 31, 46),
        pygame.Rect(61, 49, 35, 45),
        pygame.Rect(109, 48, 31, 46),
        pygame.Rect(157, 49, 35, 45),
    ],
    down=[
        pygame.Rect(3, 0, 43, 47),
        pygame.Rect(51, 1, 43, 47),
        pygame.Rect(99, 0, 43, 47),
        pygame.Rect(147, 1, 43, 47),
    ],
)

###############################################################

SKIN3_FRAMES = create_frames(
    right=[
        pygame.Rect(11, 110, 24, 41),
        pygame.Rect(66, 111, 20, 40),
        pygame.Rect(113, 110, 24, 41),
        pygame.Rect(162, 111, 26, 40),
    ],
    up=[
        pygame.Rect(11, 161, 29, 41),
        pygame.Rect(60, 162, 28, 40),
        pygame.Rect(113, 161, 29, 41),
        pygame.Rect(166, 162, 29, 40),
    ],
    left=[
        pygame.Rect(16, 59, 24, 41),
        pygame.Rect(67, 60, 20, 40),
        pygame.Rect(118, 59, 25, 41),
        pygame.Rect(169, 60, 26, 40),
    ],
    down=[
        pygame.Rect(11, 8, 29, 41),
        pygame.Rect(60, 9, 30, 40),
        pygame.Rect(113, 8, 29, 41),
        pygame.Rect(167, 9, 28, 40),
    ],
)

###############################################################

SKIN4_FRAMES = create_frames(
    right=[
        pygame.Rect(5, 117, 41, 44),
        pygame.Rect(83, 118, 38, 44),
        pygame.Rect(158, 117, 38, 44),
        pygame.Rect(234, 118, 38, 44),
    ],
    up=[
        pygame.Rect(2, 168, 69, 48),
        pygame.Rect(77, 169, 69, 48),
        pygame.Rect(153, 171, 69, 48),
        pygame.Rect(227, 169, 69, 48),
    ],
    left=[
        pygame.Rect(28, 60, 41, 44),
        pygame.Rect(102, 61, 41, 44),
        pygame.Rect(178, 60, 41, 44),
        pygame.Rect(254, 61, 41, 44),
    ],
    down=[
        pygame.Rect(2, 4, 71, 44),
        pygame.Rect(77, 5, 71, 44),
        pygame.Rect(152, 4, 71, 44),
        pygame.Rect(227, 4, 71, 44),
    ],
)

###############################################################

SKIN5_FRAMES = create_frames(
    right=[
        pygame.Rect(11, 110, 24, 41),
        pygame.Rect(66, 111, 21, 40),
        pygame.Rect(113, 110, 24, 41),
        pygame.Rect(162, 111, 26, 40),
    ],
    up=[
        pygame.Rect(11, 161, 29, 42),
        pygame.Rect(60, 162, 28, 41),
        pygame.Rect(113, 161, 29, 42),
        pygame.Rect(167, 162, 28, 41),
    ],
    left=[
        pygame.Rect(16, 59, 24, 41),
        pygame.Rect(66, 60, 21, 40),
        pygame.Rect(118, 59, 24, 41),
        pygame.Rect(169, 60, 26, 40),
    ],
    down=[
        pygame.Rect(11, 8, 29, 42),
        pygame.Rect(60, 9, 28, 40),
        pygame.Rect(113, 8, 29, 42),
        pygame.Rect(167, 9, 28, 40),
    ],
)

###############################################################

SKIN6_FRAMES = create_frames(
    right=[
        pygame.Rect(5, 98, 22, 44),
        pygame.Rect(37, 99, 22, 43),
        pygame.Rect(68, 98, 22, 44),
        pygame.Rect(101, 99, 22, 43),
    ],
    up=[
        pygame.Rect(4, 147, 25, 43),
        pygame.Rect(38, 148, 22, 42),
        pygame.Rect(68, 147, 25, 43),
        pygame.Rect(101, 148, 22, 42),
    ],
    left=[
        pygame.Rect(5, 50, 22, 44),
        pygame.Rect(37, 51, 22, 44),
        pygame.Rect(69, 50, 22, 44),
        pygame.Rect(101, 51, 22, 43),
    ],
    down=[
        pygame.Rect(3, 2, 27, 45),
        pygame.Rect(35, 3, 27, 44),
        pygame.Rect(67, 2, 27, 45),
        pygame.Rect(99, 3, 27, 44),
    ],
)

###############################################################

SKIN7_FRAMES = create_frames(
    right=[
        pygame.Rect(7, 67, 17, 29),
        pygame.Rect(39, 66, 17, 30),
        pygame.Rect(71, 67, 17, 29),
        pygame.Rect(39, 66, 17, 30),
    ],
    up=[
        pygame.Rect(5, 98, 23, 30),
        pygame.Rect(37, 98, 23, 30),
        pygame.Rect(69, 98, 23, 30),
        pygame.Rect(37, 98, 23, 30),
    ],
    left=[
        pygame.Rect(8, 35, 17, 29),
        pygame.Rect(40, 34, 17, 30),
        pygame.Rect(72, 35, 17, 29),
        pygame.Rect(40, 34, 17, 30),
    ],
    down=[
        pygame.Rect(5, 2, 23, 30),
        pygame.Rect(37, 2, 23, 30),
        pygame.Rect(69, 2, 23, 30),
        pygame.Rect(37, 2, 23, 30),
    ],
)

###############################################################

SKIN8_FRAMES = create_frames(
    right=[
        pygame.Rect(5, 104, 18, 38),
        pygame.Rect(34, 104, 20, 38),
        pygame.Rect(68, 104, 18, 38),
        pygame.Rect(99, 105, 20, 38),
    ],
    up=[
        pygame.Rect(6, 152, 20, 38),
        pygame.Rect(38, 152, 22, 38),
        pygame.Rect(70, 152, 20, 38),
        pygame.Rect(100, 152, 22, 38),
    ],
    left=[
        pygame.Rect(9, 56, 18, 38),
        pygame.Rect(42, 56, 20, 38),
        pygame.Rect(73, 56, 18, 38),
        pygame.Rect(104, 56, 20, 38),
    ],
    down=[
        pygame.Rect(7, 8, 18, 38),
        pygame.Rect(38, 8, 20, 39),
        pygame.Rect(71, 8, 18, 38),
        pygame.Rect(101, 8, 20, 39),
    ],
)

###############################################################

SKIN9_FRAMES = create_frames(
    right=[
        pygame.Rect(4, 65, 26, 31),
        pygame.Rect(36, 64, 26, 31),
        pygame.Rect(68, 65, 26, 31),
        pygame.Rect(36, 64, 26, 31),
    ],
    up=[
        pygame.Rect(4, 97, 24, 30),
        pygame.Rect(36, 97, 24, 29),
        pygame.Rect(68, 97, 24, 30),
        pygame.Rect(36, 97, 24, 29),
    ],
    left=[
        pygame.Rect(2, 33, 26, 31),
        pygame.Rect(34, 33, 26, 30),
        pygame.Rect(66, 33, 26, 31),
        pygame.Rect(34, 33, 26, 30),
    ],
    down=[
        pygame.Rect(4, 2, 24, 30),
        pygame.Rect(36, 2, 24, 29),
        pygame.Rect(68, 2, 24, 30),
        pygame.Rect(36, 2, 24, 29),
    ],
)

###############################################################

SKIN10_FRAMES = create_frames(
    right=[
        pygame.Rect(6, 96, 21, 46),
        pygame.Rect(38, 97, 21, 45),
        pygame.Rect(70, 96, 21, 46),
        pygame.Rect(102, 97, 21, 45),
    ],
    up=[
        pygame.Rect(4, 144, 25, 46),
        pygame.Rect(36, 145, 25, 45),
        pygame.Rect(68, 144, 25, 46),
        pygame.Rect(100, 145, 25, 45),
    ],
    left=[
        pygame.Rect(5, 48, 21, 46),
        pygame.Rect(37, 49, 21, 45),
        pygame.Rect(69, 48, 21, 46),
        pygame.Rect(101, 49, 21, 45),
    ],
    down=[
        pygame.Rect(4, 0, 25, 46),
        pygame.Rect(36, 1, 25, 45),
        pygame.Rect(68, 0, 25, 46),
        pygame.Rect(99, 1, 25, 45),
    ],
)

###############################################################

SKIN11_FRAMES = create_frames(
    right=[
        pygame.Rect(4, 97, 20, 45),
        pygame.Rect(38, 98, 19, 44),
        pygame.Rect(68, 97, 20, 45),
        pygame.Rect(102, 98, 19, 44),
    ],
    up=[
        pygame.Rect(5, 144, 23, 46),
        pygame.Rect(38, 144, 21, 46),
        pygame.Rect(68, 144, 25, 46),
        pygame.Rect(100, 145, 25, 45),
    ],
    left=[
        pygame.Rect(8, 49, 20, 45),
        pygame.Rect(39, 50, 19, 44),
        pygame.Rect(72, 49, 20, 45),
        pygame.Rect(103, 50, 19, 44),
    ],
    down=[
        pygame.Rect(5, 0, 23, 46),
        pygame.Rect(38, 0, 20, 46),
        pygame.Rect(69, 0, 23, 46),
        pygame.Rect(103, 0, 20, 46),
    ],
)

###############################################################

SKIN12_FRAMES = create_frames(
    right=[
        pygame.Rect(4, 97, 21, 45),
        pygame.Rect(36, 98, 21, 44),
        pygame.Rect(68, 97, 21, 45),
        pygame.Rect(100, 98, 21, 44),
    ],
    up=[
        pygame.Rect(5, 145, 23, 45),
        pygame.Rect(37, 146, 23, 44),
        pygame.Rect(69, 145, 23, 45),
        pygame.Rect(101, 146, 23, 44),
    ],
    left=[
        pygame.Rect(7, 49, 21, 45),
        pygame.Rect(39, 50, 21, 44),
        pygame.Rect(71, 49, 21, 45),
        pygame.Rect(103, 50, 21, 44),
    ],
    down=[
        pygame.Rect(4, 3, 25, 43),
        pygame.Rect(37, 4, 24, 42),
        pygame.Rect(68, 3, 25, 43),
        pygame.Rect(100, 4, 24, 42),
    ],
)

FRAMES = [
    SKIN1_FRAMES, SKIN2_FRAMES, SKIN3_FRAMES, SKIN4_FRAMES,
    SKIN5_FRAMES, SKIN6_FRAMES, SKIN7_FRAMES, SKIN8_FRAMES,
    SKIN9_FRAMES, SKIN10_FRAMES, SKIN11_FRAMES, SKIN12_FRAMES,
]

# Ghosts: sprite sheets, animation frames and gameplay sizes
GHOST_FILE: str = os.path.join(ASSETS_DIR, "sprites/ghosts.png")
EYES_FILE: str = os.path.join(ASSETS_DIR, "sprites/eyes.png")

EYES_RECT: pygame.Rect = pygame.Rect(31, 31, 82, 42)

# blinky movement

BLINKY_FRAMES = create_frames(
    right=[
        pygame.Rect(0, 0, 179, 180),
        pygame.Rect(229, 0, 182, 180),
    ],
    up=[
        pygame.Rect(950, 0, 194, 178),
        pygame.Rect(1194, 0, 189, 186),
    ],
    left=[
        pygame.Rect(0, 236, 175, 182),
        pygame.Rect(235, 236, 182, 180),
    ],
    down=[
        pygame.Rect(463, 0, 195, 186),
        pygame.Rect(708, 0, 190, 178),
    ],
)
# clyde movements

CLYDE_FRAMES = create_frames(
    right=[
        pygame.Rect(480, 480, 180, 182),
        pygame.Rect(710, 475, 182, 183),
    ],
    up=[
        pygame.Rect(1427, 475, 184, 179),
        pygame.Rect(1661, 475, 180, 179),
    ],
    left=[
        pygame.Rect(0, 714, 180, 179),
        pygame.Rect(238, 714, 184, 178),
    ],
    down=[
        pygame.Rect(942, 475, 199, 182),
        pygame.Rect(1199, 475, 178, 179),
    ],
)

# Inky movement

INKY_FRAMES = create_frames(
    right=[
        pygame.Rect(467, 239, 193, 186),
        pygame.Rect(710, 238, 205, 178),
    ],
    up=[
        pygame.Rect(1473, 238, 208, 179),
        pygame.Rect(1731, 239, 208, 179),
    ],
    left=[
        pygame.Rect(0, 475, 186, 181),
        pygame.Rect(236, 475, 192, 181),
    ],
    down=[
        pygame.Rect(980, 238, 189, 179),
        pygame.Rect(1219, 242, 204, 181),
    ],
)

# Pinky movement
PINKY_FRAMES = create_frames(
    right=[
        pygame.Rect(472, 714, 181, 188),
        pygame.Rect(703, 712, 199, 182),
    ],
    up=[
        pygame.Rect(1448, 712, 190, 183),
        pygame.Rect(1688, 712, 189, 180),
    ],
    left=[
        pygame.Rect(0, 955, 179, 178),
        pygame.Rect(229, 955, 184, 180),
    ],
    down=[
        pygame.Rect(952, 714, 191, 179),
        pygame.Rect(1201, 712, 197, 184),
    ],
)


BLUE_FRAMES = [
    pygame.Rect(690, 954, 181, 183),
    pygame.Rect(463, 955, 177, 184),
]

GHOST_SIZE_RATIO: float = 0.63
EYES_SIZE_RATIO: float = 0.32
GHOST_EAT_COOLDOWN_MS: int = 1000

# Gameplay rules
WIN_LEVEL: int = 10

# In-game sprites: gums, key and player size
GUMS_FILE: str = os.path.join(ASSETS_DIR, "sprites/gums.png")
GUM_RECT: pygame.Rect = pygame.Rect(192, 305, 240, 224)
SUPERGUM_RECT: pygame.Rect = pygame.Rect(1551, 144, 504, 472)

KEY_FILE: str = os.path.join(ASSETS_DIR, "sprites/key.png")

PLAYER_SIZE_RATIO: float = 0.87
KEY_SIZE_RATIO: float = 0.41
GUM_SIZE_RATIO: float = 0.22
SUPERGUM_SIZE_RATIO: float = 0.51

# In-game HUD: score, timer, hearts and pause button
SCORE_IMG: str = os.path.join(ASSETS_DIR, "sprites/score.png")
TIMER_IMG: str = os.path.join(ASSETS_DIR, "sprites/timer.png")

score_rect: pygame.Rect = pygame.Rect(135, 150, 793, 1320)

timer_rect: pygame.Rect = pygame.Rect(149, 0, 923, 886)

HEART_FILE: str = os.path.join(ASSETS_DIR, "sprites/heart.png")
HEART_WIDTH: int = 48
HEART_OFFSET_X: int = 9
HEART_OFFSET_Y: int = 77
HEART_GAP: int = -11

PAUSE_BUTTON_FILE: str = os.path.join(ASSETS_DIR, "sprites/pause_play.png")

PAUSE_BUTTON_RECT: pygame.Rect = pygame.Rect(97, 144, 417, 436)
PAUSE_BUTTON_PRESSED_RECT: pygame.Rect = pygame.Rect(609, 152, 421, 425)

PLAY_BUTTON_RECT: pygame.Rect = pygame.Rect(1125, 150, 420, 430)
PLAY_BUTTON_PRESSED_RECT: pygame.Rect = pygame.Rect(1658, 152, 420, 427)

PAUSE_BUTTON_ICON_HEIGHT: int = 55
PAUSE_BUTTON_OFFSET_X: int = 31
PAUSE_BUTTON_OFFSET_Y: int = 23

# Maze rendering
MAZE_MAX_WIDTH_RATIO: float = 0.68
MAZE_MAX_HEIGHT_RATIO: float = 1.0

MAZE_PANEL_FILL_ALPHA: int = 130
MAZE_PANEL_BORDER_ALPHA: int = 255
MAZE_TOP_PANEL_FILL_ALPHA_ACTIVE: int = 225
TOP_PANEL_EXTRA_MS: int = 100

WALLS_COLOR = (182, 155, 125)
WALLS_WIDTH = 3

# In-game side info panels (controls and cheat codes)
SIDE_INFO_WIDTH: int = 260
SIDE_INFO_HEIGHT: int = 220
SIDE_INFO_OUTER_MARGIN: int = 20
SIDE_INFO_BOTTOM_MARGIN: int = 20
SIDE_INFO_PANEL_PADDING: int = 20
SIDE_INFO_PANEL_RADIUS: int = 14
SIDE_INFO_PANEL_ALPHA: int = 120
SIDE_INFO_TITLE_SIZE: int = 24
SIDE_INFO_TEXT_SIZE: int = 17
SIDE_INFO_LINE_GAP: int = 8
SIDE_INFO_TITLE_GAP: int = 14
SIDE_INFO_TEXT_COLOR: tuple[int, int, int] = BODY_TEXT_COLOR

CONTROLS_TITLE: str = "CONTROLS"
CONTROLS_LINES: list[str] = [
    "ARROWS / WASD - MOVE",
    "ESC - PAUSE",
    "GRAB THE KEY TO OPEN",
    "THE SIDE TUNNEL",
    "SUPER GUM = GHOSTS FLEE",
]

CHEATS_TITLE: str = "CHEAT CODES"
CHEATS_LINES: list[str] = [
    "F1 - INVISIBILITY MODE",
    "F2 - GHOST FREEZE",
    "F3 - GOD MODE",
    "F4 - SKIP LEVEL",
    "PRESS AGAIN TO UNDO",
]

# Cheats: icons, popup and invisibility
CHEAT_ICONS_FILE: str = os.path.join(ASSETS_DIR, "sprites/cheat_icons.png")

CHEAT_ICON_RECTS: dict[str, pygame.Rect] = {
    "invisible": pygame.Rect(25, 217, 281, 292),
    "god_mode": pygame.Rect(336, 550, 274, 300),
    "skip_level": pygame.Rect(638, 216, 259, 289),
    "freeze": pygame.Rect(925, 549, 275, 301),
    "none": pygame.Rect(1233, 215, 273, 292),
}

CHEAT_POPUP_DURATION_MS: int = 1000
CHEAT_POPUP_ICON_HEIGHT: int = 110
CHEAT_POPUP_PANEL_PADDING: int = 40
CHEAT_POPUP_PANEL_RADIUS: int = 16
CHEAT_POPUP_PANEL_ALPHA: int = 230

CHEAT_POPUP_TEXTS: dict[str, tuple[str, str]] = {
    "invisible": ("INVISIBILITY MODE", "They can't see me... waka waka!"),
    "god_mode": ("GOD MODE", "Lives don't matter anymore!"),
    "skip_level": ("SKIP LEVEL", "Skipping ahead to the next maze!"),
    "freeze": ("GHOST FREEZE", "The ghosts are stuck in place!"),
    "none": ("CHEATS OFF", "Back to playing fair."),
}

CHEAT_POPUP_TITLE_SIZE: int = 34
CHEAT_POPUP_SUBTITLE_SIZE: int = 20
CHEAT_POPUP_ICON_TEXT_GAP: int = 16
CHEAT_POPUP_TEXT_GAP: int = 10
CHEAT_POPUP_FADE_MS: int = 200

CHEAT_POPUP_COLORS: dict[str, tuple[int, int, int]] = {
    "invisible": (186, 120, 255),   # ghostly purple
    "god_mode": (255, 215, 0),      # gold
    "skip_level": (255, 60, 60),    # shiny red
    "freeze": (120, 220, 255),      # ice blue
    "none": ACCENT_COLOR,
}

INVISIBLE_PLAYER_ALPHA: int = 140

# Countdown overlay
COUNTDOWN_START: int = 3

COUNTDOWN_OVERLAY_ALPHA: int = 190

COUNTDOWN_LABEL_TEXT: str = "GET READY"
COUNTDOWN_LABEL_SIZE: int = 30
COUNTDOWN_LABEL_COLOR: tuple[int, int, int] = TITLE_COLOR
COUNTDOWN_LABEL_GAP: int = 20

COUNTDOWN_NUMBER_SIZE: int = 120
COUNTDOWN_NUMBER_COLOR: tuple[int, int, int] = ACCENT_COLOR
COUNTDOWN_NUMBER_SHADOW_OFFSET: tuple[int, int] = (4, 4)

COUNTDOWN_CIRCLE_RADIUS: int = 80
COUNTDOWN_CIRCLE_ALPHA: int = 160
COUNTDOWN_CIRCLE_BORDER_COLOR: tuple[int, int, int] = ACCENT_COLOR

# Pause menu
PAUSE_PANEL_ALPHA: int = 190
PAUSE_PANEL_BORDER_COLOR: tuple[int, int, int] = ACCENT_COLOR

PAUSE_TITLE_TEXT: str = "PAUSED"
PAUSE_TITLE_FONT_SIZE: int = 70
PAUSE_TITLE_COLOR: tuple[int, int, int] = ACCENT_COLOR

PAUSE_BUTTON_HEIGHT: int = 64
PAUSE_BUTTON_GAP: int = 22
PAUSE_BUTTON_FONT_SIZE: int = 24
PAUSE_BUTTON_TEXT_COLOR: tuple[int, int, int] = ACCENT_COLOR
PAUSE_TITLE_TO_BUTTONS_GAP: int = 50
PAUSE_BUTTON_LABELS: list[tuple[str, str]] = [
    ("RESUME", "resume"),
    ("RESTART LEVEL", "restart"),
    ("QUIT TO MENU", "quit"),
]

# Level select page
LEVELS_TITLE_TEXT: str = "CHOOSE LEVEL"
LEVELS_HINT_KEYS: list[tuple[str, str]] = [
    ("LEFT RIGHT / A D", "MOVE"),
    ("ENTER", "PLAY"),
    ("ESC", "BACK"),
]

LEVELS_TITLE_TOP: int = 60

LEVELS_HINT_SIZE: int = 19
LEVELS_HINT_BOTTOM: int = 24

LEVELS_NODE_COUNT: int = 20
LEVELS_NODE_RECT: pygame.Rect = pygame.Rect(11, 59, 26, 28)
LEVELS_NODE_PRESSED_RECT: pygame.Rect = pygame.Rect(107, 107, 26, 26)

LEVELS_NODE_SCALE: float = 3
LEVELS_STEP_X: int = 80
LEVELS_HIGH_RISE: int = 90
LEVELS_LINE_WIDTH: int = 6
LEVELS_LINE_COLOR: tuple[int, int, int] = ACCENT_COLOR
LEVELS_NUMBER_SIZE: int = 40

LEVELS_NUMBER_COLOR: tuple[int, int, int] = ACCENT_COLOR
LEVELS_NUMBER_PRESSED_COLOR: tuple[int, int, int] = (150, 105, 94)

LOCKED_LEVEL_FILE: str = os.path.join(ASSETS_DIR, "sprites/locked_level.png")
LEVELS_LOCKED_SCALE: float = 1.5

LEVELS_INFO_SIZE: int = 26


LEVELS_TITLE_SIZE: int = 52
LEVELS_TITLE_LINE_LEN: int = 160
LEVELS_TITLE_LINE_GAP: int = 28
LEVELS_TITLE_DIAMOND: int = 8
LEVELS_SUBTITLE_SIZE: int = 22
LEVELS_SUBTITLE_GAP: int = 14

LEVELS_INFO_TOP_GAP: int = 50

LEVELS_INFO_CARDS: list[tuple[str, str, str]] = [
    ("1 - 10", "MAIN", "BEAT THEM IN A ROW TO WIN THE GAME"),
    ("11 - 20", "OPTIONAL", "JUST FOR EXTRA CHALLENGE"),
]
LEVELS_CARD_WIDTH: int = 560
LEVELS_CARD_GAP: int = 30
LEVELS_CARD_PADDING: int = 20
LEVELS_CARD_ALPHA: int = 130
LEVELS_CARD_RANGE_SIZE: int = 32
LEVELS_CARD_TAG_SIZE: int = 18
LEVELS_TAG_TEXT_DARK: tuple[int, int, int] = (25, 18, 10)

# Level win screen
LEVEL_WIN_PANEL_PADDING_Y: int = 410
LEVEL_WIN_HEADLINE_OFFSET_Y: int = 60

LEVEL_WIN_HINT_TEXT: str = "PRESS ENTER FOR NEXT LEVEL"
LEVEL_WIN_HINT_SIZE: int = 18
LEVEL_WIN_HINT_COLOR: tuple[int, int, int] = BODY_TEXT_COLOR
LEVEL_WIN_HINT_TOP_GAP: int = 10
LEVEL_WIN_HINT_BOTTOM_GAP: int = 30

# Game win screen
WIN_PANEL_PADDING_Y: int = 330
WIN_HEADLINE_OFFSET_Y: int = 60
WIN_NAME_BOX_OFFSET_Y: int = 240

# Game over screen: panel, stats, name entry and buttons
GAMEOVER_ICONS_FILE: str = os.path.join(ASSETS_DIR,
                                        "sprites/gameover_icons.png")

GAMEOVER_STAT_ICON_RECTS: dict[str, pygame.Rect] = {
    "TIME": pygame.Rect(141, 171, 342, 402),
    "LEVEL": pygame.Rect(608, 167, 359, 410),
    "SCORE": pygame.Rect(1149, 207, 349, 356),
    "GUMS EATEN": pygame.Rect(1665, 262, 401, 255),
}

GAMEOVER_PANEL_WIDTH: int = 800
GAMEOVER_PANEL_RADIUS: int = 16
GAMEOVER_PANEL_ALPHA: int = 160
GAMEOVER_PANEL_BORDER_COLOR: tuple[int, int, int] = ACCENT_COLOR
GAMEOVER_PANEL_PADDING_Y: int = 190

GAMEOVER_TITLE_FONT_SIZE: int = 66
GAMEOVER_TITLE_COLOR: tuple[int, int, int] = ACCENT_COLOR
GAMEOVER_TITLE_GAP: int = 10
GAMEOVER_VALUE_COLOR: tuple[int, int, int] = (255, 255, 255)

GAMEOVER_STATS_OFFSET_Y: int = 300
GAMEOVER_STATS_LINE_GAP: int = 130
GAMEOVER_STATS_SECTION_GAP: int = 25
GAMEOVER_STATS_ICON_SIZE: int = 30

GAMEOVER_STATS_FONT_SIZE: int = 29
STATS_TITLE_FONT_SIZE: int = 40
GAMEOVER_STATS_COLOR: tuple[int, int, int] = ACCENT_COLOR

GAMEOVER_NAME_BOX_OFFSET_Y: int = 480

GAMEOVER_NAME_BOX_WIDTH_RATIO: float = 0.4
GAMEOVER_NAME_BOX_HEIGHT: int = 60
GAMEOVER_NAME_LABEL_GAP: int = 10
GAMEOVER_LABEL_FONT_SIZE: int = 22
GAMEOVER_INPUT_FONT_SIZE: int = 30
GAMEOVER_LABEL_COLOR: tuple[int, int, int] = ACCENT_COLOR
GAMEOVER_INPUT_COLOR: tuple[int, int, int] = TITLE_COLOR

GAMEOVER_INPUT_BORDER_COLOR: tuple[int, int, int] = (214, 168, 92)
GAMEOVER_INPUT_BORDER_COLOR_LOCKED: tuple[int, int, int] = (189, 129, 89)

GAMEOVER_INPUT_PANEL_ALPHA: int = 140
GAMEOVER_INPUT_PANEL_ALPHA_LOCKED: int = 100
GAMEOVER_INPUT_TEXT_ALPHA: int = 200
GAMEOVER_INPUT_TEXT_ALPHA_LOCKED: int = 100

GAMEOVER_SUBMIT_BUTTON_HEIGHT: int = 40
GAMEOVER_SUBMIT_BUTTON_GAP: int = 25

GAMEOVER_BUTTON_HEIGHT: int = 55
GAMEOVER_BUTTON_GAP: int = 106
GAMEOVER_BUTTON_OFFSET_Y: int = 65
GAMEOVER_BUTTON_FONT_SIZE: int = 24
GAMEOVER_BUTTON_TEXT_COLOR: tuple[int, int, int] = ACCENT_COLOR
GAMEOVER_BUTTON_LOCKED_ALPHA: int = 120

# Scoreboard page
SCOREBOARD_TITLE_TEXT: str = "SCOREBOARD"
SCOREBOARD_TITLE_SIZE: int = 44
SCOREBOARD_HEADER_SIZE: int = 20
SCOREBOARD_ROW_SIZE: int = 28

SCOREBOARD_MAX_ROWS: int = 10
SCOREBOARD_PANEL_RADIUS: int = 18
SCOREBOARD_PANEL_ALPHA: int = 130
SCOREBOARD_TITLE_GAP: int = 16
SCOREBOARD_HEADER_GAP: int = 10

SCOREBOARD_ROW_HEIGHT: int = 80
SCOREBOARD_ROW_GAP: int = 8
SCOREBOARD_ROW_RADIUS: int = 10
SCOREBOARD_ROW_ALPHA: int = 90
SCOREBOARD_ROW_PADDING_X: int = 20
SCOREBOARD_RANK_COL_WIDTH: int = 70

SCOREBOARD_RANK_COLORS: list[tuple[int, int, int]] = [
    (255, 215, 0),     # gold
    (210, 215, 225),   # silver
    (205, 127, 50),    # bronze
]
SCOREBOARD_EMPTY_TEXT: str = "---"
SCOREBOARD_EMPTY_ALPHA: int = 90

SCOREBOARD_COLUMN_GAP: int = 30
SCOREBOARD_TOP_MARGIN: int = 40
SCOREBOARD_BOTTOM_MARGIN: int = 40
SCOREBOARD_CARD_GAP: int = 20
SCOREBOARD_MAIN_WIDTH_RATIO: float = 0.45
SCOREBOARD_CARD_PADDING: int = 24

SCOREBOARD_CARD_TITLE_SIZE: int = 30
SCOREBOARD_CARD_LABEL_SIZE: int = 20
SCOREBOARD_CARD_VALUE_SIZE: int = 28
SCOREBOARD_CARD_FOOTER_SIZE: int = 18
SCOREBOARD_CARD_ROW_GAP: int = 16
SCOREBOARD_PANEL_PADDING: int = 30
SCOREBOARD_OUTER_GAP: int = 20
SCOREBOARD_CHAMPION_TITLE: str = "CHAMPION"
SCOREBOARD_CHAMPION_FOOTER: str = "Think you can beat it?"
SCOREBOARD_CHAMPION_EMPTY_FOOTER: str = "The throne is empty. Take it!"
SCOREBOARD_STATS_TITLE: str = "BOARD STATS"
SCOREBOARD_STATS_FOOTER: str = "Only the top 10 make the board."

# Mouse cursor
CURSOR_FILES: dict[str, str] = {
    "normal": os.path.join(MOUSE_DIR, "Triangle Mouse icon 1.png"),
    "hover": os.path.join(MOUSE_DIR, "Catpaw pointing Mouse icon.png"),
    "click": os.path.join(MOUSE_DIR, "Catpaw holding Mouse icon.png"),
}

CURSOR_HEIGHT: int = 25

CURSOR_HOTSPOTS: dict[str, tuple[float, float]] = {
    "normal": (0.0, 0.0),
    "hover": (0.35, 0.05),
    "click": (0.15, 0.05),
}
