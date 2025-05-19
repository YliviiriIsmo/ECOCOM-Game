import pygame
import os
#import game_music

class GameUI:
    def __init__(self, screen, score_display):
        self.screen = screen
        self.score_display = score_display  # Tallennetaan score_display
        self.items_collected = {}  # Alustetaan kerättyjen esineiden sanakirja
        self.pop_effects = {}  # Seurataan pop-animaatioita (esine: aikaleima)
        self.pop_duration = 200  # Pop-animaation kesto millisekunneissa

        self.WIDTH, self.HEIGHT = screen.get_size()

        # Kansioiden sijainnit
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        UI_DIR = os.path.join(BASE_DIR)
        COLLECTIBLES_DIR = os.path.join(BASE_DIR)

        # Ladataan UI-taustakuva
        self.ui_background = pygame.image.load(os.path.join(UI_DIR, "ui-background.png"))
        self.ui_background = pygame.transform.scale(self.ui_background, (1000, 200))

        # UI:n sijainti (alas keskelle)
        self.ui_x = (self.WIDTH - self.ui_background.get_width()) // 2
        self.ui_y = self.HEIGHT - self.ui_background.get_height() - 10

        # Ladataan sydänkuva
        self.heart_image = pygame.image.load(os.path.join(UI_DIR, "heart.png"))
        self.heart_image = pygame.transform.scale(self.heart_image, (36, 36))

        # Esineiden nimet määritelty erikseen
        self.ITEM_NAMES = {
            "1.cpu.png": "Prosessori",
            "2.emolevy.png": "Emolevy",
            "3.ram_muisti.png": "RAM Muisti",
            "4.kovalevy.png": "Kovalevy",
            "5.PSU.png": "Virtalahde",
            "6.naytonohjain.png": "Naytonohjain",
            "7.tuuletin.png": "Tuuletin",
            "8.heatsink.png": "Jaahdytyssiili",
            "9.syotto-tulostus.png": "Oheislaitteet",
            "10.verkkosovitin.png": "Verkkosovitin"
        }

        # Ladataan kaikki kerättävät esineiden kuvat - täytyy käyttää samoja kuin EnemySpawnerissa
        self.item_images = {}
        self.collected_counts = {name: 0 for name in self.ITEM_NAMES.values()}  # Tallentaa montako esinettä on kerätty
        for filename, item_name in self.ITEM_NAMES.items():
            item_path = os.path.join(COLLECTIBLES_DIR, filename)
            image = pygame.image.load(item_path)
            self.item_images[item_name] = pygame.transform.scale(image, (80, 80))

        # UI-asetukset
        self.item_positions = [(self.ui_x + 30 + i * 96, self.ui_y + 80) for i in range(len(self.item_images))]  # Esineiden paikat  
        self.heart_positions = [(self.ui_x + 24.5 + i * 36.5, self.ui_y + 19.5) for i in range(5)]  # Sydämien paikat  

        self.font = pygame.font.Font(None, 30)  # Fontti kerättävien lukumäärien näyttämiseen
        self.lives = 5  # Alussa 5 elämää

    def add_item(self, item_name):
        """Lisää kerätty esine UI:hin ja päivittää lukumäärän näkyviin."""
        if item_name in self.collected_counts:
            self.collected_counts[item_name] += 1  # Kasvatetaan oikeaa lukumäärää
        else:
            self.collected_counts[item_name] = 1  # Luodaan, jos ei ole vielä

        # Käynnistä pop-efekti
        self.pop_effects[item_name] = pygame.time.get_ticks()

        self.draw()  # Pakota piirtämään uudelleen

    def update_ui(self):
        """Päivittää UI:n tekstit"""
        self.text_surfaces = {}
        for item, count in self.collected_counts.items():
            self.text_surfaces[item] = self.font.render(f"{item}: {count}", True, (255, 255, 255))

    def remove_life(self):
        """Vähentää elämää (sydämet vähenevät)."""
        if self.lives > 0:
            self.lives -= 1
            #game_music.play_sound("damage")  # Pelaaja ottaa vahinkoa

    def draw(self):
        """Piirtää UI:n näytölle ja pakottaa sen päivittymään."""
        self.screen.blit(self.ui_background, (self.ui_x, self.ui_y))

        # Piirretään sydämet
        for i in range(self.lives):
            self.screen.blit(self.heart_image, self.heart_positions[i])
        
        # Piirretään kerättävät esineet
        for i, item_name in enumerate(self.item_images.keys()):
            if i < len(self.item_positions):
                x, y = self.item_positions[i]
                original_image = self.item_images[item_name]

                # Oletus skaalaus
                scale = 1.0

                # Jos esineellä on pop-animaatio, suurennetaan hetkeksi
                if item_name in self.pop_effects:
                    elapsed = pygame.time.get_ticks() - self.pop_effects[item_name]
                    if elapsed < self.pop_duration:
                        scale = 1.2 if elapsed < self.pop_duration / 1.1 else 1.0
                    else:
                        del self.pop_effects[item_name]  # Poista animaatio kun valmis

                # Skaalaa kuva
                width, height = original_image.get_size()
                scaled_image = pygame.transform.scale(original_image, (int(width * scale), int(height * scale)))

                # Piirrä kuva
                self.screen.blit(scaled_image, (x, y))

                # Piirrä lukumäärä
                count = self.collected_counts.get(item_name, 0)
                count_text = self.font.render(str(count), True, (0, 0, 0))
                self.screen.blit(count_text, (x + 30, y + 75))
        
        # Pakotetaan näyttö päivittämään UI:n
        pygame.display.update()

class ScoreDisplay:
    def __init__(self, screen, font, icon_image, all_item_names):
        self.screen = screen
        self.font = font
        self.icon_image = pygame.transform.scale(icon_image, (250, 250))  # Skaalataan ikoni dynaamiseksi
        self.score = 0
        self.alpha = 255
        self.display_time = pygame.time.get_ticks()
        self.fade_duration = 4000
        self.triple_score_active = False
        self.triple_score_timer = 0
        self.triple_score_duration = 20000

        self.items_collected = {item: 0 for item in all_item_names}

    def activate_triple_score(self):
        self.triple_score_active = True
        self.triple_score_timer = pygame.time.get_ticks() + self.triple_score_duration

    def add_score(self, points):
        if self.triple_score_active:
            points *= 3
        self.score += points
        self.display_time = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.display_time

        # Triple Score ajastimen tarkistus
        if self.triple_score_active and current_time >= self.triple_score_timer:
            self.triple_score_active = False

        # Fade-efekti
        if elapsed_time < self.fade_duration:
            self.alpha = int((elapsed_time / self.fade_duration) * 255)
        else:
            self.alpha = 255 if elapsed_time < self.fade_duration * 1.3 else 0

    def draw(self):
        if self.alpha > 0:
                # Kopioidaan ja asetetaan alpha-arvo ikonille
                icon = self.icon_image.copy()
                icon.set_alpha(self.alpha)

                # Piirretään ikoni
                icon_x = 20  # Ikonin x-sijainti
                icon_y = 20  # Ikonin y-sijainti
                self.screen.blit(icon, (icon_x, icon_y))

                # Alusta score.font
                score = type('', (), {})()  # Luo tyhjä objekti dynaamisesti
                score.font = pygame.font.Font(None, 40)  # Alusta fontti

                # Lasketaan pisteiden tekstin sijainti suhteessa ikoniin
                score_text = score.font.render(f"Pisteet: {self.score}", True, (255, 255, 255))
                score_text.set_alpha(self.alpha)

                # Keskitetään teksti ikonin sisälle
                text_rect = score_text.get_rect(center=(icon_x + self.icon_image.get_width() // 2,
                                                        icon_y + self.icon_image.get_height() // 1.5))
                self.screen.blit(score_text, text_rect)

                # Triple Score -ajastin
                if self.triple_score_active:
                    remaining_time = max(0, (self.triple_score_timer - pygame.time.get_ticks()) // 1000)
                    
                    # Piirrä varjostus (musta)
                    triple_text_shadow = self.font.render(f"Piste Boosteri: {remaining_time}s", True, (0, 0, 0))
                    triple_text_shadow_rect = triple_text_shadow.get_rect(center=(icon_x + self.icon_image.get_width() // 1.3,
                                                                                icon_y + self.icon_image.get_height() - 220))
                    self.screen.blit(triple_text_shadow, (triple_text_shadow_rect.x + 2, triple_text_shadow_rect.y + 2))  # Siirrä varjo hieman

                    # Piirrä teksti (keltainen)
                    triple_text = self.font.render(f"Piste Boosteri: {remaining_time}s", True, (255, 255, 0))  # Keltainen teksti
                    triple_text_rect = triple_text.get_rect(center=(icon_x + self.icon_image.get_width() // 1.3,
                                                                    icon_y + self.icon_image.get_height() - 220))
                    self.screen.blit(triple_text, triple_text_rect)