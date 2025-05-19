import pygame
from controller import Controller
from main_menu import MainMenu

# Alustetaan Pygame
pygame.init()
pygame.joystick.init()

# Näytön asetukset
# Haetaan näytön koko
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
SCALE_X = WIDTH / 1920  # resoluutio on 1920x1080
SCALE_Y = HEIGHT / 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

pygame.display.set_caption("Pelin Päävalikko")

# Luodaan päävalikko
controller = Controller()
controller.reload_config()  # Lataa ohjainkonfiguraatio heti ohjelman alussa
menu = MainMenu(screen, controller=controller)

# Pelisilmukka
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    menu.update(events)
    menu.draw()
    pygame.display.flip()

# Pygamen lopetus (vasta pelin jälkeen)
pygame.quit()