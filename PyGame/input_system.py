import pygame
import json
import os
from game_data import GameData
import game_music
from controller import Controller

# Pygame alustus
pygame.init()

# Näytön koko
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Nimimerkin valinta")

# Värit
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

# Fontti
font = pygame.font.Font(None, 72)

# Tallennustiedosto
SAVE_FILE = "saves.json"

# Kirjaimet A-Z
LETTERS = [chr(i) for i in range(ord("A"), ord("Z") + 1)]

# Selvitetään kansion polku
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_leaderboard():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return json.load(file)
    return []

def save_leaderboard(data):
    with open(SAVE_FILE, "w") as file:
        json.dump(data, file, indent=4)

def load_sprite(filename, width, height):
    image = pygame.image.load(os.path.join(BASE_DIR, filename))
    return pygame.transform.scale(image, (int(width), int(height)))

class NameInput:
    def __init__(self, score, time_elapsed):
        self.score = score
        self.time_elapsed = time_elapsed
        self.current_slot = 0
        self.current_name = ["A", "A", "A"]
        self.leaderboard = load_leaderboard()
        self.saved = False

        self.menu_active = True
        self.selection_mode = "letters"
        self.selected_button = 0

        self.button_width = 503.5
        self.button_height = 133

        self.button_images = {
            "Hyväksy": (
                load_sprite("hyvaksy.png", self.button_width, self.button_height),
                load_sprite("hyvaksy_hover.png", self.button_width, self.button_height)
            ),
            "Takaisin": (
                load_sprite("paavalikko.png", self.button_width, self.button_height),
                load_sprite("paavalikko_hover.png", self.button_width, self.button_height)
            ),
            "Poista": (
                load_sprite("poista.png", self.button_width, self.button_height),
                load_sprite("poista_hover.png", self.button_width, self.button_height)
            ),
        }

        self.buttons = [
            {"name": "Hyväksy", "action": "save"},
            {"name": "Takaisin", "action": "exit"},
            {"name": "Poista", "action": "delete"},
        ]

        # Ohjain
        self.controller = Controller()

    def draw_text(self, text, x, y, color=BLACK):
        render = font.render(text, True, color)
        screen.blit(render, (x, y))

    def draw_ui(self):
        screen_width, screen_height = screen.get_size()
        background_path = os.path.join(BASE_DIR, "gameover.png")

        if not os.path.isfile(background_path):
            raise FileNotFoundError(f"Ei löydy tiedostoa: {background_path}")

        background = pygame.image.load(background_path)
        background = pygame.transform.scale(background, (screen_width, screen_height))
        screen.blit(background, (0, 0))

        # Otsikko
        title_surf = font.render("Valitse nimimerkki", True, BLACK)
        title_rect = title_surf.get_rect(center=(screen_width * 0.5, screen_height * 0.2))
        screen.blit(title_surf, title_rect)

        # Nimimerkin kirjaimet
        spacing = screen_width * 0.08
        for i, letter in enumerate(self.current_name):
            color = GRAY if self.selection_mode == "letters" and i == self.current_slot else BLACK
            letter_surf = font.render(letter, True, color)
            letter_rect = letter_surf.get_rect(center=(screen_width * 0.5 + (i - 1) * spacing, screen_height * 0.3))
            screen.blit(letter_surf, letter_rect)

        # Painikkeet
        button_y_start = screen_height * 0.51
        button_spacing = screen_height * 0.17

        for i, button in enumerate(self.buttons):
            name = button["name"]
            image = self.button_images[name][1] if self.selection_mode == "buttons" and self.selected_button == i else self.button_images[name][0]
            button_rect = image.get_rect(center=(screen_width * 0.5, button_y_start + i * button_spacing))
            screen.blit(image, button_rect)

        if self.saved:
            saved_text = "Tallennettu"
            saved_surf = font.render(saved_text, True, GREEN)
            saved_rect = saved_surf.get_rect(center=(screen_width // 2, 450))
            screen.blit(saved_surf, saved_rect)

        pygame.display.flip()

    def handle_event(self, event):
        action = self.controller.get_input(event)
        if action == "up":
            self.navigate_up()
        elif action == "down":
            self.navigate_down()
        elif action == "left":
            if self.selection_mode == "letters":
                self.current_slot = (self.current_slot - 1) % len(self.current_name)
        elif action == "right":
            if self.selection_mode == "letters":
                self.current_slot = (self.current_slot + 1) % len(self.current_name)
        elif action == "select":
            self.select()
        elif action == "back":
            self.menu_active = False

    def update(self):
        move = self.controller.get_movement()

        if self.selection_mode == "letters":
            if move.y < -0.5:
                self.change_letter(1)
            elif move.y > 0.5:
                self.change_letter(-1)
            if move.x < -0.5:
                self.current_slot = (self.current_slot - 1) % len(self.current_name)
            elif move.x > 0.5:
                self.current_slot = (self.current_slot + 1) % len(self.current_name)

        elif self.selection_mode == "buttons":
            if move.y < -0.5:
                self.selected_button = (self.selected_button - 1) % len(self.buttons)
            elif move.y > 0.5:
                self.selected_button = (self.selected_button + 1) % len(self.buttons)

    def navigate_up(self):
        if self.selection_mode == "letters":
            self.change_letter(1)
        elif self.selection_mode == "buttons":
            self.selected_button = (self.selected_button - 1) % len(self.buttons)

    def navigate_down(self):
        if self.selection_mode == "letters":
            self.change_letter(-1)
        elif self.selection_mode == "buttons":
            self.selected_button = (self.selected_button + 1) % len(self.buttons)

    def select(self):
        if self.selection_mode == "letters":
            self.selection_mode = "buttons"
            self.selected_button = 0
        elif self.selection_mode == "buttons":
            self.activate_button(self.selected_button)

    def change_letter(self, direction):
        current_index = LETTERS.index(self.current_name[self.current_slot])
        new_index = (current_index + direction) % len(LETTERS)
        self.current_name[self.current_slot] = LETTERS[new_index]

        # Jos kirjoittaa "DEL", tyhjennetään lista
        if "".join(self.current_name) == "DEL":
            self.clear_leaderboard()

    def confirm_name(self):
        self.save_name(self.score, self.time_elapsed)

    def save_name(self, score, time_elapsed):
        name = "".join(self.current_name)
        if not name:
            return

        GameData.save_data(name, score, time_elapsed)
        self.leaderboard = GameData.get_top_scores(10)
        save_leaderboard(self.leaderboard)

        self.saved = True

    def clear_leaderboard(self):
        self.leaderboard = []
        save_leaderboard(self.leaderboard)

    def activate_button(self, index):
        action = self.buttons[index]["action"]

        if action == "save":
            self.save_name(self.score, self.time_elapsed)
        elif action == "exit":
            self.menu_active = False
        elif action == "delete":
            if "".join(self.current_name) == "DEL":
                self.clear_leaderboard()
                self.saved = True