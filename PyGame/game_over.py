import pygame
import os
import sys
from game_data import GameData  # Tuodaan GameData-luokka käyttöön
from input_system import NameInput  # Tuodaan NameInput-luokka käyttöön
import game_music

class GameOver:
    def __init__(self, screen, score, time_elapsed):
        self.screen = screen
        self.score = score
        self.time_elapsed = time_elapsed
        self.font = pygame.font.Font(None, 36)

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
            {"text": "Ei", "action": "skip"},
        ]

        self.selected_index = 0  # Aluksi "Kyllä" valittuna

        # Ohjain (Gamepad) tuki
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def handle_input(self, event):
        """Käsittelee näppäimistön, ohjaimen ja joystickin syötteet"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                #game_music.play_sound("button_hover")  # Ääniefekti ylös

            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                #game_music.play_sound("button_hover")  # Ääniefekti alas

            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                #game_music.play_sound("button_select")  # Ääniefekti valinnalle
                return self.buttons[self.selected_index]["action"]

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # A-nappi (hyväksy)
                #game_music.play_sound("button_select")  # Ääniefekti valinnalle
                return self.buttons[self.selected_index]["action"]
            elif event.button == 1:  # B-nappi (peruuta, valitaan "Ei")
                #game_music.play_sound("button_select")  # Ääniefekti peruutukselle
                return "skip"

        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:  # Vain pystysuuntainen liike
                if event.value < -0.5:  # Ylös
                    self.selected_index = (self.selected_index - 1) % len(self.buttons)
                    #game_music.play_sound("button_hover")  # Ääniefekti ylös
                elif event.value > 0.5:  # Alas
                    self.selected_index = (self.selected_index + 1) % len(self.buttons)
                    #game_music.play_sound("button_hover")  # Ääniefekti alas

        elif event.type == pygame.JOYHATMOTION:
            x, y = event.value
            if y == 1:  # D-Pad ylös
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                #game_music.play_sound("button_hover")  # Ääniefekti ylös
            elif y == -1:  # D-Pad alas
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                #game_music.play_sound("button_hover")  # Ääniefekti alas


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
                if action:
                    return action  # Palauttaa "save" tai "skip"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if self.button_rects[i].collidepoint(pygame.mouse.get_pos()):  # Hiiren klikkaus
                            #game_music.play_sound("button_select")  # Ääniefekti
                            return button["action"]

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
                    name_input.handle_input(event)

            else:
                running = False  # Sulje, kun nimi on syötetty

        player_name = "".join(name_input.current_name)  # Hae nimi NameInputista
        if player_name:  # Varmistetaan, että nimi ei ole tyhjä
            # Tallennetaan oikea pistemäärä ja aika!
            GameData.save_data(player_name, self.score, self.time_elapsed)

        return "done"


    def show_screen(self):
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

        def load_sprite(filename, width, height):
            image = pygame.image.load(os.path.join(BASE_DIR, filename))
            return pygame.transform.scale(image, (int(width), int(height)))

        button_width, button_height = 503.5, 133

        button_images = {
            "Uusi peli": (load_sprite("play_button.png", button_width, button_height),
                          load_sprite("play_button_hover.png", button_width, button_height)),
            "Päävalikko": (load_sprite("main_menu.png", button_width, button_height),
                           load_sprite("main_menu_hover.png", button_width, button_height)),
            "Lopeta": (load_sprite("quit_button.png", button_width, button_height),
                       load_sprite("quit_button_hover.png", button_width, button_height)),
        }

        buttons = [
            {"text": "Uusi peli", "action": "restart"},
            {"text": "Päävalikko", "action": "menu"},
            {"text": "Lopeta", "action": "quit"},
        ]

        button_width, button_height = 503.5, 133
        button_rects = [pygame.Rect((screen_width - button_width) // 2, 150 + i * (button_height + 40),
                                    button_width, button_height) for i in range(len(buttons))]

        selected_index = 0
        last_axis_move = 0  # Estää akselin toistuvan scrollauksen

        running = True
        while running:
            self.screen.fill((0, 0, 0))
            self.screen.blit(game_over_image, (0, 0))

            # Piirrä painikkeet
            for i, button in enumerate(buttons):
                button_image = button_images[button["text"]][1] if i == selected_index else button_images[button["text"]][0]
                self.screen.blit(button_image, (button_rects[i].x, button_rects[i].y))

            pygame.display.flip()

            # Tapahtumien käsittely
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        selected_index = (selected_index - 1) % len(buttons)
                        #game_music.play_sound("button_hover")  # Ääniefekti
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected_index = (selected_index + 1) % len(buttons)
                        #game_music.play_sound("button_hover")  # Ääniefekti
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        #game_music.play_sound("button_select")  # Ääniefekti
                        return buttons[selected_index]["action"]
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A-nappi (valitse)
                        #game_music.play_sound("button_select")  # Ääniefekti
                        return buttons[selected_index]["action"]
                    elif event.button == 1:  # B-nappi (peruuta, oletuksena Päävalikko)
                        #game_music.play_sound("button_select")  # Ääniefekti
                        return "menu"
                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis == 1:  # Vain pystysuuntainen liike
                        if event.value < -0.5 and last_axis_move >= -0.5:  # Ylös
                            selected_index = (selected_index - 1) % len(buttons)
                            #game_music.play_sound("button_hover")  # Ääniefekti
                        elif event.value > 0.5 and last_axis_move <= 0.5:  # Alas
                            selected_index = (selected_index + 1) % len(buttons)
                            #game_music.play_sound("button_hover")  # Ääniefekti
                        last_axis_move = event.value
                elif event.type == pygame.JOYHATMOTION:
                    x, y = event.value
                    if y == 1:  # D-Pad ylös
                        selected_index = (selected_index - 1) % len(buttons)
                        #game_music.play_sound("button_hover")  # Ääniefekti
                    elif y == -1:  # D-Pad alas
                        selected_index = (selected_index + 1) % len(buttons)
                        #game_music.play_sound("button_hover")  # Ääniefekti

            pygame.time.delay(100)