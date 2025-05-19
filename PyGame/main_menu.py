import pygame
import os
import time
from game_data import GameData 
import game_music
from controller import Controller

class MainMenu:
    def __init__(self, screen, controller=None):
        self.screen = screen
        self.controller = controller or Controller() # Alustetaan ohjain
        self.controller.reload_config()  # Lataa ohjainkonfiguraatio uudelleen
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.SCALE_X = self.WIDTH / 1920
        self.SCALE_Y = self.HEIGHT / 1080

        # Skaalattu fontti
        self.font = pygame.font.Font(None, int(40 * self.SCALE_Y))

        # Alustetaan attribuutit
        self.showing_logo = False  # Alustetaan showing_logo
        self.start_time = 0  # Alustetaan start_time
        self.popup = None  # Alustetaan popup
        self.popup_content = None  # Alustetaan popup_content

        game_music.play_music(game_music.MAIN_MENU_MUSIC)

        # Selvitetään kansion polku, jossa tämä tiedosto sijaitsee
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # Lataa taustakuva
        self.background = pygame.image.load(os.path.join(BASE_DIR, "background.png"))
        self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))  # Skaalaa näyttöön sopivaksi

        self.start_game_logo = pygame.image.load(os.path.join(BASE_DIR, "game_start_logo.png"))
        self.start_game_logo = pygame.transform.scale(self.start_game_logo, (self.WIDTH, self.HEIGHT))

        def load_sprite(filename, width_ratio, height_ratio):
            width = int(self.WIDTH * width_ratio)
            height = int(self.HEIGHT * height_ratio)
            image = pygame.image.load(os.path.join(BASE_DIR, filename))
            return pygame.transform.scale(image, (width, height))
        
        # Painikkeiden sijainti suhteessa näytön kokoon
        self.play_button_rect = pygame.Rect(
            self.WIDTH * 0.4, self.HEIGHT * 0.4,
            200 * self.SCALE_X, 80 * self.SCALE_Y
        )

        # Painikkeiden asettelu
        self.margin = 100
        self.button_width = 503.5
        self.button_height = 133

        self.button_rects = []
        self.selected_index = 0  # Valittu painike

        # Ladataan painikkeiden kuvat
        self.button_images = {
            "Pelaa": (load_sprite("play_button.png", 0.3, 0.1),  # 30% leveys, 10% korkeus
                    load_sprite("play_button_hover.png", 0.3, 0.1)),
            "Ohjeet": (load_sprite("instructions_button.png", 0.3, 0.1),
                    load_sprite("instructions_button_hover.png", 0.3, 0.1)),
            "Ennätys": (load_sprite("leaderboard_button.png", 0.3, 0.1),
                        load_sprite("leaderboard_button_hover.png", 0.3, 0.1)),
            "Tekijä": (load_sprite("credits_button.png", 0.3, 0.1),
                    load_sprite("credits_button_hover.png", 0.3, 0.1)),
            "Ohjainasetukset": (load_sprite("controller_config_button.png", 0.3, 0.1),  # Uusi painike
                    load_sprite("controller_config_button_hover.png", 0.3, 0.1)),
            "Sulje": (load_sprite("quit_button.png", 0.3, 0.1),
                    load_sprite("quit_button_hover.png", 0.3, 0.1)),
        }

        # Painikkeiden asetukset "Pelaa", self.start_game
        self.buttons = [
            ("Pelaa", self.start_game),
            ("Ohjeet", self.toggle_instructions),
            ("Ennätys", self.toggle_leaderboard),
            ("Tekijä", self.toggle_credits),
            ("Ohjainasetukset", self.open_controller_config),  # Uusi painike
            ("Sulje", self.quit_game),
        ]

        # Skaalaa painikkeiden mitat suhteessa näytön kokoon
        self.button_width = self.WIDTH * 0.3  # 30% näytön leveydestä
        self.button_height = self.HEIGHT * 0.1  # 10% näytön korkeudesta

        # Lasketaan painikkeiden paikat suhteessa näytön kokoon
        for i, (text, _) in enumerate(self.buttons):
            x = self.WIDTH * 0.68  # 70% näytön leveydestä
            y = self.margin + i * (self.button_height + self.HEIGHT * 0.03)  # 3% näytön korkeudesta marginaalina
            self.button_rects.append(pygame.Rect(x, y, self.button_width, self.button_height))

        # Skaalaa popup-kuvat suhteessa näytön kokoon
        self.popup_image = load_sprite("popup_image.png", 0.6, 0.6)  # 80% leveys, 70% korkeus
        self.leaderboard_image = load_sprite("leaderboardImage.png", 0.8, 0.7)  # Sama suhteellinen koko

        # Skaalaa popup-kuvan koko suhteessa näytön kokoon
        popup_width = self.WIDTH * 0.55  # 60% näytön leveydestä
        popup_height = self.HEIGHT * 0.6  # 70% näytön korkeudesta

        # Siirretään popup vasemmalle, jotta se ei mene painikkeiden päälle
        popup_x = (self.WIDTH - popup_width) // 2  # Keskitetään vaakasuunnassa
        if popup_x + popup_width > self.WIDTH * 0.68:  # Jos popup menee painikkeiden päälle
            popup_x = int(self.WIDTH * 0.05)  # Siirretään vasemmalle

        popup_y = (self.HEIGHT - popup_height) // 1.5  # Keskitetään pystysuunnassa

        self.popup_rect = pygame.Rect(
            popup_x,
            popup_y,
            popup_width,
            popup_height
        )

        # Skaalaa popup-kuvat
        self.popup_image = pygame.transform.scale(self.popup_image, (int(popup_width), int(popup_height)))
        self.leaderboard_image = pygame.transform.scale(self.leaderboard_image, (int(popup_width), int(popup_height)))

        # Estetään tuplapainallukset
        self.last_input_time = 0  

        # Ohjain
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def draw(self):
        """Piirtää päävalikon"""
        self.screen.blit(self.background, (0, 0))

         # Alustetaan fontit
        title_font = pygame.font.Font(pygame.font.match_font('arial'), 36)
        text_font = pygame.font.Font(pygame.font.match_font('arial'), 28)

        # Piirretään painikkeet
        mouse_pos = pygame.mouse.get_pos()
        for i, (text, _) in enumerate(self.buttons):
            # Valitaan oikea kuva (normaali tai hover)
            if self.button_rects[i].collidepoint(mouse_pos) or i == self.selected_index:
                button_image = self.button_images[text][1]  # Hover-kuva
            else:
                button_image = self.button_images[text][0]  # Normaali kuva

            # Piirretään kuva painikkeen kohdalle
            self.screen.blit(button_image, (self.button_rects[i].x, self.button_rects[i].y))

        # Näytetään koko ruudun kokoinen logo, jos peli on käynnistymässä
            if self.showing_logo:
                self.screen.blit(self.start_game_logo, (0, 0))  # Piirtää koko ruutuun

        # Näytetään pop-up, jos sellainen on
        if self.popup:
            if self.popup == "ennätys":
                # Piirretään leaderboard-kuva
                self.screen.blit(self.leaderboard_image, self.popup_rect.topleft)

                # Sarakkeiden x-koordinaatit suhteessa popupin kokoon
                x_positions = [
                    self.popup_rect.x + int(self.popup_rect.width * 0.1),  # Sija
                    self.popup_rect.x + int(self.popup_rect.width * 0.3),  # Nimi
                    self.popup_rect.x + int(self.popup_rect.width * 0.6),  # Pisteet
                    self.popup_rect.x + int(self.popup_rect.width * 0.8)  # Aika
                ]

                # Skaalattu fonttikoko suhteessa popupin korkeuteen
                text_font_size = int(self.popup_rect.height * 0.05)  # 5% popupin korkeudesta
                text_font = pygame.font.Font(pygame.font.match_font('arial'), text_font_size)

                # Piirretään leaderboardin otsikot ja tulokset
                for idx, row in enumerate(self.popup_content):
                    color = (0, 0, 0) if idx == 0 else (0, 0, 0)  # Otsikot ja tulokset mustana
                    text_y = self.popup_rect.y + int(self.popup_rect.height * 0.15) + idx * int(self.popup_rect.height * 0.07)

                    for col, text in enumerate(row):
                        text_surf = text_font.render(str(text), True, color)
                        self.screen.blit(text_surf, (x_positions[col], text_y))
            else:
                # Piirretään popup-kuva
                self.screen.blit(self.popup_image, self.popup_rect.topleft)

                # Skaalattu fonttikoko suhteessa popupin korkeuteen
                text_font_size = int(self.popup_rect.height * 0.05)  # 5% popupin korkeudesta
                text_font = pygame.font.Font(pygame.font.match_font('arial'), text_font_size)

                # Piirretään tekstirivit suhteessa popupin kokoon
                for idx, line in enumerate(self.popup_content):
                    text_surf = text_font.render(line, True, (0, 0, 0))
                    text_x = self.popup_rect.centerx - text_surf.get_width() // 2  # Keskitetään teksti vaakasuunnassa
                    text_y = self.popup_rect.y + int(self.popup_rect.height * 0.15) + idx * int(self.popup_rect.height * 0.07)
                    self.screen.blit(text_surf, (text_x, text_y))

            # Varmistetaan, että title_font ja text_font ovat aina alustettuja
            title_font = pygame.font.Font(pygame.font.match_font('arial'), 36)
            text_font = pygame.font.Font(pygame.font.match_font('arial'), 28)

            # Asetetaan otsikkoteksti
            title = None  # Alustetaan tyhjällä arvolla

            # Asetetaan otsikkoteksti
            if self.popup == "ennätys":
                title = title_font.render("TOP 10 ENNÄTYKSET", True, (0, 0, 0))
            elif self.popup == "ohjeet":
                title = title_font.render("PELIN OHJEET", True, (0, 0, 0))
            elif self.popup == "tekijä":
                title = title_font.render("PELIN TEKIJÄ", True, (0, 0, 0))
            else:
                title = None

            # Piirretään otsikko keskitetysti popupin sisään
            if title:
                title_x = self.popup_rect.centerx - title.get_width() // 2
                title_y = self.popup_rect.y + self.popup_rect.height * 0.07  # 5% popupin korkeudesta marginaalina
                self.screen.blit(title, (title_x, title_y))

            # Näytetään koko ruudun kokoinen logo, jos peli on käynnistymässä
            if self.showing_logo:
                self.screen.blit(self.start_game_logo, (0, 0))  # Piirtää koko ruutuun

        pygame.display.flip()

    def update(self, events):
        # Jos logo näkyy, odotetaan ja sitten aloitetaan peli
        if self.showing_logo:
            if time.time() - self.start_time > 2:
                self.showing_logo = False
                self.start_game_now()
            return
        
        # päivitä inputit
        self.selected_index = self.controller.handle_menu_navigation(self.selected_index, self.buttons, events)

        if self.controller.confirm_selection():
            _, action = self.buttons[self.selected_index]
            action()

        if self.controller.esc_pressed():
            self.popup = None

    def start_game(self):
        """ Näyttää logon hetkeksi ja sitten aloittaa pelin """
        self.showing_logo = True
        self.start_time = time.time()

    def start_game_now(self):
        """ Käynnistää peli-ikkunan PlayerControllerilla """
        from PlayerController import run_game
        run_game(self.screen, self.controller)

    def toggle_instructions(self):
        """ Näyttää tai piilottaa ohjeet """
        if self.popup == "ohjeet":
            self.popup = None
        else:
            self.popup = "ohjeet"
            self.popup_content = [
                "Liiku: Ohjainsauvalla / WASD-nuolilla",
                "Tavoite: Kerää tietokoneenosia ja saa pisteitä!",
                "Vältä vääriä esineitä omenia ja peliohjaimia, sekä hiiriä!",
                "",
                "Onnea peliin!"
            ]

    def toggle_leaderboard(self):
        """ Näyttää tai piilottaa leaderboardin """
        if self.popup == "ennätys":
            self.popup = None
        else:
            self.popup = "ennätys"

            # Haetaan top 10 -tulokset
            top_scores = GameData.get_top_scores(10)

            # Tallennetaan sarakkeiden otsikot ja itse tiedot
            self.popup_content = [("Sija", "Nimi", "Pisteet", "Aika")]  # Otsikkorivi
            self.popup_content += [
                (str(i+1), entry["name"], str(entry["score"]), f"{entry['time_elapsed']}s")
                for i, entry in enumerate(top_scores)
            ]

    def toggle_credits(self):
        """ Näyttää tai piilottaa tekijän tiedot """
        if self.popup == "tekijä":
            self.popup = None
        else:
            self.popup = "tekijä"
            self.popup_content = [
                "Tämän pelin on kehittänyt:",
                "Ismo Yliviiri.",
                "2025.",
                "",
                "Käytetyt ohjelmat:",
                "Ohjelmoitu Pythonilla ja Pygamella.",
                "2D kuvat tehty FireAlpaca ja Canva -ohjelmalla.",
                "Musiikit tehty Suno Pro -ohjelmalla.",
                "Ääniefektit tehty elevenlabs.io -ohjelmalla.",
                "",
                "Kiitos pelaamisesta!"
            ]
    def open_controller_config(self):
        import controller_config
        controller_config.run(self.screen)
        self.controller.reload_config()  # Lataa uudet asetukset tiedostosta

    def reset_state(self):
        """Nollaa valikon tilan, kun peli päättyy ja palataan takaisin"""
        self.showing_logo = False
        self.popup = None
        self.popup_content = None
        self.selected_index = 0  # Nollaa valittu painike
        self.last_input_time = 0  # Nollaa syötteen aikaleima
        self.controller.reload_config()  # Lataa ohjainkonfiguraatio uudelleen

    def quit_game(self):
        """ Sulkee pelin """
        pygame.quit()
        exit()