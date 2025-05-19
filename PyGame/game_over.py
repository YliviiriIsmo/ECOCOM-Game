import pygame
import os
import sys
from game_data import GameData  # Tuodaan GameData-luokka käyttöön
from input_system import NameInput  # Tuodaan NameInput-luokka käyttöön
import game_music
from controller import Controller  # Tuodaan Controller-luokka käyttöön

class GameOver:
    def __init__(self, screen, score, time_elapsed):
        self.screen = screen
        self.score = score
        self.time_elapsed = time_elapsed
        self.font = pygame.font.Font(None, 36)
        self.selected_index = 0
        self.controller = Controller()

        game_music.play_music(game_music.GAME_OVER_MUSIC)

        # Selvitetään kansion polku, jossa tämä tiedosto sijaitsee
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        def load_sprite(filename, width, height):
            image = pygame.image.load(os.path.join(BASE_DIR, filename))
            return pygame.transform.scale(image, (int(width), int(height)))

        # Painikkeiden mitat
        self.button_width = 503.5
        self.button_height = 133

        # Ladataan painikkeiden kuvat
        self.button_images = {
            "Kyllä": (load_sprite("kylla.png", self.button_width, self.button_height),
                      load_sprite("kylla_hover.png", self.button_width, self.button_height)),
            "Ei": (load_sprite("ei.png", self.button_width, self.button_height),
                   load_sprite("ei_hover.png", self.button_width, self.button_height)),
        }

        # Painikkeiden sijainnit
        screen_width, screen_height = screen.get_size()
        self.button_rects = [
            pygame.Rect((screen_width - self.button_width) // 2, 300, self.button_width, self.button_height),
            pygame.Rect((screen_width - self.button_width) // 2, 450, self.button_width, self.button_height),
        ]

        self.buttons = [
            {"text": "Kyllä", "action": "save"},
            {"text": "Ei", "action": "menu"},
        ]

    def handle_input(self, event):
        action = self.controller.get_input(event)

        if action == "up":
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
            #game_music.play_sound("button_hover")

        elif action == "down":
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            #game_music.play_sound("button_hover")

        elif action == "select":
            #game_music.play_sound("button_select")
            return self.buttons[self.selected_index]["action"]

        elif action == "back":
            return "menu"

        # Hiirellä klikkaus pysyy erikseen:
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.buttons):
                if self.button_rects[i].collidepoint(pygame.mouse.get_pos()):
                    return self.buttons[i]["action"]

    def ask_to_save(self):
        """Näyttää Game Over -ruudun"""
        screen_width, screen_height = self.screen.get_size()

        # Selvitetään tiedoston absoluuttinen polku
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
        game_over_image_path = os.path.join(BASE_DIR, "gameover.png")

        # Ladataan kuva absoluuttisella polulla
        if not os.path.isfile(game_over_image_path):
            raise FileNotFoundError(f"Tiedostoa ei löydy: {game_over_image_path}")

        game_over_image = pygame.image.load(game_over_image_path)
        game_over_image = pygame.transform.scale(game_over_image, (screen_width, screen_height))

        """Kysyy pelaajalta, haluaako hän tallentaa tuloksensa."""
        running = True
        while running:
            self.screen.blit(game_over_image, (0, 0))  # Näytä Game Over -kuva taustalla

            # Näytä teksti
            text = self.font.render("Haluatko tallentaa tuloksesi?", True, (0, 0, 0))
            self.screen.blit(text, (screen_width // 2 - 200, 200))

            # Piirrä painikkeet
            for i, button in enumerate(self.buttons):
                image = self.button_images[button["text"]][1] if i == self.selected_index else self.button_images[button["text"]][0]
                self.screen.blit(image, (self.button_rects[i].x, self.button_rects[i].y))


            pygame.display.flip()

            # Tapahtumien käsittely
            for event in pygame.event.get():
                action = self.handle_input(event)
                if action == "save":
                    return self.save_game()  # Tallennetaan ja palataan päävalikkoon
                elif action == "menu":
                    return "menu"  # Palataan päävalikkoon

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, button in enumerate(self.buttons):
                        if self.button_rects[i].collidepoint(pygame.mouse.get_pos()):
                            return self.buttons[i]["action"]

            pygame.time.delay(100)  # Pieni viive välttää liikaa liikettä

        return None

    def save_game(self):
        """Tallentaa pelaajan oikeat pisteet ja ajan"""
        name_input = NameInput(self.score, self.time_elapsed)
        running = True

        while running:
            if name_input.menu_active:
                name_input.draw_ui()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    name_input.handle_event(event)
            else:
                running = False  # Sulje, kun nimi on syötetty

        player_name = "".join(name_input.current_name)  # Hae nimi NameInputista
        if player_name:  # Varmistetaan, että nimi ei ole tyhjä
            # Tallennetaan oikea pistemäärä ja aika!
            GameData.save_data(player_name, self.score, self.time_elapsed)

        return "menu"  # Palautetaan päävalikkoon, kun tallennus on valmis
    
    def game_over_flow(self):
        """Hallinnoi Game Over -tilaa."""
        action = self.ask_to_save()
        if action == "menu":
            self.reset_state()  # Nollaa valikon tila
            return self.show_main_menu()  # Siirry päävalikkoon
        elif action == "restart":
            return self.restart_game()  # Käynnistä peli uudelleen