# ----------------------------------------------------------------------------------------
#   cli.py
#   ------
#
#   CLI entry point for wj-spaceinvaders. Handles argument parsing and launches the game.
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

import argparse
import sys
import traceback
from .version import VERSION_STR

# ----------------------------------------------------------------------------------------
#   Main Entry Point
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for wj-spaceinvaders CLI.

    Parameters:
        argv: Command line arguments. If None, uses sys.argv[1:].

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        return _main_inner(argv)
    except KeyboardInterrupt:
        return 1
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0
    except BaseException as e:
        t = "-----------------------------------------------------------------------------\n"
        t += "UNHANDLED EXCEPTION OCCURRED!!\n"
        t += "\n"
        t += traceback.format_exc()
        t += "\n"
        t += f"EXCEPTION: {type(e)} {e}\n"
        t += "-----------------------------------------------------------------------------\n"
        t += "\n"
        print(t, file=sys.stderr)
        return 1


# ----------------------------------------------------------------------------------------
def _main_inner(argv: list[str]) -> int:
    """Inner main function."""
    parser = argparse.ArgumentParser(
        prog="wj-spaceinvaders",
        description=(
            "Classic Space Invaders for the terminal — ANSI colour and Unicode"
            " half-block graphics."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"wj-spaceinvaders {VERSION_STR}",
    )

    parser.parse_args(argv)

    # Launch the game
    from .game import Game

    game = Game()
    game.run()
    return 0
