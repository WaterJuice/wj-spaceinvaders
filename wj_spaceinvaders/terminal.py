# ----------------------------------------------------------------------------------------
#   terminal.py
#   -----------
#
#   Raw terminal mode handling for game input and screen control. Uses termios/tty
#   for raw mode and select for non-blocking keyboard reads. Manages alternate
#   screen buffer and cursor visibility.
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

import os
import select
import sys
import termios
import tty
from enum import Enum
from enum import auto
from types import TracebackType

# ----------------------------------------------------------------------------------------
#   Constants
# ----------------------------------------------------------------------------------------

# ANSI escape sequences
ESC = "\033"
CSI = f"{ESC}["
ALT_SCREEN_ON = f"{CSI}?1049h"
ALT_SCREEN_OFF = f"{CSI}?1049l"
CURSOR_HIDE = f"{CSI}?25l"
CURSOR_SHOW = f"{CSI}?25h"
CURSOR_HOME = f"{CSI}H"
CLEAR_SCREEN = f"{CSI}2J"

# OSC sequences to set/reset the terminal's native background colour.
# This affects the actual window background (including inter-row gaps),
# not just the ANSI cell background.
BG_BLACK = f"{ESC}]11;rgb:00/00/00\007"
BG_RESET = f"{ESC}]111\007"

# ----------------------------------------------------------------------------------------
#   Types
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class Key(Enum):
    """Keyboard input events."""

    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()
    SPACE = auto()
    ESCAPE = auto()
    ENTER = auto()
    QUIT = auto()
    PAUSE = auto()
    UNKNOWN = auto()


# ----------------------------------------------------------------------------------------
#   Terminal Context Manager
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class Terminal:
    """
    Manages raw terminal mode for game input and rendering.

    Usage as context manager:
        with Terminal() as term:
            key = term.read_key()
            cols, rows = term.get_size()
    """

    def __init__(self) -> None:
        self._old_settings: list[int | list[bytes | int]] = []
        self._fd: int = sys.stdin.fileno()

    # ------------------------------------------------------------------------------------
    def __enter__(self) -> Terminal:
        # Save current terminal settings
        self._old_settings = termios.tcgetattr(self._fd)  # pyright: ignore[reportUnknownMemberType]

        # Enter raw mode
        tty.setraw(self._fd)

        # Switch to alternate screen buffer, hide cursor, set black background.
        # OSC 11 sets the terminal's native window background to pure black so
        # that any inter-row font gaps are invisible.
        sys.stdout.write(
            ALT_SCREEN_ON + BG_BLACK + CURSOR_HIDE + "\033[48;2;0;0;0m" + CLEAR_SCREEN
        )
        sys.stdout.flush()

        return self

    # ------------------------------------------------------------------------------------
    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        # Restore terminal settings
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)  # pyright: ignore[reportUnknownMemberType]

        # Restore terminal background, leave alternate screen buffer, show cursor
        sys.stdout.write(BG_RESET + CURSOR_SHOW + ALT_SCREEN_OFF)
        sys.stdout.flush()

    # ------------------------------------------------------------------------------------
    def read_key(self) -> Key | None:
        """
        Read a keypress without blocking.

        Returns:
            Key enum value, or None if no key was pressed.
        """
        if not _has_input(self._fd):
            return None

        ch = os.read(self._fd, 1)
        if not ch:
            return None

        # Escape sequence
        if ch == b"\x1b":
            if not _has_input(self._fd):
                return Key.ESCAPE
            ch2 = os.read(self._fd, 1)
            if ch2 == b"[":
                ch3 = os.read(self._fd, 1)
                if ch3 == b"A":
                    return Key.UP
                if ch3 == b"B":
                    return Key.DOWN
                if ch3 == b"C":
                    return Key.RIGHT
                if ch3 == b"D":
                    return Key.LEFT
            return Key.ESCAPE

        # Regular keys
        if ch == b" ":
            return Key.SPACE
        if ch in (b"q", b"Q"):
            return Key.QUIT
        if ch in (b"p", b"P"):
            return Key.PAUSE
        if ch in (b"\r", b"\n"):
            return Key.ENTER

        return Key.UNKNOWN

    # ------------------------------------------------------------------------------------
    def read_all_keys(self) -> list[Key]:
        """
        Read all pending keypresses without blocking.

        Returns:
            List of Key enum values. Empty list if no keys pressed.
        """
        keys: list[Key] = []
        while True:
            key = self.read_key()
            if key is None:
                break
            keys.append(key)
        return keys

    # ------------------------------------------------------------------------------------
    @staticmethod
    def get_size() -> tuple[int, int]:
        """
        Get terminal size in columns and rows.

        Returns:
            Tuple of (columns, rows).
        """
        size = os.get_terminal_size()
        return size.columns, size.lines

    # ------------------------------------------------------------------------------------
    @staticmethod
    def write(text: str) -> None:
        """Write text to stdout and flush."""
        sys.stdout.write(text)
        sys.stdout.flush()

    # ------------------------------------------------------------------------------------
    @staticmethod
    def cursor_home() -> str:
        """Return ANSI sequence to move cursor to top-left."""
        return CURSOR_HOME


# ----------------------------------------------------------------------------------------
#   Internal Functions
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def _has_input(fd: int) -> bool:
    """Check if there is input available on the file descriptor."""
    readable, _, _ = select.select([fd], [], [], 0)
    return len(readable) > 0
