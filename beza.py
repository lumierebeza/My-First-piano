import pygame
import random
import json
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
TILE_WIDTH = SCREEN_WIDTH // 4
TILE_HEIGHT = 150

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_PURPLE = (204, 153, 255)
LIGHT_BLUE = (173, 216, 230)

# Game settings
DAILY_LEVEL_LIMIT = 5
DATA_FILE = "game_data.json"
DEFAULT_SCREEN_LOCK_TIME = 5  # Default to 5 minutes if no input is provided

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My First Piano")

# Load and play background music
pygame.mixer.init()

# List of music tracks
music_tracks = [
    'oldMcdonalds.mp3',
    'Twinkle-Twinkle.mp3',
    'track3.mp3'
]

# Function to play a music track
def play_music(track_index):
    try:
        pygame.mixer.music.load(music_tracks[track_index])
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Error loading music track: {e}")

# Function to read data from the file
def read_game_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"date": "", "levels_completed": 0}

# Function to write data to the file
def write_game_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Function to check if the player can continue
def can_play():
    data = read_game_data()
    today = datetime.now().date().isoformat()
    if data["date"] != today:
        data = {"date": today, "levels_completed": 0}
        write_game_data(data)
    return data["levels_completed"] < DAILY_LEVEL_LIMIT

# Update game data after level completion
def update_level_data():
    data = read_game_data()
    data["levels_completed"] += 1
    write_game_data(data)

# Define a tile class with improved visuals
class Tile:
    def __init__(self, x, y, letter=''):
        self.rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
        self.color = random.choice([BLACK, BLUE, RED])
        self.letter = letter

    def move(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.letter:
            font = pygame.font.SysFont(None, 24)
            textobj = font.render(self.letter, True, WHITE)
            textrect = textobj.get_rect()
            textrect.center = self.rect.center
            screen.blit(textobj, textrect)

# Function to display text
def draw_text(screen, text, font, color, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    screen.blit(textobj, textrect)

# Gradient background function
def draw_gradient_background():
    for y in range(SCREEN_HEIGHT):
        color = (
            int(LIGHT_PURPLE[0] + (LIGHT_BLUE[0] - LIGHT_PURPLE[0]) * y / SCREEN_HEIGHT),
            int(LIGHT_PURPLE[1] + (LIGHT_BLUE[1] - LIGHT_PURPLE[1]) * y / SCREEN_HEIGHT),
            int(LIGHT_PURPLE[2] + (LIGHT_BLUE[2] - LIGHT_PURPLE[2]) * y / SCREEN_HEIGHT)
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

# Level selection screen with improved visuals
def level_selection_screen():
    font = pygame.font.SysFont(None, 30)
    selected_level = 0
    while True:
        draw_gradient_background()
        draw_text(screen, "Select Level", font, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        
        for i, track in enumerate(music_tracks):
            text = f"Level {i+1}"
            color = BLUE if selected_level == i else GREY
            draw_text(screen, text, font, color, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 60)
        
        draw_text(screen, "Press Enter to Start", font, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_level = (selected_level - 1) % len(music_tracks)
                elif event.key == pygame.K_DOWN:
                    selected_level = (selected_level + 1) % len(music_tracks)
                elif event.key == pygame.K_RETURN:
                    return selected_level
        
        pygame.display.flip()
        pygame.time.Clock().tick(30)

# Parent configuration screen to set screen lock time in minutes
def parent_configuration_screen():
    font = pygame.font.SysFont(None, 24)
    input_box = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, SCREEN_WIDTH // 2, 40)
    color_inactive = pygame.Color('black')
    color_active = pygame.Color('black')
    color = color_inactive
    active = False
    text = ''
    clock = pygame.time.Clock()
    max_time = DEFAULT_SCREEN_LOCK_TIME

    while True:
        draw_gradient_background()
        draw_text(screen, "Set Screen Lock Time (minutes):", font, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if text.isdigit():
                        max_time = int(text) * 60  # Convert minutes to seconds
                    return max_time
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        color = color_active if active else color_inactive
        clock.tick(30)

# Main game function with improved visuals
def main():
    title_screen()  # Display title screen before level selection

    # Get screen lock time from parent
    screen_lock_time = parent_configuration_screen()
    if screen_lock_time is None:
        return

    while True:
        level = level_selection_screen()
        if level is None:
            return

        if not can_play():
            print("Daily limit reached. Try again tomorrow!")
            return

        clock = pygame.time.Clock()
        speed = 3  # Slower tile speed
        tiles = []
        score = 0
        font = pygame.font.SysFont(None, 24)
        start_time = pygame.time.get_ticks()
        tile_timer = pygame.time.get_ticks()

        # Play the selected music track
        play_music(level)

        # Define the target words for each level
        target_words = ["FARM", "TWINKLE"]
        expected_word = target_words[level]
        
        def draw_score(score):
            text = font.render(f"Score: {score}", True, BLACK)
            screen.blit(text, [10, 10])

        def draw_target_word(word):
            text = font.render(f"Form Word: {word}", True, BLACK)
            screen.blit(text, [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30])

        def create_tile():
            x = random.randint(0, 3) * TILE_WIDTH
            letter = random.choice([chr(random.randint(65, 90)), ''])  # Random letter or empty
            return Tile(x, -TILE_HEIGHT, letter)

        def display_message(message):
            font = pygame.font.SysFont(None, 24)
            textobj = font.render(message, True, BLACK)
            textrect = textobj.get_rect()
            textrect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            screen.blit(textobj, textrect)
            pygame.display.flip()
            pygame.time.wait(2000)  # Wait for 2 seconds

        def restart_game():
            while True:
                draw_gradient_background()
                draw_text(screen, "Game Over!", pygame.font.SysFont(None, 36), BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
                draw_text(screen, "Click to Restart", pygame.font.SysFont(None, 24), BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        return main()

        while True:
            screen.fill(WHITE)
            draw_gradient_background()
            draw_score(score)
            draw_target_word(expected_word)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for tile in tiles:
                        if tile.rect.collidepoint(event.pos):
                            if tile.letter and tile.letter == expected_word[0]:
                                expected_word = expected_word[1:]  # Remove the first letter
                                score += 1
                                tiles.remove(tile)
                            else:
                                display_message("Game Over!")
                                restart_game()
                                return

            if pygame.time.get_ticks() - tile_timer > 1000:  # Add new tile every 1000ms
                tiles.append(create_tile())
                tile_timer = pygame.time.get_ticks()

            for tile in tiles[:]:
                tile.move(speed)
                if tile.rect.top > SCREEN_HEIGHT:
                    tiles.remove(tile)

            if not expected_word:  # If the word is formed
                display_message("Congratulations! Level Completed!")
                update_level_data()
                break

            for tile in tiles:
                tile.draw(screen)

            if pygame.time.get_ticks() - start_time > screen_lock_time * 1000:  # Screen lock time check
                display_message("Time's Up! Screen Locked.")
                return

            pygame.display.flip()
            clock.tick(60)

def title_screen():
    font = pygame.font.SysFont(None, 48)
    while True:
        draw_gradient_background()
        draw_text(screen, "My First Piano", font, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text(screen, "Press Enter to Start", pygame.font.SysFont(None, 36), BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

# Run the game
if __name__ == "__main__":
    main()
    pygame.quit()
