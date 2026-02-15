# ----------------------------------------------------------------------------------------
#   sprites.py
#   ----------
#
#   Pixel art sprite definitions using rich 24-bit RGB colour. Each sprite uses
#   multiple colours for gradient and depth effects rather than flat single-colour
#   fills. Designed to fit an 80×24 terminal with a spacious, modern aesthetic.
#
#   (c) 2026 WaterJuice — Unlicense; see LICENSE in the project root.
#
#   Version History
#   ---------------
#   Feb 2026 - Created
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------------------------

from collections.abc import Mapping
from .display import Colour
from .display import Pixel

# ----------------------------------------------------------------------------------------
#   Types
# ----------------------------------------------------------------------------------------

type SpriteData = list[list[Pixel]]

# ----------------------------------------------------------------------------------------
#   Colour Palettes
# ----------------------------------------------------------------------------------------

# Alien Type 1 — Violet/Purple
_A1_LIGHT: Colour = (220, 160, 255)
_A1_MID: Colour = (160, 60, 255)
_A1_DARK: Colour = (100, 30, 180)

# Alien Type 2 — Warm Amber/Gold
_A2_LIGHT: Colour = (255, 220, 100)
_A2_MID: Colour = (255, 160, 40)
_A2_DARK: Colour = (200, 90, 10)

# Alien Type 3 — Cool Teal
_A3_LIGHT: Colour = (100, 255, 220)
_A3_MID: Colour = (30, 200, 170)
_A3_DARK: Colour = (10, 130, 110)

# Player — Blue Steel gradient
_PL_TIP: Colour = (220, 240, 255)
_PL_LIGHT: Colour = (120, 200, 255)
_PL_MID: Colour = (50, 140, 255)
_PL_DARK: Colour = (20, 70, 200)

# Mystery — Hot Pink / Gold
_MY_GOLD: Colour = (255, 210, 80)
_MY_PINK: Colour = (255, 60, 120)

# Shield — Electric Blue
_SH_EDGE: Colour = (100, 150, 255)
_SH_BODY: Colour = (50, 80, 200)

# Bullet colours
BULLET_CYAN: Colour = (120, 230, 255)
BULLET_ORANGE: Colour = (255, 140, 50)

# Explosion colours
_EX_WHITE: Colour = (255, 255, 180)
_EX_ORANGE: Colour = (255, 170, 50)
_EX_RED: Colour = (255, 70, 30)

# UI colours
SCORE_COLOUR: Colour = (200, 220, 255)
LIVES_COLOUR: Colour = (120, 200, 255)
GROUND_COLOUR: Colour = (30, 50, 80)

# Star colours (dim blue-whites for background)
STAR_COLOURS: list[Colour] = [
    (50, 55, 80),
    (65, 70, 100),
    (80, 90, 120),
    (100, 115, 145),
]

# ----------------------------------------------------------------------------------------
#   Helpers
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def _mc(pattern: list[str], colours: Mapping[str, Colour]) -> SpriteData:
    """
    Build a multi-colour sprite from an ASCII pattern and colour map.

    Each character in the pattern maps to a colour. '.' is always transparent.
    """
    return [[colours.get(ch) for ch in row] for row in pattern]


# ----------------------------------------------------------------------------------------
#   Alien Sprites — Type 1 (violet/purple, 6×5)
# ----------------------------------------------------------------------------------------

_A1 = {"a": _A1_LIGHT, "b": _A1_MID, "c": _A1_DARK}

ALIEN1_A: SpriteData = _mc(
    [
        "..ab..",
        ".abba.",
        "c.ab.c",
        ".abba.",
        ".c..c.",
    ],
    _A1,
)

ALIEN1_B: SpriteData = _mc(
    [
        "..ab..",
        ".abba.",
        "c.ab.c",
        ".abba.",
        "c....c",
    ],
    _A1,
)

# ----------------------------------------------------------------------------------------
#   Alien Sprites — Type 2 (amber/gold, 6×5)
# ----------------------------------------------------------------------------------------

_A2 = {"a": _A2_LIGHT, "b": _A2_MID, "c": _A2_DARK}

ALIEN2_A: SpriteData = _mc(
    [
        ".c..c.",
        ".abba.",
        "bbbbbb",
        ".a..a.",
        "c.ab.c",
    ],
    _A2,
)

ALIEN2_B: SpriteData = _mc(
    [
        ".c..c.",
        "bbbbbb",
        ".abba.",
        ".c..c.",
        ".c..c.",
    ],
    _A2,
)

# ----------------------------------------------------------------------------------------
#   Alien Sprites — Type 3 (teal/cyan, 6×5)
# ----------------------------------------------------------------------------------------

_A3 = {"a": _A3_LIGHT, "b": _A3_MID, "c": _A3_DARK}

ALIEN3_A: SpriteData = _mc(
    [
        ".abba.",
        "bbbbbb",
        "c.ab.c",
        "bbbbbb",
        ".c..c.",
    ],
    _A3,
)

ALIEN3_B: SpriteData = _mc(
    [
        ".abba.",
        "bbbbbb",
        "c.ab.c",
        "bbbbbb",
        "c....c",
    ],
    _A3,
)

# ----------------------------------------------------------------------------------------
#   Player Ship (9×4) — blue steel gradient, bright tip to dark base
# ----------------------------------------------------------------------------------------

_PL = {"a": _PL_TIP, "b": _PL_LIGHT, "c": _PL_MID, "d": _PL_DARK}

PLAYER: SpriteData = _mc(
    [
        "....a....",
        "...bcb...",
        ".bcccccb.",
        "dcccccccd",
    ],
    _PL,
)

# ----------------------------------------------------------------------------------------
#   Player Ship Small (for lives display, 5×3)
# ----------------------------------------------------------------------------------------

PLAYER_SMALL: SpriteData = _mc(
    [
        "..b..",
        ".ccc.",
        "dcccd",
    ],
    _PL,
)

# ----------------------------------------------------------------------------------------
#   Mystery Ship (10×3) — hot pink body with gold accents
# ----------------------------------------------------------------------------------------

_MY = {"a": _MY_GOLD, "b": _MY_PINK}

MYSTERY: SpriteData = _mc(
    [
        "..abbbba..",
        "aabbbbbbaa",
        ".b..ab..b.",
    ],
    _MY,
)

# ----------------------------------------------------------------------------------------
#   Shield (14×7) — electric blue dome, bright edges with deep core
# ----------------------------------------------------------------------------------------

_SH = {"a": _SH_EDGE, "b": _SH_BODY}

SHIELD: SpriteData = _mc(
    [
        "...aabbbbaa...",
        ".aabbbbbbbbaa.",
        "aabbbbbbbbbbaa",
        "bbbbbbbbbbbbbb",
        "bbbbbbbbbbbbbb",
        "bbbbb....bbbbb",
        "bbbb......bbbb",
    ],
    _SH,
)

# ----------------------------------------------------------------------------------------
#   Bullet Sprites
# ----------------------------------------------------------------------------------------

BULLET_PLAYER: SpriteData = [
    [BULLET_CYAN],
    [BULLET_CYAN],
    [BULLET_CYAN],
]

BULLET_ALIEN: SpriteData = [
    [BULLET_ORANGE],
    [BULLET_ORANGE],
]

# ----------------------------------------------------------------------------------------
#   Explosion (5×5) — bright core radiating outward
# ----------------------------------------------------------------------------------------

_EX = {"a": _EX_WHITE, "b": _EX_ORANGE, "c": _EX_RED}

EXPLOSION_1: SpriteData = _mc(
    [
        "c...c",
        ".b.b.",
        "..a..",
        ".b.b.",
        "c...c",
    ],
    _EX,
)

EXPLOSION_2: SpriteData = _mc(
    [
        ".b.b.",
        "..a..",
        ".bab.",
        "..a..",
        ".b.b.",
    ],
    _EX,
)

# ----------------------------------------------------------------------------------------
#   Sprite Dimensions
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def sprite_size(sprite: SpriteData) -> tuple[int, int]:
    """
    Get the width and height of a sprite.

    Returns:
        Tuple of (width, height).
    """
    if not sprite or not sprite[0]:
        return (0, 0)
    return (len(sprite[0]), len(sprite))
