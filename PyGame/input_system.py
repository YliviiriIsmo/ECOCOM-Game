import pygame
import json
import os
import time
from game_data import GameData
import game_music

# Pygame alustus
pygame.init()

# Näytön koko
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Nimimerkin valinta")

game_music.play_music(game_music.MAIN_MENU_MUSIC)

# Värit
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

# Fontti
font = pygame.font.Font(None, 72)

# Tallennustiedosto
SAVE_FILE = "saves.json"

# Kirjaimet A-Z
LETTERS = [chr(i) for i in range(ord("A"), ord("Z") + 1)]

# Selvitetään kansion polku, jossa tämä tiedosto sijaitsee
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Lataa leaderboard
def load_leaderboard():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return json.load(file)
    return []

# Tallenna leaderboard
def save_leaderboard(data):
    with open(SAVE_FILE, "w") as file:
        json.dump(data, file, indent=4)

def load_sprite(filename, width, height):
    image = pygame.image.load(os.path.join(BASE_DIR, filename))
    return pygame.transform.scale(image, (int(width), int (height)))

# Nimen syöttö
class NameInput:
    def __init__(self, score, time_elapsed):
        self.score = score
        self.time_elapsed = time_elapsed
        self.current_slot = 0  # Aktiivinen kirjainslotti
        self.current_name = ["A", "A", "A"]  # Oletusnimi
        self.leaderboard = load_leaderboard()  # Lataa leaderboard
        self.saved = False  # Flag to indicate if the name has been saved

        # Navigointi
        self.menu_active = True
        self.selection_mode = "letters"  # "letters" tai "buttons"
        self.selected_button = 0

        # Painikkeet
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

        # Ohjain tuki
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def draw_text(self, text, x, y, color=BLACK):
        render = font.render(text, True, color)
        screen.blit(render, (x, y))

    def draw_ui(self):
        # Taustakuva
        screen_width, screen_height = screen.get_size()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
        game_over_image_path = os.path.join(BASE_DIR, "gameover.png")

        # Ladataan kuva absoluuttisella polulla
        if not os.path.isfile(game_over_image_path):
            raise FileNotFoundError(f"Tiedostoa ei löydy: {game_over_image_path}")

        game_over_image = pygame.image.load(game_over_image_path)
        game_over_image = pygame.transform.scale(game_over_image, (screen_width, screen_height))

        screen.blit(game_over_image, (0, 0))

         # Skaalaa otsikon paikka suhteessa näyttöön
        title_rect = font.render("Valitse nimimerkki", True, BLACK).get_rect(
            center=(screen_width * 0.5, screen_height * 0.2)
        )
        screen.blit(font.render("Valitse nimimerkki", True, BLACK), title_rect)

        # Piirrä nimimerkin kirjaimet dynaamisesti skaalattuna
        spacing = screen_width * 0.08  # Skaalautuva etäisyys
        for i, letter in enumerate(self.current_name):
            color = GRAY if self.selection_mode == "letters" and i == self.current_slot else BLACK
            letter_surf = font.render(letter, True, color)
            letter_rect = letter_surf.get_rect(center=(screen_width * 0.5 + (i - 1) * spacing, screen_height * 0.3))
            screen.blit(letter_surf, letter_rect)

        # Piirrä painikkeet suhteellisesti näytön kokoon
        button_y_start = screen_height * 0.51  # Aloituskorkeus
        button_spacing = screen_height * 0.17  # Väli painikkeiden välillä

        for i, button in enumerate(self.buttons):
            name = button["name"]
            image = self.button_images[name][1] if self.selection_mode == "buttons" and self.selected_button == i else self.button_images[name][0]
            button_rect = image.get_rect(center=(screen_width * 0.5, button_y_start + i * button_spacing))
            screen.blit(image, button_rect)

        # Näytä "Tallennettu" viesti, jos nimi on tallennettu
        if self.saved:
            saved_text = "Tallennettu"
            saved_surf = font.render(saved_text, True, GREEN)
            saved_rect = saved_surf.get_rect(center=(screen_width // 2, 450))
            screen.blit(saved_surf, saved_rect)

        pygame.display.flip()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:  # Näppäimistön käsittely
            self.handle_keyboard_input(event)

        elif event.type == pygame.JOYBUTTONDOWN:  # Ohjaimen napit
            self.handle_joystick_input(event)

        elif event.type == pygame.JOYHATMOTION:  # Ohjaimen D-Pad
            self.handle_dpad_input(event)

        elif event.type == pygame.JOYAXISMOTION: # Ohjaimen analogitikku
            self.handle_joystick_axis(event)

    def handle_keyboard_input(self, event):
        if self.selection_mode == "letters":
            if event.key in (pygame.K_w, pygame.K_UP):  # Vaihda kirjain ylöspäin
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.change_letter(1)
            elif event.key in (pygame.K_s, pygame.K_DOWN):  # Vaihda kirjain alaspäin
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.change_letter(-1)
            elif event.key in (pygame.K_a, pygame.K_LEFT):  # Siirry vasemmalle
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.current_slot = (self.current_slot - 1) % 3
            elif event.key in (pygame.K_d, pygame.K_RIGHT):  # Siirry oikealle
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.current_slot = (self.current_slot + 1) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):  # Vahvista nimi
                #game_music.play_sound("button_select")  # Ääniefekti
                self.confirm_name()
            elif event.key in (pygame.K_TAB, pygame.K_e):  # Siirry painikkeisiin
                self.selection_mode = "buttons"
                self.selected_button = 0

        elif self.selection_mode == "buttons":
            if event.key in (pygame.K_w, pygame.K_UP):  # Ylös painikkeissa
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.selected_button = (self.selected_button - 1) % len(self.buttons)
            elif event.key in (pygame.K_s, pygame.K_DOWN):  # Alas painikkeissa
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.selected_button = (self.selected_button + 1) % len(self.buttons)
            elif event.key in (pygame.K_a, pygame.K_LEFT):  # Takaisin kirjaimiin
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.selection_mode = "letters"
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):  # Aktivoi painike
                #game_music.play_sound("button_select")  # Ääniefekti
                self.activate_button(self.selected_button)

    def handle_joystick_input(self, event):
        #Navikointi ohjaimella sen ristiohjaimen ja nappien kautta
        if event.type == pygame.JOYAXISMOTION:  # Analogitikun liike
            if abs(event.value) > 0.5:  # Suodatetaan pienet liikkeet
                if event.axis == 1:  # Y-akseli (ylös/alas)
                    if self.selection_mode == "letters":
                        #game_music.play_sound("button_hover")  # Ääniefekti
                        self.change_letter(-1 if event.value > 0 else 1)
                    elif self.selection_mode == "buttons":
                        #game_music.play_sound("button_select")  # Ääniefekti
                        self.selected_button = (self.selected_button + (1 if event.value > 0 else -1)) % len(self.buttons)

                elif event.axis == 0:  # X-akseli (vasen/oikea)
                    if self.selection_mode == "letters":
                        #game_music.play_sound("button_hover")  # Ääniefekti
                        self.current_slot = (self.current_slot + (1 if event.value > 0 else -1)) % 3
                    else:
                        self.selection_mode = "letters" if event.value < 0 else "buttons"
        
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # A-nappi
                if self.selection_mode == "letters":  
                    #game_music.play_sound("button_select")  # Ääniefekti
                    self.selection_mode = "buttons"  # Siirrytään painikkeisiin
                    self.selected_button = 0  
                elif self.selection_mode == "buttons":
                    self.activate_button(self.selected_button)  # Aktivoi valittu painike

            elif event.button == 1:  # B-nappi (takaisin)
                if self.selection_mode == "buttons":
                    #game_music.play_sound("button_select")  # Ääniefekti
                    self.selection_mode = "letters"  # Palaa kirjainvalintaan

    def handle_dpad_input(self, event):
        x, y = event.value  # D-Pad suunta

        if self.selection_mode == "letters":
            if y == 1:  # Ylös (lisää kirjain)
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.change_letter(1)
            elif y == -1:  # Alas (vähennä kirjain)
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.change_letter(-1)
            elif x == -1:  # Vasemmalle (siirry kirjain sloteissa)
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.current_slot = (self.current_slot - 1) % 3
            elif x == 1:  # Oikealle
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.current_slot = (self.current_slot + 1) % 3

        elif self.selection_mode == "buttons":
            if y == 1:  # Ylös (vaihda painiketta)
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.selected_button = (self.selected_button - 1) % len(self.buttons)
            elif y == -1:  # Alas
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.selected_button = (self.selected_button + 1) % len(self.buttons)
            elif x == -1:  # Vasemmalle (palaa kirjain valintaan)
                #game_music.play_sound("button_hover")  # Ääniefekti
                self.selection_mode = "letters"

    def handle_joystick_axis(self, event):
        if abs(event.value) < 0.5:
            return  # Suodatus pienille liikkeille

        if event.axis == 1:  # Y-akseli (ylös/alas)
            if event.value < 0:  # Ylös
                if self.selection_mode == "letters":
                    #game_music.play_sound("button_hover")  # Ääniefekti
                    self.change_letter(1)
                elif self.selection_mode == "buttons":
                    #game_music.play_sound("button_hover")  # Ääniefekti
                    self.selected_button = (self.selected_button - 1) % len(self.buttons)
            else:  # Alas
                if self.selection_mode == "letters":
                    #game_music.play_sound("button_hover")  # Ääniefekti
                    self.change_letter(-1)
                elif self.selection_mode == "buttons":
                    #game_music.play_sound("button_hover")  # Ääniefekti
                    self.selected_button = (self.selected_button + 1) % len(self.buttons)

        elif event.axis == 0:  # X-akseli (vasen/oikea)
            if event.value < 0:  # Vasemmalle
                if self.selection_mode == "buttons":
                    #game_music.play_sound("button_hover")  # Ääniefekti
                    self.selection_mode = "letters"
                else:
                    self.current_slot = (self.current_slot - 1) % 3
            else:  # Oikealle
                if self.selection_mode == "letters":
                    #game_music.play_sound("button_hover")  # Ääniefekti
                    self.current_slot = (self.current_slot + 1) % 3
                else:
                    self.selection_mode = "buttons"

    def change_letter(self, direction):
        current_index = LETTERS.index(self.current_name[self.current_slot])
        new_index = (current_index + direction) % len(LETTERS)
        self.current_name[self.current_slot] = LETTERS[new_index]

    def confirm_name(self):
        self.save_name(self.score, self.time_elapsed)

    def save_name(self, score, time_elapsed):
        """Tallentaa pelaajan nimen, oikean pistemäärän ja ajan"""
        name = "".join(self.current_name)

        if not name:
            return  # Älä tallenna tyhjää nimeä

        # Tallennetaan oikeat pisteet ja aika
        GameData.save_data(name, self.score, self.time_elapsed)

        # Päivitetään leaderboard-lista
        self.leaderboard = GameData.get_top_scores(10)
        # Tallennetaan leaderboard tiedostoon
        save_leaderboard(self.leaderboard)

        # Asetetaan tallennusviesti näkyviin
        self.saved = True

    def activate_button(self, index):
        action = self.buttons[index]["action"]
        if action == "save":
            #game_music.play_sound("button_select")  # Ääniefekti
            self.save_name(self.score, self.time_elapsed)

        elif action == "exit":
            #game_music.play_sound("button_select")  # Ääniefekti
            self.menu_active = False  # Poistu päävalikkoon
        elif action == "delete":
            if "".join(self.current_name) == "DEL": #nimimerkki poistamiselle
                self.leaderboard = []  # Tyhjennä lista
                save_leaderboard(self.leaderboard)
                self.saved = True  # Näytä tallennusviesti            
                #game_music.play_sound("button_select")  # Ääniefekti 