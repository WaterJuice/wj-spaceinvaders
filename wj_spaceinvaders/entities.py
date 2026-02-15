# ----------------------------------------------------------------------------------------
#   entities.py
#   -----------
#
#   Game entity classes: Player, AlienFormation, Bullet, Shield, and MysteryShip.
#   Each entity knows how to update its state and draw itself to a pixel buffer.
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

import random
from . import sprites
from .display import PixelBuffer
from .sprites import SpriteData
from .sprites import sprite_size

# ----------------------------------------------------------------------------------------
#   Constants
# ----------------------------------------------------------------------------------------

# Formation layout: 3 rows × 8 columns (spacious, not a replica)
FORMATION_ROWS = 3
FORMATION_COLS = 8

# Spacing between aliens in the formation (pixels)
# Aliens are 6×5, spacing 9×8 gives 3px horizontal and 3px vertical gap
# Formation width: 7×9 + 6 = 69px (fits in 80 columns with margins)
# Formation height: 2×8 + 5 = 21px
ALIEN_SPACING_X = 9
ALIEN_SPACING_Y = 8

# Player movement speed (pixels per frame)
PLAYER_SPEED = 3

# Bullet speeds (pixels per frame)
PLAYER_BULLET_SPEED = 4
ALIEN_BULLET_SPEED = 2

# Alien shooting probability per frame (adjusted per remaining alien count)
ALIEN_SHOOT_BASE_CHANCE = 0.0015

# Mystery ship speed
MYSTERY_SPEED = 1

# Explosion duration in frames
EXPLOSION_FRAMES = 10

# Points per alien type
ALIEN_POINTS: dict[int, int] = {
    1: 30,  # Squid (top row)
    2: 20,  # Crab (middle rows)
    3: 10,  # Octopus (bottom rows)
}

# Mystery ship points (randomly chosen)
MYSTERY_POINTS: list[int] = [50, 100, 150, 200, 300]

# ----------------------------------------------------------------------------------------
#   Alien Type Sprites
# ----------------------------------------------------------------------------------------

# Sprites indexed by (alien_type, animation_frame)
ALIEN_SPRITES: dict[tuple[int, int], SpriteData] = {
    (1, 0): sprites.ALIEN1_A,
    (1, 1): sprites.ALIEN1_B,
    (2, 0): sprites.ALIEN2_A,
    (2, 1): sprites.ALIEN2_B,
    (3, 0): sprites.ALIEN3_A,
    (3, 1): sprites.ALIEN3_B,
}

# Which rows use which alien type (row 0 = top)
ROW_ALIEN_TYPE: dict[int, int] = {
    0: 1,  # Top row: violet
    1: 2,  # Middle row: amber
    2: 3,  # Bottom row: teal
}

# ----------------------------------------------------------------------------------------
#   Player
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class Player:
    """The player's ship at the bottom of the screen."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.width, self.height = sprite_size(sprites.PLAYER)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width // 2 - self.width // 2
        # Position player near bottom, leaving 1px for ground line
        self.y = screen_height - self.height - 1
        self.lives = 3
        self.alive = True
        self.respawn_timer = 0

    # ------------------------------------------------------------------------------------
    def move_left(self) -> None:
        """Move player left."""
        self.x = max(0, self.x - PLAYER_SPEED)

    # ------------------------------------------------------------------------------------
    def move_right(self) -> None:
        """Move player right."""
        self.x = min(self.screen_width - self.width, self.x + PLAYER_SPEED)

    # ------------------------------------------------------------------------------------
    def fire(self) -> Bullet | None:
        """
        Create a bullet if the player is alive.

        Returns:
            New Bullet, or None if player can't fire.
        """
        if not self.alive:
            return None
        bx = self.x + self.width // 2
        by = self.y - 3
        return Bullet(bx, by, -PLAYER_BULLET_SPEED, is_player=True)

    # ------------------------------------------------------------------------------------
    def hit(self) -> None:
        """Handle player being hit."""
        self.lives -= 1
        self.alive = False
        self.respawn_timer = 60  # ~2 seconds at 30fps

    # ------------------------------------------------------------------------------------
    def update(self) -> None:
        """Update respawn timer."""
        if not self.alive and self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0 and self.lives > 0:
                self.alive = True
                self.x = self.screen_width // 2 - self.width // 2

    # ------------------------------------------------------------------------------------
    def draw(self, buf: PixelBuffer) -> None:
        """Draw the player ship."""
        if self.alive:
            buf.draw_sprite(self.x, self.y, sprites.PLAYER)


# ----------------------------------------------------------------------------------------
#   Bullet
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class Bullet:
    """A bullet fired by either the player or an alien."""

    def __init__(self, x: int, y: int, dy: int, *, is_player: bool) -> None:
        self.x = x
        self.y = y
        self.dy = dy
        self.is_player = is_player
        self.active = True
        self.sprite = sprites.BULLET_PLAYER if is_player else sprites.BULLET_ALIEN
        self.width, self.height = sprite_size(self.sprite)

    # ------------------------------------------------------------------------------------
    def update(self, screen_height: int) -> None:
        """Move the bullet. Deactivate if off-screen."""
        self.y += self.dy
        if self.y < -self.height or self.y > screen_height:
            self.active = False

    # ------------------------------------------------------------------------------------
    def draw(self, buf: PixelBuffer) -> None:
        """Draw the bullet."""
        if self.active:
            buf.draw_sprite(self.x, self.y, self.sprite)


# ----------------------------------------------------------------------------------------
#   Explosion
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class Explosion:
    """A brief explosion animation."""

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.timer = EXPLOSION_FRAMES
        self.active = True

    # ------------------------------------------------------------------------------------
    def update(self) -> None:
        """Advance the explosion animation."""
        self.timer -= 1
        if self.timer <= 0:
            self.active = False

    # ------------------------------------------------------------------------------------
    def draw(self, buf: PixelBuffer) -> None:
        """Draw the explosion."""
        if self.active:
            sprite = (
                sprites.EXPLOSION_1
                if self.timer > EXPLOSION_FRAMES // 2
                else sprites.EXPLOSION_2
            )
            buf.draw_sprite(self.x, self.y, sprite)


# ----------------------------------------------------------------------------------------
#   Alien Formation
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class AlienFormation:
    """
    Grid of aliens that moves as a unit.

    The formation moves right until the rightmost alien hits the edge,
    then drops down and reverses direction.
    """

    def __init__(self, screen_width: int, start_y: int = 20) -> None:
        self.screen_width = screen_width
        self.anim_frame = 0
        self.move_timer = 0
        self.move_interval = 30  # Frames between moves (decreases as aliens die)
        self.direction = 1  # 1 = right, -1 = left
        self.move_amount = 2  # Pixels per step

        # Build the grid: each cell is (alien_type, alive)
        self.grid: list[list[tuple[int, bool]]] = []
        for row in range(FORMATION_ROWS):
            alien_type = ROW_ALIEN_TYPE[row]
            self.grid.append([(alien_type, True) for _ in range(FORMATION_COLS)])

        # Calculate starting position to centre the formation
        self._widths = self._calc_row_widths()
        max_width = max(self._widths)
        self.x = (screen_width - max_width) // 2
        self.y = start_y

    # ------------------------------------------------------------------------------------
    def _calc_row_widths(self) -> list[int]:
        """Calculate pixel width of each row based on alien type."""
        widths: list[int] = []
        for row in range(FORMATION_ROWS):
            alien_type = ROW_ALIEN_TYPE[row]
            sw, _ = sprite_size(ALIEN_SPRITES[(alien_type, 0)])
            widths.append(FORMATION_COLS * ALIEN_SPACING_X - (ALIEN_SPACING_X - sw))
        return widths

    # ------------------------------------------------------------------------------------
    def alive_count(self) -> int:
        """Count remaining alive aliens."""
        return sum(1 for row in self.grid for _, alive in row if alive)

    # ------------------------------------------------------------------------------------
    def _leftmost_col(self) -> int:
        """Find the leftmost column with a living alien."""
        for col in range(FORMATION_COLS):
            for row in range(FORMATION_ROWS):
                if self.grid[row][col][1]:
                    return col
        return 0

    # ------------------------------------------------------------------------------------
    def _rightmost_col(self) -> int:
        """Find the rightmost column with a living alien."""
        for col in range(FORMATION_COLS - 1, -1, -1):
            for row in range(FORMATION_ROWS):
                if self.grid[row][col][1]:
                    return col
        return FORMATION_COLS - 1

    # ------------------------------------------------------------------------------------
    def _lowest_row(self) -> int:
        """Find the lowest row with a living alien."""
        for row in range(FORMATION_ROWS - 1, -1, -1):
            for col in range(FORMATION_COLS):
                if self.grid[row][col][1]:
                    return row
        return 0

    # ------------------------------------------------------------------------------------
    def update(self) -> None:
        """Update formation movement."""
        alive = self.alive_count()
        if alive == 0:
            return

        # Speed up as aliens die (24 total aliens in 3×8 formation)
        self.move_interval = max(3, 30 - (24 - alive))

        self.move_timer += 1
        if self.move_timer < self.move_interval:
            return
        self.move_timer = 0

        # Toggle animation frame
        self.anim_frame = 1 - self.anim_frame

        # Try to move horizontally
        new_x = self.x + self.direction * self.move_amount

        # Check bounds
        left_col = self._leftmost_col()
        right_col = self._rightmost_col()
        left_edge = new_x + left_col * ALIEN_SPACING_X
        right_col_type = self.grid[0][right_col][0]  # Any alive row will do for width
        for row in range(FORMATION_ROWS):
            if self.grid[row][right_col][1]:
                right_col_type = self.grid[row][right_col][0]
                break
        sw, _ = sprite_size(ALIEN_SPRITES[(right_col_type, 0)])
        right_edge = new_x + right_col * ALIEN_SPACING_X + sw

        if left_edge < 0 or right_edge > self.screen_width:
            # Hit edge — drop down and reverse
            self.y += 2
            self.direction = -self.direction
        else:
            self.x = new_x

    # ------------------------------------------------------------------------------------
    def try_shoot(self) -> Bullet | None:
        """
        Randomly fire a bullet from one of the lowest alive aliens in each column.

        Returns:
            New Bullet, or None if no shot fired.
        """
        if random.random() > ALIEN_SHOOT_BASE_CHANCE * self.alive_count():
            return None

        # Pick a random column that has living aliens
        active_cols: list[int] = []
        for col in range(FORMATION_COLS):
            for row in range(FORMATION_ROWS - 1, -1, -1):
                if self.grid[row][col][1]:
                    active_cols.append(col)
                    break

        if not active_cols:
            return None

        col = random.choice(active_cols)

        # Find the lowest alive alien in this column
        for row in range(FORMATION_ROWS - 1, -1, -1):
            alien_type, alive = self.grid[row][col]
            if alive:
                sw, sh = sprite_size(ALIEN_SPRITES[(alien_type, 0)])
                ax = self.x + col * ALIEN_SPACING_X + sw // 2
                ay = self.y + row * ALIEN_SPACING_Y + sh
                return Bullet(ax, ay, ALIEN_BULLET_SPEED, is_player=False)

        return None

    # ------------------------------------------------------------------------------------
    def get_alien_rect(self, row: int, col: int) -> tuple[int, int, int, int]:
        """Get the bounding box (x, y, w, h) of an alien in the formation."""
        alien_type = self.grid[row][col][0]
        sw, sh = sprite_size(ALIEN_SPRITES[(alien_type, 0)])
        ax = self.x + col * ALIEN_SPACING_X
        ay = self.y + row * ALIEN_SPACING_Y
        return (ax, ay, sw, sh)

    # ------------------------------------------------------------------------------------
    def reached_bottom(self, player_y: int) -> bool:
        """Check if any alive alien has reached the player's level."""
        lowest_row = self._lowest_row()
        alien_type = ROW_ALIEN_TYPE[lowest_row]
        _, sh = sprite_size(ALIEN_SPRITES[(alien_type, 0)])
        bottom = self.y + lowest_row * ALIEN_SPACING_Y + sh
        return bottom >= player_y

    # ------------------------------------------------------------------------------------
    def draw(self, buf: PixelBuffer) -> None:
        """Draw all alive aliens."""
        for row in range(FORMATION_ROWS):
            for col in range(FORMATION_COLS):
                alien_type, alive = self.grid[row][col]
                if alive:
                    sprite = ALIEN_SPRITES[(alien_type, self.anim_frame)]
                    ax = self.x + col * ALIEN_SPACING_X
                    ay = self.y + row * ALIEN_SPACING_Y
                    buf.draw_sprite(ax, ay, sprite)


# ----------------------------------------------------------------------------------------
#   Shield
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class Shield:
    """A destructible barrier. Individual pixels are removed on bullet impact."""

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        # Copy the shield sprite so we can modify it
        self.pixels: SpriteData = [row[:] for row in sprites.SHIELD]
        self.width, self.height = sprite_size(sprites.SHIELD)

    # ------------------------------------------------------------------------------------
    def damage(self, bx: int, by: int, radius: int = 2) -> bool:
        """
        Apply damage at a point, destroying pixels within the given radius.

        Returns:
            True if any pixels were destroyed.
        """
        hit = False
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    px = bx - self.x + dx
                    py = by - self.y + dy
                    if 0 <= px < self.width and 0 <= py < self.height:
                        if self.pixels[py][px] is not None:
                            self.pixels[py][px] = None
                            hit = True
        return hit

    # ------------------------------------------------------------------------------------
    def has_pixel_at(self, x: int, y: int) -> bool:
        """Check if a solid pixel exists at the given world coordinates."""
        px = x - self.x
        py = y - self.y
        if 0 <= px < self.width and 0 <= py < self.height:
            return self.pixels[py][px] is not None
        return False

    # ------------------------------------------------------------------------------------
    def draw(self, buf: PixelBuffer) -> None:
        """Draw the shield."""
        buf.draw_sprite(self.x, self.y, self.pixels)


# ----------------------------------------------------------------------------------------
#   Mystery Ship
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
class MysteryShip:
    """The bonus mystery ship that flies across the top of the screen."""

    def __init__(self, screen_width: int) -> None:
        self.screen_width = screen_width
        self.width, self.height = sprite_size(sprites.MYSTERY)
        self.active = False
        self.x = 0
        self.y = 1
        self.direction = 1
        self.spawn_timer = 0
        self.spawn_interval = random.randint(400, 800)
        self.points = 0

    # ------------------------------------------------------------------------------------
    def update(self) -> None:
        """Update mystery ship position or spawn timer."""
        if self.active:
            self.x += MYSTERY_SPEED * self.direction
            if self.x < -self.width or self.x > self.screen_width:
                self.active = False
        else:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval:
                self._spawn()

    # ------------------------------------------------------------------------------------
    def _spawn(self) -> None:
        """Spawn the mystery ship."""
        self.active = True
        self.spawn_timer = 0
        self.spawn_interval = random.randint(400, 800)
        self.points = random.choice(MYSTERY_POINTS)
        self.direction = random.choice([-1, 1])
        if self.direction == 1:
            self.x = -self.width
        else:
            self.x = self.screen_width

    # ------------------------------------------------------------------------------------
    def draw(self, buf: PixelBuffer) -> None:
        """Draw the mystery ship."""
        if self.active:
            buf.draw_sprite(self.x, self.y, sprites.MYSTERY)


# ----------------------------------------------------------------------------------------
#   Collision Detection
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def check_bullet_alien(
    bullet: Bullet,
    formation: AlienFormation,
) -> tuple[int, int, int] | None:
    """
    Check if a player bullet hit an alien.

    Returns:
        Tuple of (row, col, points) if hit, None otherwise.
    """
    if not bullet.is_player or not bullet.active:
        return None

    for row in range(FORMATION_ROWS):
        for col in range(FORMATION_COLS):
            alien_type, alive = formation.grid[row][col]
            if not alive:
                continue

            ax, ay, aw, ah = formation.get_alien_rect(row, col)
            bw, bh = sprite_size(bullet.sprite)

            if _rects_overlap(bullet.x, bullet.y, bw, bh, ax, ay, aw, ah):
                return (row, col, ALIEN_POINTS[alien_type])

    return None


# ----------------------------------------------------------------------------------------
def check_bullet_player(bullet: Bullet, player: Player) -> bool:
    """Check if an alien bullet hit the player."""
    if bullet.is_player or not bullet.active or not player.alive:
        return False

    bw, bh = sprite_size(bullet.sprite)
    return _rects_overlap(
        bullet.x,
        bullet.y,
        bw,
        bh,
        player.x,
        player.y,
        player.width,
        player.height,
    )


# ----------------------------------------------------------------------------------------
def check_bullet_shield(bullet: Bullet, shield: Shield) -> bool:
    """Check if a bullet hit a shield, applying damage if so."""
    bw, bh = sprite_size(bullet.sprite)

    # Quick bounding box check
    if not _rects_overlap(
        bullet.x,
        bullet.y,
        bw,
        bh,
        shield.x,
        shield.y,
        shield.width,
        shield.height,
    ):
        return False

    # Check if any bullet pixel overlaps a shield pixel
    for by in range(bullet.y, bullet.y + bh):
        for bx_off in range(bw):
            if shield.has_pixel_at(bullet.x + bx_off, by):
                shield.damage(bullet.x + bx_off, by)
                return True

    return False


# ----------------------------------------------------------------------------------------
def check_bullet_mystery(bullet: Bullet, mystery: MysteryShip) -> bool:
    """Check if a player bullet hit the mystery ship."""
    if not bullet.is_player or not bullet.active or not mystery.active:
        return False

    bw, bh = sprite_size(bullet.sprite)
    return _rects_overlap(
        bullet.x,
        bullet.y,
        bw,
        bh,
        mystery.x,
        mystery.y,
        mystery.width,
        mystery.height,
    )


# ----------------------------------------------------------------------------------------
#   Internal Helpers
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
def _rects_overlap(
    x1: int,
    y1: int,
    w1: int,
    h1: int,
    x2: int,
    y2: int,
    w2: int,
    h2: int,
) -> bool:
    """Check if two rectangles overlap."""
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


# ----------------------------------------------------------------------------------------
def create_shields(screen_width: int, player_y: int) -> list[Shield]:
    """
    Create 3 shields positioned above the player with generous spacing.

    Returns:
        List of 3 Shield objects.
    """
    shield_w, shield_h = sprite_size(sprites.SHIELD)
    shield_y = player_y - shield_h - 2
    gap = 12
    total_width = 3 * shield_w + 2 * gap
    start_x = (screen_width - total_width) // 2

    shield_list: list[Shield] = []
    for i in range(3):
        sx = start_x + i * (shield_w + gap)
        shield_list.append(Shield(sx, shield_y))
    return shield_list


# ----------------------------------------------------------------------------------------
def draw_score_and_lives(
    buf: PixelBuffer,
    score: int,
    lives: int,
    high_score: int,
    level: int,
) -> None:
    """Draw the score, high score, lives, and level at the top and bottom of the screen."""
    # Layout for 80 columns: score left, HI centre, LV right
    # Each font char is 4px wide (3px glyph + 1px space)
    buf.draw_text(1, 0, f"{score:05d}", sprites.SCORE_COLOUR)
    hi_text = f"HI {high_score:05d}"
    buf.draw_text(buf.width // 2 - len(hi_text) * 2, 0, hi_text, sprites.SCORE_COLOUR)
    lv_text = f"LV{level}"
    buf.draw_text(buf.width - len(lv_text) * 4 - 1, 0, lv_text, sprites.SCORE_COLOUR)

    # Draw lives as small player ships at bottom-left
    lives_x = 2
    lives_y = buf.height - 4
    for i in range(lives - 1):
        buf.draw_sprite(lives_x + i * 7, lives_y, sprites.PLAYER_SMALL)

    # Ground line
    buf.fill_rect(0, buf.height - 1, buf.width, 1, sprites.GROUND_COLOUR)
