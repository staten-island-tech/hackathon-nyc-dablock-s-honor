import pygame
import sys

# --- Settings ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (245, 235, 220)  # Light tan
WALL_COLOR = (80, 60, 50)   # Dark brown for walls
PLAYER_COLOR = (50, 100, 200)
PLAYER_RADIUS = 20
PLAYER_SIZE = (32, 45)  # Desired width and height for all player sprites
PLAYER_SPEED = 2.3

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A Day in the Life of a New Yorker")
clock = pygame.time.Clock()
player_direction = "down"  # Default facing down

animation_frame = 0
animation_speed = 150  # milliseconds per frame
last_frame_update = pygame.time.get_ticks()

def load_and_scale(path):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, PLAYER_SIZE)


player_animations = {
    "up": [
        load_and_scale("pokemon_backward_1.png"),
        load_and_scale("pokemon_backward_2.png"),
        load_and_scale("pokemon_backward_3.png")
    ],
    "down": [
        load_and_scale("pokemon_forward_1.png"),
        load_and_scale("pokemon_forward_2.png"),
        load_and_scale("pokemon_forward_3.png")
    ],
    "left": [
        load_and_scale("pokemon_left_1.png"),
        load_and_scale("pokemon_left_2.png"),
        load_and_scale("pokemon_left_3.png")
    ],
    "right": [
        load_and_scale("pokemon_right_1.png"),
        load_and_scale("pokemon_right_2.png"),
        load_and_scale("pokemon_right_3.png")
    ],
}


# --- Player Setup ---
player_pos = [150, 150]  # Start safely inside the room

# --- Wall Setup (simple rectangle boundaries) ---
walls = [
    # Outer walls
    pygame.Rect(100, 100, 600, 10),   # Top wall
    pygame.Rect(100, 490, 600, 10),   # Bottom wall
    pygame.Rect(100, 100, 10, 400),   # Left wall
    pygame.Rect(690, 100, 10, 400),   # Right wall

    # Inner walls
    pygame.Rect(300, 100, 10, 200),   # Vertical wall splitting bedroom
    pygame.Rect(300, 300, 200, 10),   # Horizontal wall splitting kitchen/living
    pygame.Rect(500, 300, 10, 190),   # Right vertical wall of kitchen
    pygame.Rect(300, 400, 200, 10),   # Bottom divider wall
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
    typing_speed = 50  # ms per character
    fade_alpha = 255
    fade_speed = 3
    done = False
    key_released = True

    fading_in = False
    fade_to_cutscene_bg = True
    fading_out_to_black = False
    fade_into_game = False   # <- make sure THIS line is here!
    black_pause_after_fade_out = False
    black_pause_timer = None


    initial_black_pause = 1500  # milliseconds
    initial_pause_start = pygame.time.get_ticks()

    prompt_delay_timer = None
    prompt_delay_duration = 1000
    show_prompt = False
    waiting_for_key = False

    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))

    typewriter_timer = pygame.time.get_ticks()
    show_first_line_timer = None
    wait_before_typing = 1000

    # Start with full black
    screen.fill((0, 0, 0))
    pygame.display.flip()

    while not done:
        screen.fill((30, 30, 30))  # Cutscene background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                key_released = True
            elif event.type == pygame.KEYDOWN and key_released:
                key_released = False

                if text_index < len(dialogue_lines) and letter_index < len(dialogue_lines[text_index]):
                    # Skip to full line if still typing
                    letter_index = len(dialogue_lines[text_index])
                else:
                    # Advance to next line if fully typed
                    text_index += 1
                    letter_index = 0
                    prompt_delay_timer = None
                    show_prompt = False
                    waiting_for_key = False

                    if text_index >= len(dialogue_lines):
                        fading_out_to_black = True
                        fade_alpha = 0
                        black_pause_timer = pygame.time.get_ticks()


        now = pygame.time.get_ticks()

        # 1. Initial black screen pause
        if fade_to_cutscene_bg:
            if now - initial_pause_start < initial_black_pause:
                screen.fill((0, 0, 0))
            else:
                fading_in = True
                fade_to_cutscene_bg = False

        # 2. Fade-in from black to cutscene background
        elif fading_in:
            fade_alpha -= fade_speed
            if fade_alpha <= 0:
                fade_alpha = 0
                fading_in = False
                show_first_line_timer = pygame.time.get_ticks()

            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))

        # 3. Wait before starting first line
        elif text_index == 0 and show_first_line_timer:
            if now - show_first_line_timer < wait_before_typing:
                pass
            else:
                show_first_line_timer = None

        # 4. Typewriter effect
        if not fading_in and not fade_to_cutscene_bg and not show_first_line_timer and not fading_out_to_black and text_index < len(dialogue_lines):
            line = dialogue_lines[text_index]
            if letter_index < len(line):
                if now - typewriter_timer > typing_speed:
                    letter_index += 1
                    typewriter_timer = now

            rendered_text = font.render(line[:letter_index], True, WHITE)
            screen.blit(rendered_text, (50, HEIGHT // 2))

            if letter_index >= len(line):
                if prompt_delay_timer is None:
                    prompt_delay_timer = now
                elif now - prompt_delay_timer >= prompt_delay_duration:
                    # Blink prompt
                    blink_interval = 800
                    if (now // blink_interval) % 2 == 0:
                        prompt = font.render("Press any key to continue...", True, (180, 180, 180))
                        screen.blit(prompt, (50, HEIGHT // 2 + 40))
                    show_prompt = True
                    waiting_for_key = True

        # 5. Fade to black after final line
        if fading_out_to_black:
            fade_alpha += fade_speed
            if fade_alpha >= 255:
                fade_alpha = 255
                fading_out_to_black = False
                black_pause_after_fade_out = True
                black_pause_timer = now

            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))

        # 6. Wait on black before fading into gameplay
        if black_pause_after_fade_out:
            screen.fill((0, 0, 0))
            if now - black_pause_timer >= 1500:
                fade_into_game = True
                black_pause_after_fade_out = False
                fade_alpha = 255

        # 7. Fade into gameplay scene
        if fade_into_game:
            # Draw the actual game background now (fade will go over it)
            screen.fill(BG_COLOR)

            # Draw walls with new color
            for wall in walls:
                pygame.draw.rect(screen, WALL_COLOR, wall)

            # --- Draw furniture and room elements ---
            # Bed
            pygame.draw.rect(screen, (150, 100, 100), pygame.Rect(120, 120, 80, 40))

            # Table
            pygame.draw.rect(screen, (180, 140, 100), pygame.Rect(350, 320, 60, 30))

            # Couch
            pygame.draw.rect(screen, (200, 100, 50), pygame.Rect(500, 420, 100, 40))

            # Kitchen counter
            pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(310, 310, 60, 10))

            # Door (optional)
            pygame.draw.rect(screen, (120, 60, 40), pygame.Rect(385, 490, 30, 10))

            # Draw player sprite
            player_sprite = player_animations[player_direction][animation_frame]
            sprite_rect = player_sprite.get_rect(center=player_pos)
            screen.blit(player_sprite, sprite_rect)


            # Fade surface overlays game scene
            fade_alpha -= fade_speed
            if fade_alpha <= 0:
                fade_alpha = 0
                done = True
            else:
                fade_surface.set_alpha(fade_alpha)
                screen.blit(fade_surface, (0, 0))


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
    moving = False

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx = -PLAYER_SPEED
        player_direction = "left"
        moving = True
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx = PLAYER_SPEED
        player_direction = "right"
        moving = True

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy = -PLAYER_SPEED
        player_direction = "down"  # WAS 'up' before
        moving = True
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy = PLAYER_SPEED
        player_direction = "up"  # WAS 'down' before
        moving = True


    # Apply movement with simple collision detection
    new_pos = [player_pos[0] + dx, player_pos[1] + dy]
    player_rect = pygame.Rect(
        new_pos[0] - PLAYER_SIZE[0] // 2,
        new_pos[1] - PLAYER_SIZE[1] // 2,
        PLAYER_SIZE[0],
        PLAYER_SIZE[1]
    )


    # Check collision against walls
    collision = False
    # Only check against actual wall dividers
    for wall in walls[1:]:
        if player_rect.colliderect(wall):
            collision = True
            break


    if not collision:
        player_pos[0] = new_pos[0]
        player_pos[1] = new_pos[1]

    # Animate only if moving
    if moving:
        now = pygame.time.get_ticks()
        if now - last_frame_update > animation_speed:
            animation_frame = (animation_frame + 1) % 3
            last_frame_update = now
    else:
        animation_frame = 0

    # Draw everything
    screen.fill(BG_COLOR)

    # Draw walls
    for wall in walls:
        pygame.draw.rect(screen, WHITE if wall == walls[0] else BLACK, wall)

    # Draw player sprite with current animation frame
    player_sprite = player_animations[player_direction][animation_frame]
    sprite_rect = player_sprite.get_rect(center=player_pos)
    screen.blit(player_sprite, sprite_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
