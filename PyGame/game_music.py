
import pygame
import os

#pygame.mixer.quit()
#pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.init()  # Alustetaan äänimoduli

# Selvitetään nykyisen tiedoston sijainti
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Määritetään musiikkitiedostot
MAIN_MENU_MUSIC = "main_menu.mp3"
GAME_MUSIC = "game_music.mp3"
GAME_OVER_MUSIC = "main_menu.mp3"  # Sama kuin päävalikossa

pygame.mixer.set_num_channels(8)  # Asetetaan 8 erillistä kanavaa ääniefekteille

# Ladataan ääniefektit etukäteen
#sound_hover = pygame.mixer.Sound(os.path.join(BASE_DIR, "buttonhover.wav"))
#sound_select = pygame.mixer.Sound(os.path.join(BASE_DIR, "buttonselect.wav"))

# Käytetään erillisiä kanavia ääniefekteille
channel_hover = pygame.mixer.Channel(1)  # Kanava 1
channel_select = pygame.mixer.Channel(2)  # Kanava 2

def play_music(file):
    #Soittaa annetun musiikkitiedoston loopaten.
    pygame.mixer.music.stop()  # Pysäytetään nykyinen musiikki
    pygame.mixer.music.load(os.path.join(BASE_DIR, file))  # Ladataan uusi musiikki
    pygame.mixer.music.play(-1)  # Aloitetaan toisto loopaten

def play_sound_effect(file):
    #Soittaa yksittäisen ääniefektin ilman, että päämusiikki pysähtyy.
    sound = pygame.mixer.Sound(file)
    pygame.mixer.sound.load(os.path.join(BASE_DIR, file))
    sound.play()

    def stop_music():
        # Pysäyttää kaiken musiikin.
        pygame.mixer.music.stop()

    def set_volume(volume):
        #Asettaa äänenvoimakkuuden (0.0 - 1.0).
        pygame.mixer.music.set_volume(volume)

"""
# Esimerkkejä ääniefektien soittamisesta
def play_button_hover():
    #Soittaa napin hover-ääniefektin.
    channel_hover.play(sound_hover)

def play_button_select():
    #Soittaa napin valinta-ääniefektin.
    channel_select.play(sound_select)

    def play_collect_item():
        #Soittaa esineen keräys-ääniefektin.
        sound = pygame.mixer.Sound("button_hover.wav")
        sound.play()

    def play_collect_booster():
        #Soittaa boosterin keräys-ääniefektin.
        sound = pygame.mixer.Sound("button_hover.wav")
        sound.play()

    def play_damage():
        #Soittaa vahinko-ääniefektin.
        sound = pygame.mixer.Sound("button_hover.wav")
        sound.play()

    def play_set_sound():
        #Soittaa äänen asetukset-ääniefektin.
        sound = pygame.mixer.Sound("button_hover.wav")
        sound.play()
"""

