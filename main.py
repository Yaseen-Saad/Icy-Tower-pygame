import pygame
import random
import sys

pygame.init()

# -----------------------------
# CONFIGURATION
# -----------------------------
WIDTH = 400
HEIGHT = 600
TITLE = "Icy Tower Clone (Enhanced)"
FPS = 60

# Player properties
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
PLAYER_COLOR = (255, 50, 50)
PLAYER_START_X = WIDTH // 2
PLAYER_START_Y = HEIGHT - PLAYER_HEIGHT - 50
PLAYER_JUMP_SPEED = 15
GRAVITY = 0.5
PLAYER_SPEED_X = 5

# Platform properties
PLATFORM_WIDTH = 70
PLATFORM_HEIGHT = 15
PLATFORM_COUNT = 6  # Number of platforms visible
PLATFORM_GAP_MIN = 50
PLATFORM_GAP_MAX = 120

# Colors
BACKGROUND_COLOR = (20, 20, 20)
PLATFORM_COLOR_STATIC = (0, 150, 255)
PLATFORM_COLOR_MOVING = (150, 255, 0)  # Different color for moving platforms

# Movement & difficulty
PLATFORM_MOVE_CHANCE = 0.3  # 30% chance a new platform will be moving
PLATFORM_MOVE_RANGE = 50    # How far (in px) a platform moves from its origin
PLATFORM_MOVE_SPEED = 2     # Speed at which the platform oscillates

# Game Window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Font for text
font = pygame.font.SysFont(None, 40)

# -----------------------------
# CLASSES
# -----------------------------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_y = 0  # Vertical velocity

    def update(self, platforms):
        """Update player position and handle collisions."""
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)

        # Horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED_X
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED_X

        # Optional wrap-around horizontally
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0

        # Collision with platforms (only when falling down)
        if self.vel_y > 0:
            for platform in platforms:
                if self.rect.colliderect(platform.rect) and \
                   (self.rect.bottom <= platform.rect.bottom):
                    # Land on the platform
                    self.rect.bottom = platform.rect.top
                    self.vel_y = -PLAYER_JUMP_SPEED

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)


class Platform:
    def __init__(self, x, y, width, height, is_moving=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_moving = is_moving
        self.color = PLATFORM_COLOR_STATIC if not is_moving else PLATFORM_COLOR_MOVING

        # For moving platforms
        if self.is_moving:
            self.initial_x = x
            self.move_dir = 1
            self.move_range = PLATFORM_MOVE_RANGE
            self.move_speed = PLATFORM_MOVE_SPEED

    def update(self):
        """Update platform position if it's a moving platform."""
        if self.is_moving:
            self.rect.x += self.move_dir * self.move_speed
            # If it goes beyond the range, switch direction
            if abs(self.rect.x - self.initial_x) >= self.move_range:
                self.move_dir *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def create_platforms():
    """Create an initial list of platforms at random positions."""
    platforms_list = []
    # Base platform (wider) at the bottom
    base_platform = Platform(
        x=WIDTH // 2 - PLATFORM_WIDTH,
        y=HEIGHT - 50,
        width=PLATFORM_WIDTH * 2,
        height=PLATFORM_HEIGHT,
        is_moving=False
    )
    platforms_list.append(base_platform)

    current_y = HEIGHT - 100
    while len(platforms_list) < PLATFORM_COUNT:
        x = random.randint(0, WIDTH - PLATFORM_WIDTH)
        gap = random.randint(PLATFORM_GAP_MIN, PLATFORM_GAP_MAX)
        current_y -= gap
        # Random chance the platform is moving
        is_moving = (random.random() < PLATFORM_MOVE_CHANCE)
        platforms_list.append(Platform(x, current_y, PLATFORM_WIDTH, PLATFORM_HEIGHT, is_moving))

    return platforms_list


# -----------------------------
# MAIN GAME LOOP
# -----------------------------
def main():
    running = True

    # Create player and initial platforms
    player = Player(PLAYER_START_X, PLAYER_START_Y)
    platforms = create_platforms()

    # Track camera scroll (how far we've effectively moved "up" in the world)
    camera_scroll = 0
    score = 0

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update player
        player.update(platforms)

        # Update each platform (e.g., moving platforms)
        for p in platforms:
            p.update()

        # "Camera" logic:
        # If the player has moved above the halfway point of the screen,
        # shift everything down to simulate moving the camera up.
        if player.rect.y < HEIGHT // 2:
            shift_amount = (HEIGHT // 2) - player.rect.y
            player.rect.y += shift_amount
            # Increase camera_scroll by how much we shifted
            camera_scroll += shift_amount
            # Shift platforms
            for p in platforms:
                p.rect.y += shift_amount

        # Update Score based on how far camera has scrolled
        if camera_scroll > score:
            score = camera_scroll

        # Check if the player has fallen off the screen
        if player.rect.top > HEIGHT:
            running = False

        # If any platform is completely off the bottom, remove & spawn a new one on top
        for i, p in enumerate(platforms):
            if p.rect.top > HEIGHT:
                # Find the topmost platform's y
                topmost_y = min(plat.rect.y for plat in platforms)
                # Create a new platform above the topmost one
                x = random.randint(0, WIDTH - PLATFORM_WIDTH)
                gap = random.randint(PLATFORM_GAP_MIN, PLATFORM_GAP_MAX)
                new_y = topmost_y - gap
                is_moving = (random.random() < PLATFORM_MOVE_CHANCE)
                platforms[i] = Platform(x, new_y, PLATFORM_WIDTH, PLATFORM_HEIGHT, is_moving)

        # Draw
        screen.fill(BACKGROUND_COLOR)
        for p in platforms:
            p.draw(screen)
        player.draw(screen)

        # Render score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

    # Game Over Screen
    game_over_text = font.render("Game Over!", True, (255, 0, 0))
    final_score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.fill(BACKGROUND_COLOR)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2,
                                 HEIGHT // 2 - game_over_text.get_height() // 2 - 20))
    screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2,
                                   HEIGHT // 2 - final_score_text.get_height() // 2 + 20))
    pygame.display.flip()

    pygame.time.wait(2000)  # Wait a bit before closing
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
