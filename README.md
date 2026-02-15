# wj-spaceinvaders

Classic Space Invaders game for the terminal, rendered using ANSI 24-bit colour and Unicode half-block characters for full-colour pixel graphics.

**Python 3.14+ | stdlib only | No dependencies**

## Installation

```bash
uv sync
```

## Usage

```bash
# Run via entry point
uv run wj-spaceinvaders

# Or via module
uv run python -m wj_spaceinvaders

# Show version
uv run wj-spaceinvaders --version
```

## Controls

| Key          | Action     |
|--------------|------------|
| Left / Right | Move ship  |
| Space        | Fire       |
| P            | Pause      |
| Q / Escape   | Quit       |

## Scoring

| Alien      | Points |
|------------|--------|
| Squid      | 30     |
| Crab       | 20     |
| Octopus    | 10     |
| Mystery    | ?????  |

## Requirements

- Python 3.14+
- A terminal supporting ANSI 24-bit colour and Unicode
- Minimum terminal size: 80×30

## Development

```bash
make dev          # Set up development environment
make check        # Format check + lint
make format       # Auto-format code
make lint         # Run pyright type checker
make build        # Build wheel
```

## Licence

Unlicense — public domain. See LICENSE.
