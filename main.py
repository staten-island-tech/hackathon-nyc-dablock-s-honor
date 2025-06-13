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
player_direction = "down"  # Default facing down



player_images = {
    "up": pygame.image.load("player_up.png").convert_alpha(),
    "down": pygame.image.load("player_down.png").convert_alpha(),
    "left": pygame.image.load("player_left.png").convert_alpha(),
    "right": pygame.image.load("player_right.png").convert_alpha()
}


# --- Player Setup ---
player_pos = [150, 150]  # Start safely inside the room

# --- Wall Setup (simple rectangle boundaries) ---
walls = [
    pygame.Rect(100, 100, 600, 400),  # Main room
    pygame.Rect(350, 100, 10, 150),   # Vertical divider
]

game_state = "cutscene"

dialogue = [
    "Ugh... another day in the city.",
    "Gotta get ready and catch the subway.",
    "Hope the coffee place isn’t packed again..."
]

def run_cutscene(screen, clock, font, dialogue_lines):
    text_index = 0
    letter_index = 0
    timer = pygame.time.get_ticks()
    typing_speed = 50  # ms per character
    done = False
    key_released = True
    prompt_delay_timer = None
    prompt_delay_duration = 1000  # 1.5 seconds
    showing_prompt = False
    waiting_for_key = False
    fade_alpha = 255
    fade_speed = 5
    fading_in = True

    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))

    while not done:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                key_released = True
            elif event.type == pygame.KEYDOWN and key_released:
                key_released = False

                if showing_prompt and waiting_for_key:
                    text_index += 1
                    letter_index = 0
                    prompt_delay_timer = None
                    showing_prompt = False
                    waiting_for_key = False
                    fading_in = (text_index == 0)  # Optional: only fade first line

                if text_index >= len(dialogue_lines):
                    done = True
                    break

        # Typewriter logic
        if text_index < len(dialogue_lines):
            line = dialogue_lines[text_index]

            if letter_index < len(line):
                if pygame.time.get_ticks() - timer > typing_speed:
                    letter_index += 1
                    timer = pygame.time.get_ticks()

            rendered_text = font.render(line[:letter_index], True, WHITE)
            screen.blit(rendered_text, (50, HEIGHT // 2))

            if letter_index >= len(line):
                if prompt_delay_timer is None:
                    prompt_delay_timer = pygame.time.get_ticks()

                elif pygame.time.get_ticks() - prompt_delay_timer >= prompt_delay_duration:
                    prompt = font.render("Press any key to continue...", True, (180, 180, 180))
                    screen.blit(prompt, (50, HEIGHT // 2 + 40))
                    showing_prompt = True
                    waiting_for_key = True

        # Fade only at start
        if text_index == 0 and fading_in:
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
            fade_alpha -= fade_speed
            if fade_alpha <= 0:
                fading_in = False

        pygame.display.flip()
        clock.tick(FPS)



font = pygame.font.SysFont(None, 32)
dialogue = [
    "Dang...those cars had me awake all night.",
    "Gotta catch the N train before it leaves...",
    "Might as well get a coffee before I go to work."
]
run_cutscene(screen, clock, font, dialogue)

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
        player_direction = "left"
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx = PLAYER_SPEED
        player_direction = "right"
    elif keys[pygame.K_UP] or keys[pygame.K_w]:
        dy = -PLAYER_SPEED
        player_direction = "up"
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy = PLAYER_SPEED
        player_direction = "down"


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
    player_sprite = player_images[player_direction]
    sprite_rect = player_sprite.get_rect(center=player_pos)
    screen.blit(player_sprite, sprite_rect)

    # Draw future_rect for debugging (optional)
    debug_rect = pygame.Rect(player_pos[0] - PLAYER_RADIUS, player_pos[1] - PLAYER_RADIUS, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
    pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)

    pygame.display.flip()

pygame.quit()
sys.exit()
