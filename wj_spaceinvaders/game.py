# ----------------------------------------------------------------------------------------
#   game.py
#   -------
#
#   Main game loop and state management. Handles the title screen, gameplay,
#   pause, and game over states. Coordinates entity updates, collision detection,
#   and rendering.
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

import time
from enum import Enum
from enum import auto
from . import sprites
from .display import Colour
from .display import PixelBuffer
from .entities import AlienFormation
from .entities import Bullet
from .entities import Explosion
from .entities import MysteryShip
from .entities import Player
from .entities import Shield
from .entities import check_bullet_alien
from .entities import check_bullet_mystery
from .entities import check_bullet_player
from .entities import check_bullet_shield
from .entities import create_shields
from .entities import draw_score_and_lives
from .terminal import Key
from .terminal import Terminal

# ----------------------------------------------------------------------------------------
#   Constants
# ----------------------------------------------------------------------------------------

TARGET_FPS = 30
FRAME_TIME = 1.0 / TARGET_FPS

# Minimum terminal size required
MIN_COLS = 80
MIN_ROWS = 24

# Colours for title/UI text
TITLE_COLOUR: Colour = (255, 255, 255)
TITLE_ACCENT: Colour = (0, 255, 0)
GAMEOVER_COLOUR: Colour = (255, 60, 60)
PAUSE_COLOUR: Colour = (255, 255, 0)

# Maximum bullets on screen at once
MAX_PLAYER_BULLETS = 2
MAX_ALIEN_BULLETS = 5

# ----------------------------------------------------------------------------------------
#   Game State
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class State(Enum):
    """Game state machine states."""

    TITLE = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


# ----------------------------------------------------------------------------------------
#   Game
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class Game:
    """Main game class that owns all state and runs the game loop."""

    def __init__(self) -> None:
        self.state = State.TITLE
        self.score = 0
        self.high_score = 0
        self.level = 1

        # These are initialised when entering PLAYING state
        self.screen_width = 0
        self.screen_height = 0
        self.player: Player | None = None
        self.formation: AlienFormation | None = None
        self.shields: list[Shield] = []
        self.mystery: MysteryShip | None = None
        self.player_bullets: list[Bullet] = []
        self.alien_bullets: list[Bullet] = []
        self.explosions: list[Explosion] = []

        # Title screen animation
        self._title_blink_timer = 0

    # ------------------------------------------------------------------------------------
    def run(self) -> None:
        """Run the game. Blocks until the player quits."""
        with Terminal() as term:
            cols, rows = term.get_size()

            if cols < MIN_COLS or rows < MIN_ROWS:
                term.write(
                    "\033[H\033[2J"
                    f"Terminal too small! Need at least {MIN_COLS}x{MIN_ROWS}, "
                    f"got {cols}x{rows}.\r\n"
                    "Press any key to exit.\r\n"
                )
                while not term.read_key():
                    time.sleep(0.05)
                return

            self.screen_width = min(cols, MIN_COLS)
            self.screen_height = min(rows, MIN_ROWS) * 2

            buf = PixelBuffer(self.screen_width, self.screen_height, cols, rows)

            running = True
            while running:
                frame_start = time.monotonic()

                # Process input
                keys = term.read_all_keys()
                for key in keys:
                    if key == Key.QUIT:
                        running = False
                        break
                    self._handle_key(key)

                if not running:
                    break

                # Update
                self._update()

                # Render
                buf.clear()
                self._draw(buf)
                term.write(buf.render())

                # Frame timing
                elapsed = time.monotonic() - frame_start
                sleep_time = FRAME_TIME - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

    # ------------------------------------------------------------------------------------
    def _handle_key(self, key: Key) -> None:
        """Route a keypress to the appropriate state handler."""
        if self.state == State.TITLE:
            if key in (Key.SPACE, Key.ENTER):
                self._start_game()
        elif self.state == State.PLAYING:
            self._handle_playing_key(key)
        elif self.state == State.PAUSED:
            if key == Key.PAUSE:
                self.state = State.PLAYING
            elif key == Key.ESCAPE:
                self.state = State.TITLE
        elif self.state == State.GAME_OVER:
            if key in (Key.SPACE, Key.ENTER):
                self.state = State.TITLE

    # ------------------------------------------------------------------------------------
    def _handle_playing_key(self, key: Key) -> None:
        """Handle input during gameplay."""
        if key == Key.LEFT and self.player:
            self.player.move_left()
        elif key == Key.RIGHT and self.player:
            self.player.move_right()
        elif key == Key.SPACE and self.player:
            player_bullet_count = len([b for b in self.player_bullets if b.active])
            if player_bullet_count < MAX_PLAYER_BULLETS:
                bullet = self.player.fire()
                if bullet:
                    self.player_bullets.append(bullet)
        elif key == Key.PAUSE:
            self.state = State.PAUSED
        elif key == Key.ESCAPE:
            self.state = State.TITLE

    # ------------------------------------------------------------------------------------
    def _start_game(self) -> None:
        """Initialise a new game."""
        self.state = State.PLAYING
        self.score = 0
        self.level = 1
        self._init_level()

    # ------------------------------------------------------------------------------------
    def _init_level(self) -> None:
        """Initialise entities for the current level."""
        self.player = Player(self.screen_width, self.screen_height)
        # Formation starts just below score bar (y=0-4) and mystery zone
        start_y = min(7 + (self.level - 1) * 2, self.screen_height // 3)
        self.formation = AlienFormation(self.screen_width, start_y)
        self.shields = create_shields(self.screen_width, self.player.y)
        self.mystery = MysteryShip(self.screen_width)
        self.player_bullets = []
        self.alien_bullets = []
        self.explosions = []

    # ------------------------------------------------------------------------------------
    def _update(self) -> None:
        """Update game state for one frame."""
        if self.state in (State.TITLE, State.GAME_OVER):
            self._title_blink_timer = (self._title_blink_timer + 1) % 60
        elif self.state == State.PLAYING:
            self._update_playing()

    # ------------------------------------------------------------------------------------
    def _update_playing(self) -> None:
        """Update all entities during gameplay."""
        assert self.player is not None
        assert self.formation is not None
        assert self.mystery is not None

        # Update player
        self.player.update()

        # Update formation
        self.formation.update()

        # Update mystery ship
        self.mystery.update()

        # Update bullets
        for bullet in self.player_bullets:
            bullet.update(self.screen_height)
        for bullet in self.alien_bullets:
            bullet.update(self.screen_height)

        # Update explosions
        for explosion in self.explosions:
            explosion.update()

        # Alien shooting
        alien_bullet_count = len([b for b in self.alien_bullets if b.active])
        if alien_bullet_count < MAX_ALIEN_BULLETS:
            new_bullet = self.formation.try_shoot()
            if new_bullet:
                self.alien_bullets.append(new_bullet)

        # Collision detection
        self._check_collisions()

        # Clean up inactive entities
        self.player_bullets = [b for b in self.player_bullets if b.active]
        self.alien_bullets = [b for b in self.alien_bullets if b.active]
        self.explosions = [e for e in self.explosions if e.active]

        # Check win condition — all aliens destroyed
        if self.formation.alive_count() == 0:
            self.level += 1
            self._init_level()
            # Keep current score and lives
            assert self.player is not None
            return

        # Check lose condition — aliens reached player
        if self.formation.reached_bottom(self.player.y):
            self._game_over()

    # ------------------------------------------------------------------------------------
    def _check_collisions(self) -> None:
        """Check all bullet collisions."""
        assert self.player is not None
        assert self.formation is not None
        assert self.mystery is not None

        # Player bullets vs aliens
        for bullet in self.player_bullets:
            if not bullet.active:
                continue
            hit = check_bullet_alien(bullet, self.formation)
            if hit:
                row, col, points = hit
                self.formation.grid[row][col] = (
                    self.formation.grid[row][col][0],
                    False,
                )
                ax, ay, _, _ = self.formation.get_alien_rect(row, col)
                self.explosions.append(Explosion(ax, ay))
                bullet.active = False
                self.score += points

        # Player bullets vs mystery ship
        for bullet in self.player_bullets:
            if not bullet.active:
                continue
            if check_bullet_mystery(bullet, self.mystery):
                self.explosions.append(Explosion(self.mystery.x, self.mystery.y))
                self.score += self.mystery.points
                bullet.active = False
                self.mystery.active = False

        # Player bullets vs shields
        for bullet in self.player_bullets:
            if not bullet.active:
                continue
            for shield in self.shields:
                if check_bullet_shield(bullet, shield):
                    bullet.active = False
                    break

        # Alien bullets vs player
        for bullet in self.alien_bullets:
            if not bullet.active:
                continue
            if check_bullet_player(bullet, self.player):
                self.explosions.append(Explosion(self.player.x, self.player.y))
                bullet.active = False
                self.player.hit()
                if self.player.lives <= 0:
                    self._game_over()
                    return

        # Alien bullets vs shields
        for bullet in self.alien_bullets:
            if not bullet.active:
                continue
            for shield in self.shields:
                if check_bullet_shield(bullet, shield):
                    bullet.active = False
                    break

    # ------------------------------------------------------------------------------------
    def _game_over(self) -> None:
        """Transition to game over state."""
        self.state = State.GAME_OVER
        if self.score > self.high_score:
            self.high_score = self.score

    # ------------------------------------------------------------------------------------
    def _draw(self, buf: PixelBuffer) -> None:
        """Draw the current frame based on game state."""
        if self.state == State.TITLE:
            self._draw_title(buf)
        elif self.state == State.PLAYING:
            self._draw_playing(buf)
        elif self.state == State.PAUSED:
            self._draw_playing(buf)
            self._draw_pause_overlay(buf)
        elif self.state == State.GAME_OVER:
            self._draw_playing(buf)
            self._draw_game_over_overlay(buf)

    # ------------------------------------------------------------------------------------
    def _draw_title(self, buf: PixelBuffer) -> None:
        """Draw the title screen."""
        cx = buf.width // 2

        # Title text
        title = "SPACE INVADERS"
        title_x = cx - len(title) * 4 // 2
        buf.draw_text(title_x, 3, title, TITLE_COLOUR)

        # Show alien types and point values
        y = 12
        # Type 1
        buf.draw_sprite(cx - 20, y, sprites.ALIEN1_A)
        buf.draw_text(cx - 10, y, "= 30", TITLE_ACCENT)
        y += 7
        # Type 2
        buf.draw_sprite(cx - 20, y, sprites.ALIEN2_A)
        buf.draw_text(cx - 10, y, "= 20", TITLE_ACCENT)
        y += 7
        # Type 3
        buf.draw_sprite(cx - 20, y, sprites.ALIEN3_A)
        buf.draw_text(cx - 10, y, "= 10", TITLE_ACCENT)
        y += 7
        # Mystery
        buf.draw_sprite(cx - 22, y, sprites.MYSTERY)
        buf.draw_text(cx - 10, y, "= ??", TITLE_ACCENT)

        # Blinking "press space" text
        if self._title_blink_timer < 40:
            press_text = "PRESS SPACE"
            press_x = cx - len(press_text) * 4 // 2
            buf.draw_text(press_x, buf.height - 7, press_text, TITLE_COLOUR)

    # ------------------------------------------------------------------------------------
    def _draw_playing(self, buf: PixelBuffer) -> None:
        """Draw the gameplay frame."""
        assert self.player is not None
        assert self.formation is not None
        assert self.mystery is not None

        # Score and lives
        draw_score_and_lives(
            buf, self.score, self.player.lives, self.high_score, self.level
        )

        # Mystery ship
        self.mystery.draw(buf)

        # Formation
        self.formation.draw(buf)

        # Shields
        for shield in self.shields:
            shield.draw(buf)

        # Player
        self.player.draw(buf)

        # Bullets
        for bullet in self.player_bullets:
            bullet.draw(buf)
        for bullet in self.alien_bullets:
            bullet.draw(buf)

        # Explosions
        for explosion in self.explosions:
            explosion.draw(buf)

    # ------------------------------------------------------------------------------------
    def _draw_pause_overlay(self, buf: PixelBuffer) -> None:
        """Draw the pause overlay."""
        cx = buf.width // 2
        cy = buf.height // 2
        text = "PAUSED"
        buf.draw_text(cx - len(text) * 4 // 2, cy - 3, text, PAUSE_COLOUR)

    # ------------------------------------------------------------------------------------
    def _draw_game_over_overlay(self, buf: PixelBuffer) -> None:
        """Draw the game over overlay."""
        cx = buf.width // 2
        cy = buf.height // 2

        text = "GAME OVER"
        buf.draw_text(cx - len(text) * 4 // 2, cy - 6, text, GAMEOVER_COLOUR)

        score_text = f"SCORE {self.score:05d}"
        buf.draw_text(cx - len(score_text) * 4 // 2, cy + 1, score_text, TITLE_COLOUR)

        if self._title_blink_timer < 40:
            press_text = "PRESS SPACE"
            buf.draw_text(
                cx - len(press_text) * 4 // 2, cy + 8, press_text, TITLE_COLOUR
            )
