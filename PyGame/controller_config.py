import pygame
import json
import os
import time

CONFIG_FILE = "controller_config.json"
default_actions = ["up", "down", "left", "right", "select", "back"]

def wait_for_input(min_delay=2.0):
    """Odottaa käyttäjän syötettä ja palauttaa sen, pienen viiveen jälkeen."""
    start_time = time.time()
    while True:
        for event in pygame.event.get():
            if time.time() - start_time < min_delay:
                continue
            
            # Estetään liian pienet analogiliikkeet
            if event.type == pygame.JOYAXISMOTION and abs(event.value) < 0.8:
                continue

            if event.type in [pygame.KEYDOWN, pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION, pygame.JOYHATMOTION]:
                return event
            
def configure_controller(screen):
    """Asettaa ohjainkomennot ja tallentaa ne tiedostoon."""
    pygame.font.init()
    font = pygame.font.Font(None, 60)
    bindings = {}

    # Lataa taustakuva
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    background = pygame.image.load(os.path.join(BASE_DIR, "background.png"))
    WIDTH, HEIGHT = screen.get_size()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    for action in default_actions:
        screen.blit(background, (0, 0))
        prompt_text = font.render(f"Aseta ohjain toiminnolle: {action.upper()}", True, (0, 0, 0))
        screen.blit(prompt_text, (screen.get_width() // 2 - prompt_text.get_width() // 2, screen.get_height() // 2 - 40))
        pygame.display.flip()

        event = wait_for_input(min_delay=0.5)

        if event.type == pygame.KEYDOWN:
            bindings[action] = {"type": "key", "value": event.key}
        elif event.type == pygame.JOYBUTTONDOWN:
            bindings[action] = {"type": "joybutton", "value": event.button}
        elif event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.5:
            bindings[action] = {
                "type": "joyaxis",
                "axis": event.axis,
                "direction": 1 if event.value > 0 else -1
            }
        elif event.type == pygame.JOYHATMOTION:
            bindings[action] = {"type": "joyhat", "value": list(event.value)}

    with open(CONFIG_FILE, 'w') as f:
        json.dump(bindings, f, indent=4) # Tallenna asetukset tiedostoon

    show_done_screen(screen, background)

def show_done_screen(screen, background):
    """Näyttää asetusten tallennusilmoituksen ja tarjoaa paluun päävalikkoon."""
    pygame.font.init()
    font = pygame.font.Font(None, 60)
    back_font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()

    selected = False
    while not selected:
        screen.blit(background, (0, 0))
        msg = font.render("Ohjainasetukset tallennettu!", True, (0, 0, 0))
        screen.blit(msg, (screen.get_width() // 2 - msg.get_width() // 2, screen.get_height() // 2 - 60))

        back_text = back_font.render("Paina B (ohjain) tai ESC (näppäimistö) palataksesi", True, (0, 0, 0))
        screen.blit(back_text, (screen.get_width() // 2 - back_text.get_width() // 2, screen.get_height() // 2 + 20))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                selected = True
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 1:  # B
                selected = True

def run(screen):
    """Aloittaa suoraan ohjainasetusten määrittelyn."""
    configure_controller(screen)