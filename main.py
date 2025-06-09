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
player_pos = [150, 150]  # Start safely inside the room

# --- Wall Setup (simple rectangle boundaries) ---
walls = [
    pygame.Rect(100, 100, 600, 400),  # Main room
    pygame.Rect(350, 100, 10, 150),   # Vertical divider
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

    # Attempt X movement first
    future_rect_x = pygame.Rect(player_pos[0] + dx - PLAYER_RADIUS, player_pos[1] - PLAYER_RADIUS, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
    if all(wall.contains(future_rect_x) or not wall.colliderect(future_rect_x) for wall in walls):
        player_pos[0] += dx

    # Then Y movement
    future_rect_y = pygame.Rect(player_pos[0] - PLAYER_RADIUS, player_pos[1] + dy - PLAYER_RADIUS, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
    if all(wall.contains(future_rect_y) or not wall.colliderect(future_rect_y) for wall in walls):
        player_pos[1] += dy

    # --- Draw ---
    screen.fill(BG_COLOR)
    
    # Draw walls
    for wall in walls:
        pygame.draw.rect(screen, WHITE if wall == walls[0] else BLACK, wall)

    # Draw player
    pygame.draw.circle(screen, PLAYER_COLOR, player_pos, PLAYER_RADIUS)

    # Draw future_rect for debugging (optional)
    debug_rect = pygame.Rect(player_pos[0] - PLAYER_RADIUS, player_pos[1] - PLAYER_RADIUS, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
    pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)

    pygame.display.flip()

pygame.quit()
sys.exit()
