import pygame
from main_menu import MainMenu

# Alustetaan Pygame
pygame.init()

# Näytön asetukset
# Haetaan näytön koko
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
SCALE_X = WIDTH / 1920  # resoluutio on 1920x1080
SCALE_Y = HEIGHT / 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

pygame.display.set_caption("Pelin Päävalikko")

# Luodaan päävalikko
menu = MainMenu(screen)

# Pelisilmukka
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    menu.update()
    menu.draw()
    pygame.display.update()
    
    pygame.display.flip()

# Pygamen lopetus (vasta pelin jälkeen)
pygame.quit()