# wj-spaceinvaders 1.0.1 - 30 May 2026

Moved to new GitHub location: https://github.com/WaterJuice/wj-spaceinvaders

# wj-spaceinvaders 1.0.0 - 15 Feb 2026

Initial release.

## Features

### Gameplay

- Classic Space Invaders arcade gameplay in the terminal
- Four alien types: Squid (30 pts), Crab (20 pts), Octopus (10 pts), and Mystery UFO
- Player ship with laser cannon
- Destructible shields that degrade on impact
- Aliens speed up as their numbers decrease
- Progressive difficulty across waves

### Display

- ANSI 24-bit colour rendering for full-colour pixel graphics
- Unicode half-block characters (▀) for double vertical resolution
- Smooth 30 FPS game loop

### Terminal

- Raw terminal mode with non-blocking input
- Alternate screen buffer and cursor hiding
- Automatic terminal size detection (minimum 80×30)

### Other

- Zero external dependencies — stdlib only
- Python 3.14+
- Runs via `wj-spaceinvaders` command or `python -m wj_spaceinvaders`
