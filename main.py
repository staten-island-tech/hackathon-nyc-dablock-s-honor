import pygame
import sys
import math
import numpy as np  # Required for movie frame conversion
from moviepy import VideoFileClip

# --- Settings ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (245, 235, 220)  # Light tan
WALL_COLOR = (80, 60, 50)
PLAYER_SIZE = (32, 45)
PLAYER_SPEED = 2.3

pizza_buildings_passed = 0
dialogue_shown = False
dialogue_timer = None
dialogue_duration = 4000  # 4 seconds


# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A Day in the Life of a New Yorker")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

pizza_building_entrance = pygame.Rect(WIDTH//2 + 400, HEIGHT//2 - 150, 100, 150)


player_direction = "down"
animation_frame = 0
animation_speed = 150
last_frame_update = pygame.time.get_ticks()
walls = []

def load_and_scale(path):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, PLAYER_SIZE)

player_animations = {
    "up": [load_and_scale(f"pokemon_forward_{i}.png") for i in range(1, 4)],
    "down": [load_and_scale(f"pokemon_backward_{i}.png") for i in range(1, 4)],
    "left": [load_and_scale(f"pokemon_left_{i}.png") for i in range(1, 4)],
    "right": [load_and_scale(f"pokemon_right_{i}.png") for i in range(1, 4)],
}

# Player starts in front of bed (adjusted to not overlap bed)
player_pos = [635, 400]

# Door interaction zone inside house (slightly bigger for easier interaction)
door_rect = pygame.Rect(370, 480, 60, 30)

# --- City buildings collision rects ---
city_buildings = []

def init_city_buildings():
    global city_buildings
    city_buildings.clear()
    building_positions = [100, 250, 400, 550, 700]
    building_width = 80
    building_height = 150
    for x in building_positions:
        rect = pygame.Rect(x, HEIGHT//2 - building_height, building_width, building_height)
        city_buildings.append(rect)

init_city_buildings()

def draw_room(screen):
    screen.fill(BG_COLOR)  # background outside room

    room_rect = pygame.Rect(100, 100, 600, 400)
    pygame.draw.rect(screen, (150, 110, 75), room_rect)  # interior floor

    walls.clear()

    top = pygame.Rect(100, 100, 600, 10)
    bottom = pygame.Rect(100, 490, 600, 10)
    left = pygame.Rect(100, 100, 10, 400)
    right = pygame.Rect(690, 100, 10, 400)
    for wall in [top, bottom, left, right]:
        pygame.draw.rect(screen, WALL_COLOR, wall)
        walls.append(wall)

    # Bed adjusted so player can stand near door, not stuck inside bed
    bed = pygame.Rect(600, 460, 70, 40)
    pygame.draw.rect(screen, (180, 100, 120), bed)
    walls.append(bed)

    pygame.draw.rect(screen, (180, 160, 120), pygame.Rect(370, 480, 60, 30))  # door

    desk = pygame.Rect(130, 130, 60, 30)
    pygame.draw.rect(screen, (160, 120, 90), desk)
    walls.append(desk)

    bookshelf = pygame.Rect(200, 130, 20, 60)
    pygame.draw.rect(screen, (100, 70, 50), bookshelf)
    walls.append(bookshelf)

    tv = pygame.Rect(130, 100, 60, 20)
    pygame.draw.rect(screen, (20, 20, 20), tv)
    walls.append(tv)

    wardrobe = pygame.Rect(260, 130, 40, 60)
    pygame.draw.rect(screen, (140, 100, 80), wardrobe)
    walls.append(wardrobe)

    table = pygame.Rect(350, 300, 100, 60)
    pygame.draw.rect(screen, (180, 140, 100), table)
    walls.append(table)

    couch = pygame.Rect(150, 400, 120, 40)
    pygame.draw.rect(screen, (200, 100, 50), couch)
    walls.append(couch)

    counter = pygame.Rect(110, 250, 60, 20)
    pygame.draw.rect(screen, (100, 100, 100), counter)
    walls.append(counter)

def draw_city(screen, camera_x):
    screen.fill((135, 206, 235))  # Light sky blue background

    # Draw ground
    ground_rect = pygame.Rect(0, HEIGHT // 2, WIDTH, HEIGHT // 2)
    pygame.draw.rect(screen, (50, 50, 50), ground_rect)  # street

    # Sidewalk border lines
    border_thickness = 8
    border_color = (220, 220, 220)
    pygame.draw.rect(screen, border_color, pygame.Rect(0, HEIGHT//2 - border_thickness, WIDTH, border_thickness))
    pygame.draw.rect(screen, border_color, pygame.Rect(0, HEIGHT - border_thickness, WIDTH, border_thickness))

    # Repeating buildings based on camera_x
    building_width = 100
    building_height = 150
    spacing = 150

    for i in range(-2, 10):
        x = i * spacing - (camera_x % spacing)
        world_x = camera_x + x

        building_rect = pygame.Rect(x, HEIGHT//2 - building_height, building_width, building_height)

        if world_x < 2000:
            pygame.draw.rect(screen, (70, 70, 90), building_rect)
        else:
            # Pizza shop
            pygame.draw.rect(screen, (200, 80, 30), building_rect)

            # Special red sign above one enterable pizza shop at x = 2600
            if world_x == 2600:
                sign_rect = pygame.Rect(x + building_width // 2 - 10, HEIGHT//2 - building_height - 20, 20, 20)
                pygame.draw.rect(screen, (255, 0, 0), sign_rect)

            pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(x + 20, HEIGHT//2 - 120, 60, 30))  # pizza sign background
            font_small = pygame.font.SysFont(None, 24)
            text = font_small.render("Pizza", True, (0, 0, 0))
            screen.blit(text, (x + 30, HEIGHT//2 - 115))
    
    # Special enterable pizza building at the end
    entrance_screen_x = pizza_building_entrance.x - camera_x
    if 0 <= entrance_screen_x <= WIDTH:
        pygame.draw.rect(screen, (220, 50, 50), pygame.Rect(entrance_screen_x, pizza_building_entrance.y, pizza_building_entrance.width, pizza_building_entrance.height))
        pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(entrance_screen_x + 20, pizza_building_entrance.y + 20, 60, 30))  # pizza sign
        text = pygame.font.SysFont(None, 28).render("Pizza", True, (0, 0, 0))
        screen.blit(text, (entrance_screen_x + 25, pizza_building_entrance.y + 25))

        # --- Draw final pizza building at the end of the street ---
    final_pizza_world_x = 4500
    final_pizza_screen_x = final_pizza_world_x - camera_x
    final_pizza_screen_y = HEIGHT // 2 - 80
    final_pizza_width = 120
    final_pizza_height = 200

    # Draw building (different color so it stands out)
    pygame.draw.rect(screen, (255, 255, 0), (final_pizza_screen_x, final_pizza_screen_y, final_pizza_width, final_pizza_height))

    # Draw door
    pygame.draw.rect(screen, (100, 100, 100), (final_pizza_screen_x + 30, final_pizza_screen_y + 140, 60, 60))

    # Label on building
    font_large = pygame.font.SysFont(None, 24)
    label = font_large.render("Big Pizza", True, (0, 0, 0))
    screen.blit(label, (final_pizza_screen_x + 10, final_pizza_screen_y + 10))

        # --- Draw barrier at end of road before Big Pizza ---
    barrier_world_x = 4450
    barrier_screen_x = barrier_world_x - camera_x
    barrier_y = HEIGHT // 2 - 20
    barrier_width = 10
    barrier_height = 200

    # Draw a vertical black barrier
    pygame.draw.rect(screen, (0, 0, 0), (barrier_screen_x, barrier_y, barrier_width, barrier_height))

        # Darken road beyond the barrier to make it look closed
    road_overlay_rect = pygame.Rect(barrier_screen_x + barrier_width, barrier_y, WIDTH, barrier_height)
    dark_overlay = pygame.Surface((road_overlay_rect.width, road_overlay_rect.height), pygame.SRCALPHA)
    dark_overlay.fill((0, 0, 0, 150))  # Semi-transparent black
    screen.blit(dark_overlay, (barrier_screen_x + barrier_width, barrier_y))







def is_near(rect1, rect2, distance=10):
    # Keep inflation only if distance > 0, else no inflation (stricter)
    if distance > 0:
        return rect1.colliderect(rect2.inflate(distance, distance))
    else:
        return rect1.colliderect(rect2)

# --- Cutscene ---
def run_cutscene(screen, clock, font, dialogue_lines):
    text_index = 0
    letter_index = 0
    typing_speed = 50
    fade_alpha = 255
    fade_speed = 3
    done = False
    key_released = True
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))
    fading_in = False
    fade_to_cutscene_bg = True
    fading_out_to_black = False
    fade_into_game = False
    black_pause_after_fade_out = False
    black_pause_timer = None

    initial_pause_start = pygame.time.get_ticks()
    prompt_delay_timer = None
    prompt_delay_duration = 1000
    show_prompt = False
    waiting_for_key = False
    typewriter_timer = pygame.time.get_ticks()
    show_first_line_timer = None
    wait_before_typing = 1000

    screen.fill((0, 0, 0))
    pygame.display.flip()

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
                if text_index < len(dialogue_lines) and letter_index < len(dialogue_lines[text_index]):
                    letter_index = len(dialogue_lines[text_index])
                else:
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

        if fade_to_cutscene_bg:
            if now - initial_pause_start < 1500:
                screen.fill((0, 0, 0))
            else:
                fading_in = True
                fade_to_cutscene_bg = False

        elif fading_in:
            fade_alpha -= fade_speed
            if fade_alpha <= 0:
                fade_alpha = 0
                fading_in = False
                show_first_line_timer = pygame.time.get_ticks()
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))

        elif text_index == 0 and show_first_line_timer:
            if now - show_first_line_timer < wait_before_typing:
                pass
            else:
                show_first_line_timer = None

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
                    if (now // 800) % 2 == 0:
                        prompt_text = font.render("Press Space to Continue", True, WHITE)
                        screen.blit(prompt_text, (50, HEIGHT // 2 + 40))
                    waiting_for_key = True

        if fading_out_to_black:
            fade_alpha += fade_speed
            if fade_alpha >= 255:
                fade_alpha = 255
                if black_pause_timer is None:
                    black_pause_timer = now
                elif now - black_pause_timer >= 1000:
                    done = True
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)
        
def play_jumpscare(screen, video_path):
    from moviepy import VideoFileClip

    clip = VideoFileClip(video_path)

    # Set size to your pygame screen size
    WIDTH, HEIGHT = screen.get_size()

    for frame in clip.iter_frames(fps=clip.fps, dtype='uint8'):
        # Convert frame (numpy array) to pygame surface
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0,1))
        
        # Resize the surface to fit screen size
        frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))
        
        # Display the frame
        screen.blit(frame_surface, (0, 0))
        pygame.display.update()
        
        # Maintain frame rate
        pygame.time.wait(int(1000 / clip.fps))

    pygame.quit()
    sys.exit()


# --- Main Game Loop ---
def main():
    global player_pos, player_direction, animation_frame, last_frame_update
    global pizza_buildings_passed, dialogue_shown, dialogue_timer
    inside_house = True
    running = True
    # ... rest of your code

    e_pressed = False
    camera_x = 0  # <-- Add this

    e_pressed = False

    while running:
        dt = clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    # Define Big Pizza Building barrier and interaction zone
        big_pizza_rect = pygame.Rect(2600, HEIGHT // 2 - 50, 200, 200)  # Big building blocking road
        big_pizza_entrance = pygame.Rect(2600 + 75, HEIGHT // 2 + 50, 50, 50)  # Center entrance area

        # --- Movement ---
        player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_SIZE[0], PLAYER_SIZE[1])
        prev_pos = player_pos.copy()

        dx = dy = 0
        if keys[pygame.K_w]:
            dy = -PLAYER_SPEED
            player_direction = "up"
        elif keys[pygame.K_s]:
            dy = PLAYER_SPEED
            player_direction = "down"
        if inside_house:
            if keys[pygame.K_a]:
                dx = -PLAYER_SPEED
                player_direction = "left"
            elif keys[pygame.K_d]:
                dx = PLAYER_SPEED
                player_direction = "right"
        else:
            dx = 0  # Don't move player on screen, move camera instead
            if keys[pygame.K_d]:
                player_direction = "right"
                camera_x += PLAYER_SPEED
            elif keys[pygame.K_a] and camera_x > 0:
                player_direction = "left"
                camera_x -= PLAYER_SPEED

        # Only one pizza building at x=2600
        pizza_building_x = 2600

        # Update pizza_buildings_passed once player/camera passes pizza_building_x - some margin
        if camera_x > pizza_building_x - 100:
            pizza_buildings_passed = 1
        else:
            pizza_buildings_passed = 0


        
        # Apply movement
        # Apply movement
        if inside_house:
            player_pos[0] += dx
            player_pos[1] += dy
        else:
            player_pos[1] += dy  # Only Y movement updates player position
            # X movement handled via camera_x earlier; no overwrite here!


        # Update rect
        player_rect.topleft = player_pos

        # Collision with walls or city buildings
        # Collision with walls or city buildings
        collidable = walls if inside_house else city_buildings.copy()

        if not inside_house:
            # Add the big pizza place as a blocking wall
            collidable.append(big_pizza_rect)
        for wall in collidable:
            if player_rect.colliderect(wall):
                player_pos = prev_pos
                player_rect.topleft = player_pos
                break

        # Interaction zone for player (no inflation outside house, stricter)
        # We'll keep inflation inside house for easier door exit detection
        interaction_zone = player_rect.inflate(10, 10) if inside_house else player_rect

        can_interact = False

        if inside_house:
            # Interaction with inside door to exit
            can_interact = interaction_zone.colliderect(door_rect)
            if can_interact and keys[pygame.K_e]:
                if not e_pressed:
                    inside_house = False
                    # Move player outside near house entrance
                    player_pos = [400, HEIGHT // 2 + 110]
                    e_pressed = True
        else:
            can_interact = False

            # Shift big pizza entrance rect by camera offset to get screen coordinates
            pizza_entrance_screen_rect = big_pizza_entrance.move(-camera_x, 0)

            # Define player's rectangle on screen (player X fixed center of screen)
            player_screen_rect = pygame.Rect(WIDTH // 2 - PLAYER_SIZE[0] // 2, player_pos[1], PLAYER_SIZE[0], PLAYER_SIZE[1])

            # Check collision using screen coords, not world coords
            if player_screen_rect.colliderect(pizza_entrance_screen_rect):
                can_interact = True
                if keys[pygame.K_e] and not e_pressed:
                    print("Entering the BIG PIZZA PLACE!")
                    # Teleport player to a defined location (e.g., inside pizza place)
                    player_pos[0] = 3000  # example X inside pizza place
                    player_pos[1] = HEIGHT // 2
                    e_pressed = True  # reset E press to avoid repeat

                    # Play jumpscare video
                    play_jumpscare(screen, "jumpscare.mp4")


        # Reset e_pressed once, only if E is NOT pressed this frame at all
        if not keys[pygame.K_e]:
            e_pressed = False

        

        # --- Drawing ---
        if inside_house:
            draw_room(screen)
        else:
            draw_city(screen, camera_x)
            # Draw Big Pizza Place
            pizza_building_color = (255, 50, 50)
            pizza_border_color = (180, 0, 0)

            building_screen_rect = big_pizza_rect.move(-camera_x, 0)
            pygame.draw.rect(screen, pizza_building_color, building_screen_rect)
            pygame.draw.rect(screen, pizza_border_color, building_screen_rect, 4)

            # Optional: Pizza sign
            pizza_text = font.render("PIZZA", True, (255, 255, 255))
            screen.blit(pizza_text, (building_screen_rect.x + 60, building_screen_rect.y + 10))

            # DEBUG: Draw big pizza entrance rect in green with some transparency
            pizza_entrance_screen_rect = big_pizza_entrance.move(-camera_x, 0)
            debug_surface = pygame.Surface((pizza_entrance_screen_rect.width, pizza_entrance_screen_rect.height), pygame.SRCALPHA)
            debug_surface.fill((0, 255, 0, 100))  # semi-transparent green
            screen.blit(debug_surface, pizza_entrance_screen_rect.topleft)


        # Draw player animation frame

        # Show dialogue when between 2 and 4 pizza buildings passed and dialogue not yet shown
        # Show dialogue when pizza_buildings_passed >= 1 and dialogue not yet shown
        if pizza_buildings_passed >= 1 and not dialogue_shown:
            if dialogue_timer is None:
                dialogue_timer = pygame.time.get_ticks()
            current_time = pygame.time.get_ticks()
            
            # Message box dimensions
            box_width = WIDTH - 100
            box_height = 80
            box_x = 50
            box_y = HEIGHT - box_height - 50
            
            # Colors
            box_bg_color = (255, 255, 255)
            box_border_color = (0, 0, 0)
            
            # Draw box background
            pygame.draw.rect(screen, box_bg_color, (box_x, box_y, box_width, box_height))
            # Draw box border (thicker lines)
            pygame.draw.rect(screen, box_border_color, (box_x, box_y, box_width, box_height), 4)
            
            # Padding inside the box
            padding_x = 15
            padding_y = 15
            
            message = "What the... why are there so many pizza buildings?"
            # Render text (wrap if needed)
            # For now, assume fits one line. If needed, split manually or use a helper function.
            text_surface = font.render(message, True, (0, 0, 0))
            screen.blit(text_surface, (box_x + padding_x, box_y + padding_y))

            
            # Blinking arrow at bottom right of box
            blink_speed = 500  #


        # Animate only when moving
        moved = (dx != 0 or dy != 0)

        now = pygame.time.get_ticks()
        if moved:
            if now - last_frame_update > animation_speed:
                animation_frame = (animation_frame + 1) % 3
                last_frame_update = now
        else:
            animation_frame = 0  # Reset to idle frame if not moving

        # Draw shadow (oval under player)
        # Draw shadow (oval under player)
        shadow_width = PLAYER_SIZE[0]
        shadow_height = 12  # Flat shadow
        shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), shadow_surface.get_rect())

        player_img = player_animations[player_direction][animation_frame]

        if inside_house:
            shadow_pos = (player_pos[0], player_pos[1] + PLAYER_SIZE[1] - 10)
            screen.blit(shadow_surface, shadow_pos)
            screen.blit(player_img, player_pos)
        else:
            player_screen_x = WIDTH // 2 - PLAYER_SIZE[0] // 2
            player_screen_y = player_pos[1]  # Use player's Y position outside

            # Draw shadow and player at same coordinates
            shadow_pos = (player_screen_x, player_screen_y + PLAYER_SIZE[1] - 10)
            screen.blit(shadow_surface, shadow_pos)
            screen.blit(player_img, (player_screen_x, player_screen_y))



        # Draw interaction prompt text ONLY inside house near door (NO prompt outside)
        if can_interact:
            if inside_house:
                instruction = font.render("Press E to Exit", True, WHITE)
                screen.blit(instruction, (player_pos[0] - 20, player_pos[1] - 30))
            else:
                instruction = font.render("Press E to Enter Pizza", True, WHITE)
                screen.blit(instruction, (WIDTH // 2 - 60, player_pos[1] - 30))


        pygame.display.flip()

    pygame.quit()

# --- Run game ---
cutscene_text = [
    "This is a day in the life of a New Yorker...",
    "A world of hustle, bustle, and endless stories."
]

run_cutscene(screen, clock, font, cutscene_text)
main()
