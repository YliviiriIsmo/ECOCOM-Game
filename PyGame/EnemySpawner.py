import pygame
import random
import os
from GameUI import GameUI, ScoreDisplay
#import game_music

# Alustetaan Pygame
pygame.init()

# Määritetään sprite-kansiot
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENEMY_FOLDER = os.path.join(BASE_DIR)
GROUND_ENEMY_FOLDER = os.path.join(BASE_DIR)
COLLECTIBLE_FOLDER = os.path.join(BASE_DIR)

# Skaalauskerroin suhteessa näytön kokoon
def calculate_scale_factor(screen_width, screen_height, base_width=1920, base_height=1080):
    scale_x = screen_width / base_width
    scale_y = screen_height / base_height
    return min(scale_x, scale_y)  # Käytetään pienempää skaalausta, jotta mittasuhteet säilyvät

# Alustetaan skaalauskerroin
screen_width, screen_height = pygame.display.get_surface().get_size()
SCALE_FACTOR = calculate_scale_factor(screen_width, screen_height) * 0.40  # skaalaus pienemmäksi

def scale_image(image, scale_factor):
    width = int(image.get_width() * scale_factor)
    height = int(image.get_height() * scale_factor)
    return pygame.transform.scale(image, (width, height))

# Ladataan ilmavihollisten kuvat (2 eri vihollista)
enemy_sprites = [
    ("Omena", pygame.image.load(os.path.join(ENEMY_FOLDER, "omena.png"))),
    ("Ohjain", pygame.image.load(os.path.join(ENEMY_FOLDER, "ohjain.png")))
]

# Ladataan maavihollisen animaatiot (2 kuvaa kävelylle)
ground_enemy_sprites = [
    scale_image(pygame.image.load(os.path.join(GROUND_ENEMY_FOLDER, "mouse1.png")), SCALE_FACTOR),
    scale_image(pygame.image.load(os.path.join(GROUND_ENEMY_FOLDER, "mouse2.png")), SCALE_FACTOR)
]

# Esineiden nimet määritelty erikseen
ITEM_NAMES = {
    "1.cpu.png": "Prosessori",
    "2.emolevy.png": "Emolevy",
    "3.ram_muisti.png": "RAM Muisti",
    "4.kovalevy.png": "Kovalevy",
    "5.PSU.png": "Virtalahde",
    "6.naytonohjain.png": "Naytonohjain",
    "7.tuuletin.png": "Tuuletin",
    "8.heatsink.png": "Jaahdytyssiili",
    "9.syotto-tulostus.png": "Oheislaitteet",
    "10.verkkosovitin.png": "Verkkosovitin",
    "triple_score.png": "Piste Boosteri"
}

def scale_image(image, scale_factor):
    width = int(image.get_width() * scale_factor)
    height = int(image.get_height() * scale_factor)
    return pygame.transform.scale(image, (width, height))

class Enemy(pygame.sprite.Sprite):
    """Ilmasta putoava vihollinen"""
    def __init__(self, x, y):
        super().__init__()

        name, sprite_choice = random.choice(enemy_sprites)  # Valitaan nimi ja kuva erikseen
        self.image = scale_image(sprite_choice, SCALE_FACTOR)  # Skaalataan vain kuva
        self.enemy_name = name # Tallennetaan vihollisen nimi
        
        # Määritä nimi tiedoston perusteella
        if sprite_choice == enemy_sprites[0][1]:  # Vertaa
            self.enemy_name = "Omena"
        else:
            self.enemy_name = "Ohjain"
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(1, 2)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > self.rect.y + self.rect.height:  # Poistetaan, kun menee ruudun ulkopuolelle
            self.kill()

class GroundEnemy(pygame.sprite.Sprite):
    """Maan tasolla liikkuva vihollinen, jolla on animaatio"""
    def __init__(self, x, y, speed, sprite_image, name="Tuntematon vihollinen"):
        super().__init__()
        # Skaalataan ground_enemy_sprites vain kerran, kun ne ladataan
        self.sprites = ground_enemy_sprites  # Käytetään jo skaalattuja kuvia
        self.image_index = 0
        self.image = self.sprites[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.animation_timer = 0
        self.enemy_name = name  # Nyt vihollisella on nimi

        # Käännä sprite, jos liikkuu oikealle
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        self.rect.x += self.speed
        self.animation_timer += 1
        if self.animation_timer % 15 == 0:
            self.image_index = (self.image_index + 1) % len(self.sprites)
            self.image = self.sprites[self.image_index]

            # Käännä sprite, jos liikkuu oikealle
            if self.speed > 0:
                self.image = pygame.transform.flip(self.image, True, False)

class Collectible(pygame.sprite.Sprite):
    """Kerättävä esine"""
    def __init__(self, x, y, image, item_name):  # Poistetaan filename-parametri
        super().__init__()
   
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.item_name = item_name  # Tallennetaan esineen nimi
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > self.rect.y + self.rect.height:  # Poistetaan, kun menee ruudun ulkopuolelle
            self.kill()

class EnemySpawner:
    """Generoi vihollisia ja kerättäviä esineitä"""
    def __init__(self, screen, game_ui):
        self.screen = screen
        self.game_ui = game_ui  # Käytetään samaa GameUI-instanssia
        self.WIDTH, self.HEIGHT = screen.get_size()  # Haetaan oikea koko
        self.initial_min_spawn_interval = 0.7 #Minimi spawni aika (säädä näitä jos haluat vaikeuttaa peliä)
        self.initial_max_spawn_interval = 3 #Maksimi spawni aika (säädä näitä jos haluat vaikeuttaa peliä)
        self.min_spawn_interval = self.initial_min_spawn_interval
        self.max_spawn_interval = self.initial_max_spawn_interval
        self.last_spawn_time = pygame.time.get_ticks()
        self.cycle_duration = 150000  # 2 minuuttia 30 sekuntia millisekunneissa, vaikeustason muutos
        self.increasing_difficulty = True
        self.start_time = pygame.time.get_ticks()

    def spawn_object(self, all_sprites, enemies, ground_enemies, collectibles):
        """Luo joko ilmavihollisen, maavihollisen tai kerättävän esineen"""
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time

        # Päivitä vaikeustaso
        self.update_difficulty(elapsed_time)

        min_interval_ms = int(self.min_spawn_interval * 1000)
        max_interval_ms = int(self.max_spawn_interval * 7000)

        if min_interval_ms < max_interval_ms:
            if current_time - self.last_spawn_time > random.randint(min_interval_ms, max_interval_ms):
                spawn_type = random.random()

                if spawn_type < 0.3:  # 30% ilmavihollinen
                    x = random.randint(50, self.WIDTH - 50)
                    enemy = Enemy(x, 0)  # Käytetään `enemy_sprites`-listaa
                    enemies.add(enemy)
                    all_sprites.add(enemy)

                elif spawn_type < 0.4:  # 40% maavihollinen
                    x, y, speed, sprite_image = self.get_ground_enemy_spawn_position()
                    ground_enemy = GroundEnemy(x, y, speed, sprite_image, name="Hiiri")
                    ground_enemies.add(ground_enemy)
                    all_sprites.add(ground_enemy)

                else:  # 30% kerättävä esine
                    # Valitaan satunnainen esine `ITEM_NAMES`-listasta
                    filename = random.choice(list(ITEM_NAMES.keys()))
                    full_path = os.path.join(COLLECTIBLE_FOLDER, filename)

                    if os.path.isfile(full_path):  # Varmistetaan, että tiedosto on olemassa
                        image = pygame.image.load(full_path)
                        image = scale_image(image, SCALE_FACTOR)  # Skaalataan esine

                        # Haetaan esineen nimi taulukosta
                        item_name = ITEM_NAMES[filename]

                        x = random.randint(50, self.WIDTH - 50)

                        collectible = Collectible(x, 0, image, item_name)
                        collectibles.add(collectible)
                        all_sprites.add(collectible)

                self.last_spawn_time = current_time

    def get_ground_enemy_spawn_position(self):
        """Palauttaa satunnaisen spawn-paikan maaviholliselle"""
        side = random.choice(['left', 'right'])
        max_height = self.HEIGHT // 2  # Maksimi korkeus on 1/2 ruudun korkeudesta
        y = random.randint(self.HEIGHT - max_height, self.HEIGHT - 50)  # Satunnainen korkeus alhaalta

        sprite_image = random.choice(ground_enemy_sprites)  # Valitaan satunnainen animaatiokuva

        if side == 'left':
            x = 0  # Vasen reuna
            speed = 4  # Liikkuu oikealle
        else:
            x = self.WIDTH - 100  # Oikea reuna
            speed = -4  # Liikkuu vasemmalle
        return x, y, speed, sprite_image
    

    def update_difficulty(self, elapsed_time):
        """Päivittää vaikeustason ajan myötä"""
        factor = (elapsed_time % self.cycle_duration) / self.cycle_duration

        if self.increasing_difficulty:
            self.min_spawn_interval = self.lerp(self.initial_min_spawn_interval, 0.5, factor)
            self.max_spawn_interval = self.lerp(self.initial_max_spawn_interval, 1, factor)
        else:
            self.min_spawn_interval = self.lerp(0.5, self.initial_min_spawn_interval, factor)
            self.max_spawn_interval = self.lerp(1, self.initial_max_spawn_interval, factor)

        if elapsed_time // self.cycle_duration % 2 == 1:
            self.increasing_difficulty = not self.increasing_difficulty

    @staticmethod
    def lerp(start, end, factor):
        """Lineaarinen interpolointi"""
        return start + factor * (end - start)