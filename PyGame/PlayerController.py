import pygame
import os
import sys
from game_over import GameOver
from EnemySpawner import EnemySpawner
from GameUI import GameUI, ScoreDisplay
import game_music

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_image, scale_x, scale_y):
        super().__init__()
        self.scale_x = scale_x
        self.scale_y = scale_y

        # Skaalaa sprite
        new_width = int(sprite_image.get_width() * self.scale_x)
        new_height = int(sprite_image.get_height() * self.scale_y)
        self.image = pygame.transform.scale(sprite_image, (new_width, new_height))
        self.original_image = self.image.copy()

        # Skaalattu törmäysalue
        self.rect = self.image.get_rect(center=(x, y))
        self.rect.inflate_ip(15 * self.scale_x, 25 * self.scale_y)

        self.flash_timer = 0
        self.flashing = False

    def update(self, new_x, new_y):
        self.rect.center = (new_x, new_y)  # Säilyttää keskipisteen

main_menu_instance = None  # Globaali päävalikko-instanssi

def run_game(screen):

    global main_menu_instance

    # Alustetaan Pygame
    pygame.init()

    pygame.font.init()  # Alustetaan fontit

    game_music.play_music(game_music.GAME_MUSIC)

    # Näytön koko
    WIDTH, HEIGHT = screen.get_size()
    SCALE_X = WIDTH / 1920
    SCALE_Y = HEIGHT / 1080

    pygame.display.set_caption("Pygame Player Controller")

    # Fontti
    font = pygame.font.Font(None, int(30 * SCALE_Y))
    hit_font = pygame.font.SysFont("Arial", int(50 * SCALE_Y))  # Törmäysviestin fontti

    # Lataa spritet
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # **Lataa ja skaalaa taustakuva**
    background = pygame.image.load(os.path.join(BASE_DIR, "game_background.png"))
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # **Skaalattu aika-ikoni**
    time_icon = pygame.image.load(os.path.join(BASE_DIR, "time_icon.png"))
    time_icon = pygame.transform.scale(time_icon, (int(144 * SCALE_X), int(60 * SCALE_Y)))

    # **Skaalattu piste-ikoni**
    score_icon = pygame.image.load(os.path.join(BASE_DIR, "score_icon.png"))
    score_icon = pygame.transform.scale(score_icon, (int(300 * SCALE_X), int(300 * SCALE_Y)))

    # Ladataan pistekuvake
    icon_image = pygame.Surface((50, 50))  

    # Lista kaikista esineiden nimistä (korvaa nämä oikeilla tiedoilla)
    all_item_names = ["item1", "item2", "item3"]  

    # Alustetaan ScoreDisplay **ensin**
    score_display = ScoreDisplay(screen, font, icon_image, all_item_names)

    # UI
    game_ui = GameUI(screen, score_display)

    # Osumaviesti
    hit_message = ""
    hit_message_timer = 0
    hit_message_duration = 2000  # Näytetään 2 sekuntia

    # Värit
    WHITE = (255, 255, 255)

    def load_sprite(filename):
        """Lataa pelaajan sprite annetusta tiedostosta"""
        sprite = pygame.image.load(os.path.join(BASE_DIR, filename)).convert_alpha()
        new_width = int(sprite.get_width() * SCALE_X)
        new_height = int(sprite.get_height() * SCALE_Y)
        return pygame.transform.scale(sprite, (new_width, new_height))
        #return pygame.image.load(os.path.join(BASE_DIR, filename)).convert_alpha()
    
    #Hahmon kuvat
    front_idle = load_sprite("front_idle.png")
    front_step1 = load_sprite("front_step1.png")
    front_step2 = load_sprite("front_step2.png")
    back_idle = load_sprite("back_idle.png")
    back_step1 = load_sprite("back_step1.png")
    back_step2 = load_sprite("back_step2.png")
    left_idle = load_sprite("left_idle.png")
    left_step1 = load_sprite("left_step1.png")
    left_step2 = load_sprite("left_step2.png")
    right_idle = load_sprite("right_idle.png")
    right_step1 = load_sprite("right_step1.png")
    right_step2 = load_sprite("right_step2.png")

    push_left_sprite = load_sprite("push_left.png")
    push_right_sprite = load_sprite("push_right.png")
    push_down_sprite = load_sprite("push_down.png")

    # Hahmon asetukset
    player_pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
    move_speed = 200 * SCALE_X  # Pikseleitä sekunnissa
    push_back_force = 100 * SCALE_X

    # Hahmon koko (lasketaan yhden spriten perusteella)
    player_width = front_idle.get_width()
    player_height = front_idle.get_height()

    # Liikkumisrajat
    minX = player_width // 2
    maxX = WIDTH - player_width // 2
    minY = player_height // 1.9
    maxY = HEIGHT - player_height // 3.5

    # Animaatiot
    walking_animation = {
        "up": [back_step1, back_step2, back_idle],
        "down": [front_step1, front_step2, front_idle],
        "left": [left_step1, left_step2, left_idle],
        "right": [right_step1, right_step2, right_idle]
    }
    last_idle_sprite = front_idle
    current_sprite = last_idle_sprite

    # Animaation ajastin
    animation_index = 0
    animation_timer = 0
    animation_speed = 0.2

    player = Player(WIDTH / 2, HEIGHT / 2, front_idle, SCALE_X, SCALE_Y)  

    # FPS-kello
    clock = pygame.time.Clock()

    # Enemy spawner
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    ground_enemies = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()
    spawner = EnemySpawner(screen, game_ui) # Käytetään jo luotua game_ui:ta

    # Luo ScoreDisplay-olio
    font = pygame.font.Font(None, 50)  # Fontti pisteille
    score_display = ScoreDisplay(screen, font, score_icon, list(game_ui.item_images.keys()))

    # Peliohjain
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    # Akseliarvojen suodatin (ohjainliikkeen herkkyys)
    DEADZONE = 0.2 * SCALE_X  # Jos arvo on alle tämän, se nollataan

    font = pygame.font.Font(None, int(50 * SCALE_Y))  # Fontti ajalle
    start_time = pygame.time.get_ticks()  # Tallennetaan aloitusaika

    running = True
    while running:
        dt = clock.tick(60) / 1000  # Muutetaan millisekunnit sekunneiksi

        # Tapahtumat
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Liikkuminen
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(0, 0)

        # Näppäimistö
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement.x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement.x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            movement.y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            movement.y = 1

        # Peliohjain
        if joystick:
            joy_x = joystick.get_axis(0)
            joy_y = joystick.get_axis(1)

            # Suodatetaan pienet liikkeet
            if abs(joy_x) > DEADZONE:
                movement.x += joy_x
            if abs(joy_y) > DEADZONE:
                movement.y += joy_y

        # Normalisoidaan liikevektori
        if movement.length() > 0:
            movement = movement.normalize() * move_speed * dt

            # Animaation päivitys
            animation_timer += dt
            if animation_timer >= animation_speed:
                animation_index = (animation_index + 1) % 2
                animation_timer = 0

            if movement.y < 0:
                current_sprite = walking_animation["up"][animation_index]
                last_idle_sprite = walking_animation["up"][2]
            elif movement.y > 0:
                current_sprite = walking_animation["down"][animation_index]
                last_idle_sprite = walking_animation["down"][2]
            elif movement.x < 0:
                current_sprite = walking_animation["left"][animation_index]
                last_idle_sprite = walking_animation["left"][2]
            elif movement.x > 0:
                current_sprite = walking_animation["right"][animation_index]
                last_idle_sprite = walking_animation["right"][2]

        else:
            current_sprite = last_idle_sprite

        # Pelaajan liikuttaminen ja törmäysreunat
        new_x = player_pos.x + movement.x
        new_y = player_pos.y + movement.y

        if new_x < minX:
            new_x = minX + push_back_force
            current_sprite = push_left_sprite
        elif new_x > maxX:
            new_x = maxX - push_back_force
            current_sprite = push_right_sprite

        if new_y < minY:
            new_y = minY + push_back_force
            current_sprite = push_down_sprite
        elif new_y > maxY:
            new_y = maxY

        player_pos.x, player_pos.y = new_x, new_y

        # Päivitetään pelaajan sijainti
        player_pos.x = max(minX, min(maxX, player_pos.x + movement.x))
        player_pos.y = max(minY, min(maxY, player_pos.y + movement.y))

        player.update(player_pos.x, player_pos.y)

        """Keräiltävä"""
        # Tarkista törmäykset pelaajan ja keräiltävien esineiden välillä
        collected_items = pygame.sprite.spritecollide(player, collectibles, True)

        for item in collected_items:
            if hasattr(item, "item_name"):  # Varmistetaan, että esineellä on nimi
                if item.item_name == "Piste Boosteri":
                    #game_music.play_sound("collect_booster")  # Boosteri-esineen ääni
                    score_display.activate_triple_score()  # Käynnistetään tehoste
                else:
                    game_ui.add_item(item.item_name)
                    points = 5
                    if score_display.triple_score_active:
                        points *= 3  # Kolminkertaiset pisteet
                    score_display.add_score(points)

                hit_message = f"Tama on {item.item_name}!"
                hit_message_timer = pygame.time.get_ticks()

                # Tarkistetaan, onko jokaisessa esineessä vähintään yksi
                if all(count > 0 for count in game_ui.collected_counts.values()):
                    bonus = 100
                    if score_display.triple_score_active:
                        bonus *= 3
                    score_display.add_score(bonus)

                    # Vähennetään jokaisesta esineestä 1
                    for item in game_ui.collected_counts:
                        game_ui.collected_counts[item] -= 1

        """Enemy"""
        # Tarkista törmäykset pelaajan ja vihollisten välillä
        enemy_hit = pygame.sprite.spritecollide(player, enemies, True)  # Ilmaviholliset
        ground_enemy_hit = pygame.sprite.spritecollide(player, ground_enemies, True)  # Maaviholliset
        
        if enemy_hit or ground_enemy_hit:
            if not player.flashing:  # Varmistetaan, että välkkyminen ei ole jo käynnissä
                player.flashing = True
                player.flash_timer = pygame.time.get_ticks()
                game_ui.remove_life()  # Vähennetään yksi elämä
                hit_message_timer = pygame.time.get_ticks()  # Päivitä ajastin
            
        if enemy_hit:
            for enemy in enemy_hit:
                enemy_name = getattr(enemy, "enemy_name", "Tuntematon vihollinen")  
                hit_message = f"Tama on {enemy_name}!"
                hit_message_timer = pygame.time.get_ticks()

        if ground_enemy_hit:
            for enemy in ground_enemy_hit:
                enemy_name = getattr(enemy, "enemy_name", "Tuntematon vihollinen")  # Varmistetaan, että nimi on olemassa
                if enemy_name.lower() == "hiiri":
                    hit_message = f"Iik {enemy_name}!"
                    
                else:
                    hit_message = f"Tama on {enemy_name}!"
                hit_message_timer = pygame.time.get_ticks()

        # Tarkistetaan, onko pelaajalla enää elämiä jäljellä
        if game_ui.lives <= 0:
            game_over_screen = GameOver(screen, score_display.score, elapsed_time)

            action = game_over_screen.ask_to_save()
            if action == "save":
                game_over_screen.save_game()

            action = game_over_screen.show_screen()  # Tämä estää välittömän pelin uudelleenkäynnistymisen

            if action == "restart":
                return run_game(screen)
            elif action == "menu":
                if main_menu_instance is None:
                    from main_menu import MainMenu
                    main_menu_instance = MainMenu(screen)
                else:
                    main_menu_instance.reset_state()
                screen.fill((0, 0, 0))
                pygame.display.flip()
                main_menu_instance.draw()
                return
            elif action == "quit":
                pygame.quit()
                sys.exit()
 
        """Aika ja piirtäminen"""             
        # Laske kulunut aika
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000  # Muutetaan sekunneiksi
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = font.render(f"{minutes:02}:{seconds:02}", True, (255, 255, 255))

        # Piirrä taustakuva
        screen.blit(background, (0, 0))

        # Piirrä spritet
        spawner.spawn_object(all_sprites, enemies, ground_enemies, collectibles)
        all_sprites.update()
        all_sprites.draw(screen)
        
        #pygame.draw.rect(screen, (255, 0, 0), player.rect, 2)  # Punainen törmäysalue poista käytöstä ennen viimeistä versiota

        # Piirrä aika
        screen.blit(time_icon, (WIDTH - int(200 * SCALE_X), int(20 * SCALE_Y)))
        screen.blit(time_text, (WIDTH - int(170 * SCALE_X), int(35 * SCALE_Y)))

        """Pisteet ja törmäys välkkyminen"""
        # Päivitä ja piirrä pistemäärä
        score_display.update()
        score_display.draw()

        # Näytetään törmäysteksti, jos ajastin ei ole mennyt umpeen
        if hit_message and pygame.time.get_ticks() - hit_message_timer < hit_message_duration:
            # Piirrä varjostus
            shadow_surface = hit_font.render(hit_message, True, (0, 0, 0))  # Musta varjo
            shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 2, HEIGHT // 12 + 2))  # Siirrä varjo hieman
            screen.blit(shadow_surface, shadow_rect)

            # Piirrä teksti
            text_surface = hit_font.render(hit_message, True, (0, 255, 0))  # Vihreä teksti
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 12))
            screen.blit(text_surface, text_rect)
        else:
            hit_message = ""  # Tyhjennä viesti, kun ajastin on umpeutunut

        blit_sprite = current_sprite.copy()  # Kopioi sprite ennen kuin muutetaan alpha-arvoa

        # Jos hahmo on osumasta välkkymistilassa, säädetään läpinäkyvyyttä
        if player.flashing:
            # Tarkistetaan, onko 1.5 sekuntia kulunut törmäyksestä
            if pygame.time.get_ticks() - player.flash_timer > 1500:
                player.flashing = False  # Lopetetaan välkkyminen
            else:
                # Joka toinen frame piilotetaan hahmo
                if (pygame.time.get_ticks() // 100) % 2 == 0:
                    blit_sprite.fill((0, 0, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        #else:
            #blit_sprite.set_alpha(255)  # Jos hahmo ei ole osumassa, se on aina näkyvä

        # Piirretään hahmo lopuksi
        screen.blit(blit_sprite, player.rect.topleft)

        # UI:n piirtäminen, jätä viimeiseksi, jottei hahmo välky
        game_ui.draw()

        pygame.display.flip()

    pygame.quit()
