import pygame
import sys

# --- Settings ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (200, 220, 230)
PLAYER_COLOR = (50, 100, 200)
PLAYER_RADIUS = 20
PLAYER_SPEED = 5

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A Day in the Life of a New Yorker")
clock = pygame.time.Clock()

# --- Player Setup ---
player_pos = [WIDTH // 2, HEIGHT // 2]

# --- Wall Setup (simple rectangle boundaries) ---
walls = [
    pygame.Rect(100, 100, 600, 400),  # Main room
    pygame.Rect(350, 100, 10, 150),   # Vertical divider (fake wall)
]

# --- Game Loop ---
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Movement ---
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx = -PLAYER_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx = PLAYER_SPEED
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy = -PLAYER_SPEED
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy = PLAYER_SPEED

    # Attempt move, but apply simple collision check
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy
    future_rect = pygame.Rect(new_x - PLAYER_RADIUS, new_y - PLAYER_RADIUS, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)

    if all(not wall.colliderect(future_rect) for wall in walls):
        player_pos[0] = new_x
        player_pos[1] = new_y

    # --- Draw ---
    screen.fill(BG_COLOR)
    
    # Draw room
    pygame.draw.rect(screen, WHITE, walls[0])
    pygame.draw.rect(screen, BLACK, walls[1])

    # Draw player
    pygame.draw.circle(screen, PLAYER_COLOR, player_pos, PLAYER_RADIUS)

    pygame.display.flip()

pygame.quit()
sys.exit()
