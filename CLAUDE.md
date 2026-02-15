# CLAUDE.md

This file provides guidance for AI agents working on this project.

## Project Overview

wj-spaceinvaders is a terminal-based Space Invaders game rendered with ANSI 24-bit colour and Unicode half-block characters. It uses only Python stdlib — no external dependencies.

## Language and Spelling

Use **Australian English** throughout:
- colour (not color)
- initialise (not initialize)
- sanitise (not sanitize)
- organisation (not organization)

## Code Style

### Python Files

Every Python file should have:
1. A file header block with description and version history
2. Section headers separating major sections (Imports, Constants, Functions, etc.)
3. Horizontal separators (96 chars) above each function definition

Example structure:
```python
# ----------------------------------------------------------------------------------------
#   filename.py
#   -----------
#
#   Brief description of what this module does.
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

import sys

# ----------------------------------------------------------------------------------------
#   Functions
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def my_function() -> None:
    """Docstring here."""
    pass
```

### General

- Python 3.14+ (no `from __future__ import annotations` needed)
- Use type hints throughout
- Prefer pathlib.Path over os.path
- Single-line imports, no blank lines between import groups (configured in pyproject.toml)
- Run `make format` to auto-fix import ordering

## Common Commands

```bash
make help       # Show all available targets
make check      # Run ruff + pyright
make format     # Auto-fix and format code
make build      # Build wheel into output/
make publish    # Publish output/ to PyPI
make clean      # Remove build artefacts
make dev        # Just create dev (.venv) setup
```

## Project Structure

```
wj-spaceinvaders/
├── wj_spaceinvaders/          # Main package
│   ├── __init__.py          # Package init, exports __version__
│   ├── __main__.py          # Entry point for python -m wj_spaceinvaders
│   ├── cli.py               # CLI argument parsing and entry
│   ├── version.py           # Version string handling
│   ├── terminal.py          # Raw terminal mode, input handling
│   ├── display.py           # Pixel buffer and half-block renderer
│   ├── sprites.py           # Pixel art sprite definitions
│   ├── entities.py          # Game entities (player, aliens, bullets, shields)
│   └── game.py              # Main game loop and state management
├── Makefile                  # Build automation
└── pyproject.toml            # Project metadata and dependencies
```

## Architecture

### Display System (`display.py`)
- `PixelBuffer` stores a 2D grid of RGB pixels
- Terminal columns = pixel width, terminal rows × 2 = pixel height
- Each character cell renders 2 vertical pixels using ▀ with fg/bg colours
- Uses ANSI 24-bit colour: `\033[38;2;R;G;Bm` (fg) + `\033[48;2;R;G;Bm` (bg)

### Terminal Handling (`terminal.py`)
- Raw mode via `termios` + `tty`
- Non-blocking key reads via `select.select()`
- Alternate screen buffer and cursor hiding

### Game Loop (`game.py`)
- State machine: TITLE → PLAYING → PAUSED / GAME_OVER
- Fixed 30 FPS timestep
- Per frame: input → update → collisions → render

## Testing Changes

After making changes:
1. Run `make check` to verify linting and types pass
2. Run `make build` to verify the full build works
3. Test with `uv run wj-spaceinvaders` to verify the game works

## Versioning

- Version is derived from git tags via Makefile
- Create a tag like `1.0.0` before running `make build` for a release (no `v` prefix)
- The Makefile generates `_version.py` at build time, which is not committed
- If no tags exist, version falls back to commit-based format

## Commits

When committing:
- Use clear, descriptive commit messages
- Include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` in commits made with AI assistance
- **Never rewrite git history** unless explicitly asked to

## Licence

Unlicense — public domain. See LICENSE.
