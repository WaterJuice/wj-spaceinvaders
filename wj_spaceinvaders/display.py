# ----------------------------------------------------------------------------------------
#   display.py
#   ----------
#
#   Pixel buffer and ANSI half-block rendering system. Each terminal character cell
#   displays two vertical pixels using the lower half-block character (▄) with
#   24-bit ANSI colour codes: foreground = bottom pixel, background = top pixel.
#
#   Rendering approach adapted from wj-ansigame/screen.py.
#
#   (c) 2026 WaterJuice — Unlicense; see LICENSE in the project root.
#
#   Version History
#   ---------------
#   Feb 2026 - Created
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
#   Types
# ----------------------------------------------------------------------------------------

# RGB colour as (red, green, blue) tuple, each 0-255
type Colour = tuple[int, int, int]

# A pixel is either a colour or None (transparent/background)
type Pixel = Colour | None

# ----------------------------------------------------------------------------------------
#   Constants
# ----------------------------------------------------------------------------------------

_LOWER_HALF = "\u2584"
_RESET = "\033[0m"
_BLACK: Colour = (0, 0, 0)

# ----------------------------------------------------------------------------------------
#   Pixel Buffer
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class PixelBuffer:
    """
    An 80×48 RGB pixel framebuffer that renders to a standard 80×24 terminal.

    Uses a flat array of (r, g, b) tuples — every pixel is always a concrete
    colour (black for "empty"). Rendering uses the lower half-block character (▄)
    with bg = top pixel, fg = bottom pixel.

    Parameters:
        width: Width in pixels (= game columns).
        height: Height in pixels (= game rows × 2). Must be even.
        term_cols: Actual terminal width. If larger than width, output is centred.
        term_rows: Actual terminal height. If larger than height//2, output is centred.
    """

    def __init__(
        self,
        width: int,
        height: int,
        term_cols: int = 0,
        term_rows: int = 0,
    ) -> None:
        if height % 2 != 0:
            height += 1
        self.width = width
        self.height = height
        self.term_cols = max(term_cols, width)
        self.term_rows = max(term_rows, height // 2)
        self._buf: list[Colour] = [_BLACK] * (width * height)

    # ------------------------------------------------------------------------------------
    def clear(self, colour: Colour = _BLACK) -> None:
        """Fill the entire buffer with a single colour."""
        self._buf = [colour] * (self.width * self.height)

    # ------------------------------------------------------------------------------------
    def set_pixel(self, x: int, y: int, colour: Colour) -> None:
        """Set a single pixel. Out-of-bounds writes are silently ignored."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self._buf[y * self.width + x] = colour

    # ------------------------------------------------------------------------------------
    def get_pixel(self, x: int, y: int) -> Colour:
        """Get a single pixel. Returns black for out-of-bounds reads."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._buf[y * self.width + x]
        return _BLACK

    # ------------------------------------------------------------------------------------
    def draw_sprite(self, x: int, y: int, sprite: list[list[Pixel]]) -> None:
        """
        Draw a sprite (2D list of pixels) at the given position.

        Transparent (None) pixels in the sprite are not drawn.
        """
        for sy, row in enumerate(sprite):
            for sx, pixel in enumerate(row):
                if pixel is not None:
                    self.set_pixel(x + sx, y + sy, pixel)

    # ------------------------------------------------------------------------------------
    def fill_rect(self, x: int, y: int, w: int, h: int, colour: Colour) -> None:
        """Fill a rectangular area with a solid colour."""
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for py in range(y0, y1):
            off = py * self.width
            for px in range(x0, x1):
                self._buf[off + px] = colour

    # ------------------------------------------------------------------------------------
    def draw_text(self, x: int, y: int, text: str, colour: Colour) -> None:
        """
        Draw text using a simple built-in 3×5 pixel font.

        Each character is 4 pixels wide (3 + 1 spacing).
        """
        cx = x
        for ch in text:
            glyph = _FONT.get(ch)
            if glyph is not None:
                for gy, row in enumerate(glyph):
                    for gx, pixel_on in enumerate(row):
                        if pixel_on:
                            self.set_pixel(cx + gx, y + gy, colour)
            cx += 4

    # ------------------------------------------------------------------------------------
    def render(self) -> str:
        """
        Render the pixel buffer to a string of ANSI-coloured half-block characters.

        Uses cursor positioning per row for centering in larger terminals.
        Each cell emits a combined fg+bg escape with the ▄ character:
        bg = top pixel, fg = bottom pixel.

        Returns:
            String ready to write to the terminal.
        """
        buf = self._buf
        w = self.width
        half = _LOWER_HALF
        game_rows = self.height // 2
        pad_top = (self.term_rows - game_rows) // 2
        pad_left = (self.term_cols - w) // 2

        parts: list[str] = ["\033[H"]

        for row in range(0, self.height, 2):
            # Position cursor for this terminal row (1-indexed)
            term_row = pad_top + row // 2 + 1
            term_col = pad_left + 1
            parts.append(f"\033[{term_row};{term_col}H")

            top_off = row * w
            bot_off = top_off + w
            for col in range(w):
                tr, tg, tb = buf[top_off + col]
                br, bg, bb = buf[bot_off + col]
                parts.append(f"\033[38;2;{br};{bg};{bb};48;2;{tr};{tg};{tb}m{half}")

        parts.append(_RESET)
        return "".join(parts)


# ----------------------------------------------------------------------------------------
#   Built-in 3×5 Pixel Font
# ----------------------------------------------------------------------------------------

# Each glyph is a list of 5 rows, each row a list of 3 booleans
_FONT: dict[str, list[list[bool]]] = {
    "0": [
        [True, True, True],
        [True, False, True],
        [True, False, True],
        [True, False, True],
        [True, True, True],
    ],
    "1": [
        [False, True, False],
        [True, True, False],
        [False, True, False],
        [False, True, False],
        [True, True, True],
    ],
    "2": [
        [True, True, True],
        [False, False, True],
        [True, True, True],
        [True, False, False],
        [True, True, True],
    ],
    "3": [
        [True, True, True],
        [False, False, True],
        [True, True, True],
        [False, False, True],
        [True, True, True],
    ],
    "4": [
        [True, False, True],
        [True, False, True],
        [True, True, True],
        [False, False, True],
        [False, False, True],
    ],
    "5": [
        [True, True, True],
        [True, False, False],
        [True, True, True],
        [False, False, True],
        [True, True, True],
    ],
    "6": [
        [True, True, True],
        [True, False, False],
        [True, True, True],
        [True, False, True],
        [True, True, True],
    ],
    "7": [
        [True, True, True],
        [False, False, True],
        [False, False, True],
        [False, False, True],
        [False, False, True],
    ],
    "8": [
        [True, True, True],
        [True, False, True],
        [True, True, True],
        [True, False, True],
        [True, True, True],
    ],
    "9": [
        [True, True, True],
        [True, False, True],
        [True, True, True],
        [False, False, True],
        [True, True, True],
    ],
    "A": [
        [False, True, False],
        [True, False, True],
        [True, True, True],
        [True, False, True],
        [True, False, True],
    ],
    "B": [
        [True, True, False],
        [True, False, True],
        [True, True, False],
        [True, False, True],
        [True, True, False],
    ],
    "C": [
        [False, True, True],
        [True, False, False],
        [True, False, False],
        [True, False, False],
        [False, True, True],
    ],
    "D": [
        [True, True, False],
        [True, False, True],
        [True, False, True],
        [True, False, True],
        [True, True, False],
    ],
    "E": [
        [True, True, True],
        [True, False, False],
        [True, True, False],
        [True, False, False],
        [True, True, True],
    ],
    "F": [
        [True, True, True],
        [True, False, False],
        [True, True, False],
        [True, False, False],
        [True, False, False],
    ],
    "G": [
        [False, True, True],
        [True, False, False],
        [True, False, True],
        [True, False, True],
        [False, True, True],
    ],
    "H": [
        [True, False, True],
        [True, False, True],
        [True, True, True],
        [True, False, True],
        [True, False, True],
    ],
    "I": [
        [True, True, True],
        [False, True, False],
        [False, True, False],
        [False, True, False],
        [True, True, True],
    ],
    "J": [
        [False, False, True],
        [False, False, True],
        [False, False, True],
        [True, False, True],
        [False, True, False],
    ],
    "K": [
        [True, False, True],
        [True, False, True],
        [True, True, False],
        [True, False, True],
        [True, False, True],
    ],
    "L": [
        [True, False, False],
        [True, False, False],
        [True, False, False],
        [True, False, False],
        [True, True, True],
    ],
    "M": [
        [True, False, True],
        [True, True, True],
        [True, True, True],
        [True, False, True],
        [True, False, True],
    ],
    "N": [
        [True, False, True],
        [True, True, True],
        [True, True, True],
        [True, True, True],
        [True, False, True],
    ],
    "O": [
        [False, True, False],
        [True, False, True],
        [True, False, True],
        [True, False, True],
        [False, True, False],
    ],
    "P": [
        [True, True, False],
        [True, False, True],
        [True, True, False],
        [True, False, False],
        [True, False, False],
    ],
    "Q": [
        [False, True, False],
        [True, False, True],
        [True, False, True],
        [True, True, False],
        [False, True, True],
    ],
    "R": [
        [True, True, False],
        [True, False, True],
        [True, True, False],
        [True, False, True],
        [True, False, True],
    ],
    "S": [
        [False, True, True],
        [True, False, False],
        [False, True, False],
        [False, False, True],
        [True, True, False],
    ],
    "T": [
        [True, True, True],
        [False, True, False],
        [False, True, False],
        [False, True, False],
        [False, True, False],
    ],
    "U": [
        [True, False, True],
        [True, False, True],
        [True, False, True],
        [True, False, True],
        [False, True, False],
    ],
    "V": [
        [True, False, True],
        [True, False, True],
        [True, False, True],
        [True, False, True],
        [False, True, False],
    ],
    "W": [
        [True, False, True],
        [True, False, True],
        [True, True, True],
        [True, True, True],
        [True, False, True],
    ],
    "X": [
        [True, False, True],
        [True, False, True],
        [False, True, False],
        [True, False, True],
        [True, False, True],
    ],
    "Y": [
        [True, False, True],
        [True, False, True],
        [False, True, False],
        [False, True, False],
        [False, True, False],
    ],
    "Z": [
        [True, True, True],
        [False, False, True],
        [False, True, False],
        [True, False, False],
        [True, True, True],
    ],
    " ": [
        [False, False, False],
        [False, False, False],
        [False, False, False],
        [False, False, False],
        [False, False, False],
    ],
    "-": [
        [False, False, False],
        [False, False, False],
        [True, True, True],
        [False, False, False],
        [False, False, False],
    ],
    ".": [
        [False, False, False],
        [False, False, False],
        [False, False, False],
        [False, False, False],
        [False, True, False],
    ],
    ":": [
        [False, False, False],
        [False, True, False],
        [False, False, False],
        [False, True, False],
        [False, False, False],
    ],
    "!": [
        [False, True, False],
        [False, True, False],
        [False, True, False],
        [False, False, False],
        [False, True, False],
    ],
    "?": [
        [True, True, False],
        [False, False, True],
        [False, True, False],
        [False, False, False],
        [False, True, False],
    ],
    "=": [
        [False, False, False],
        [True, True, True],
        [False, False, False],
        [True, True, True],
        [False, False, False],
    ],
}
