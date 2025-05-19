import pygame
import time
import json
import os

CONFIG_FILE = "controller_config.json"

# Oletusasetukset
DEFAULT_CONFIG = {
    "up": {"type": "key", "value": pygame.K_UP},
    "down": {"type": "key", "value": pygame.K_DOWN},
    "left": {"type": "key", "value": pygame.K_LEFT},
    "right": {"type": "key", "value": pygame.K_RIGHT},
    "select": {"type": "key", "value": pygame.K_RETURN},
    "back": {"type": "key", "value": pygame.K_ESCAPE},
    # Oletus-dpad:
    "up_dpad": {"type": "joyhat", "value": [0, 1]},
    "down_dpad": {"type": "joyhat", "value": [0, -1]},
    "left_dpad": {"type": "joyhat", "value": [-1, 0]},
    "right_dpad": {"type": "joyhat", "value": [1, 0]},
    "select_a": {"type": "joybutton", "value": 0},
    # Oletus-analogitikku:
    "left_axis": {"type": "joyaxis", "axis": 0, "direction": -1},  # vasen
    "right_axis": {"type": "joyaxis", "axis": 0, "direction": 1},  # oikea
    "up_axis": {"type": "joyaxis", "axis": 1, "direction": -1},    # ylös
    "down_axis": {"type": "joyaxis", "axis": 1, "direction": 1},   # alas
}

def load_controller_config():
    """Lataa ohjainkonfiguraation JSON-tiedostosta"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            if config:  # Jos tiedosto ei ole tyhjä
                return config
    return DEFAULT_CONFIG.copy()  # Palautetaan oletusasetukset

class Controller:
    def __init__(self):
        
        self.last_input_time = time.time()
        self.deadzone = 0.2
        self.joystick = None

        self.axis_cooldown = 0.2  # Sekunteina
        self.last_horizontal_input_time = time.time()
        self.last_vertical_input_time = time.time()

        self.reload_config()

        # Alustetaan peliohjain, jos sellainen on saatavilla
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print("Ohjain alustettu.")  # Debug-tulostus
        else:
            print("Ohjainta ei löydy.")  # Debug-tulostus

    def reload_config(self):
        """Lataa konfiguraation uudelleen tiedostosta"""
        self.config = load_controller_config()

    def handle_menu_navigation(self, selected_index, buttons, events, cooldown=0.15):
        now = time.time()
        for event in events:
            action = self.get_input(event)
            if action == "up" and now - self.last_input_time > cooldown:
                selected_index = (selected_index - 1) % len(buttons)
                self.last_input_time = now
            elif action == "down" and now - self.last_input_time > cooldown:
                selected_index = (selected_index + 1) % len(buttons)
                self.last_input_time = now
            elif action == "select" and now - self.last_input_time > cooldown:
                buttons[selected_index][1]()
                self.last_input_time = now
        return selected_index

    def confirm_selection(self):
        keys = pygame.key.get_pressed()
        now = time.time()

        if (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]) and (now - self.last_input_time > 0.15):
            self.last_input_time = now
            return True

        if self.joystick:
            if self.joystick.get_button(0) and (now - self.last_input_time > 0.15):  # A-painike
                self.last_input_time = now
                return True

        return False

    def get_movement(self, events):
        movement = pygame.Vector2(0, 0)

        # Näppäimistö configin mukaan
        keys = pygame.key.get_pressed()
        for action, binding in self.config.items():
            if binding["type"] == "key":
                if keys[binding["value"]]:
                    if action == "up":
                        movement.y -= 1
                    elif action == "down":
                        movement.y += 1
                    elif action == "left":
                        movement.x -= 1
                    elif action == "right":
                        movement.x += 1

        if self.joystick:
            # 1. Käyttäjän määrittämät joyaxis (analogitikku)
            has_axis = any(b["type"] == "joyaxis" for b in self.config.values())
            axis_active = False
            if has_axis:
                for action, binding in self.config.items():
                    if binding["type"] == "joyaxis":
                        axis_val = self.joystick.get_axis(binding["axis"])
                        if binding["direction"] == 1 and axis_val > self.deadzone:
                            if action in ("right", "right_axis"):
                                movement.x = 1
                                axis_active = True
                            elif action in ("down", "down_axis"):
                                movement.y = 1
                                axis_active = True
                        elif binding["direction"] == -1 and axis_val < -self.deadzone:
                            if action in ("left", "left_axis"):
                                movement.x = -1
                                axis_active = True
                            elif action in ("up", "up_axis"):
                                movement.y = -1
                                axis_active = True
            else:
                # Oletus: käytä analogitikkua, jos joyaxis ei ole määritetty
                axis_x = self.joystick.get_axis(0)
                axis_y = self.joystick.get_axis(1)
                if axis_x > self.deadzone:
                    movement.x = 1
                    axis_active = True
                elif axis_x < -self.deadzone:
                    movement.x = -1
                    axis_active = True
                else:
                    movement.x = 0

                if axis_y > self.deadzone:
                    movement.y = 1
                    axis_active = True
                elif axis_y < -self.deadzone:
                    movement.y = -1
                    axis_active = True
                else:
                    movement.y = 0

            # 2. Käyttäjän määrittämät joyhat (dpad) – käytä vain jos joyaxis EI OLE aktiivinen
            if not axis_active:
                has_hat = any(b["type"] == "joyhat" for b in self.config.values())
                if has_hat:
                    hat = self.joystick.get_hat(0)
                    if hat != (0, 0):  # VAIN jos DPad on painettu
                        for action, binding in self.config.items():
                            if binding["type"] == "joyhat" and tuple(binding["value"]) == hat:
                                if action in ("up", "up_dpad"):
                                    movement.y -= 1
                                elif action in ("down", "down_dpad"):
                                    movement.y += 1
                                elif action in ("left", "left_dpad"):
                                    movement.x -= 1
                                elif action in ("right", "right_dpad"):
                                    movement.x += 1
                else:
                    # Oletus: käytä dpadia, jos joyhat ei ole määritetty
                    hat_x, hat_y = self.joystick.get_hat(0)
                    movement.x += hat_x
                    movement.y -= hat_y  # Yleensä y-akseli on käänteinen dpadissa

        return movement

    def get_input(self, event):
        """Tarkistaa käyttäjän toiminnon konfiguraation perusteella."""
        if not self.config:
            return None  # Jos ei konfiguraatiota, ei toimintoa

        # Näppäimistön tapahtumat
        if event.type == pygame.KEYDOWN:
            for action, binding in self.config.items():
                if binding["type"] == "key" and event.key == binding["value"]:
                    return action

        # Ohjaimen painikkeet
        elif event.type == pygame.JOYBUTTONDOWN:
            for action, binding in self.config.items():
                if binding["type"] == "joybutton" and event.button == binding["value"]:
                    return action

        # Ohjaimen akselit (analogitikku)
        elif event.type == pygame.JOYAXISMOTION:
            for action, binding in self.config.items():
                if binding["type"] == "joyaxis" and event.axis == binding["axis"]:
                    direction = 1 if event.value > 0.5 else -1 if event.value < -0.5 else 0
                    if direction == binding["direction"]:
                        # Palauta suunta, jotta valikkonavigointi toimii
                        if action in ("right", "right_axis"):
                            return "right"
                        elif action in ("left", "left_axis"):
                            return "left"
                        elif action in ("up", "up_axis"):
                            return "up"
                        elif action in ("down", "down_axis"):
                            return "down"
                        else:
                            return action

        # Ohjaimen HAT (D-pad)
        elif event.type == pygame.JOYHATMOTION:
            for action, binding in self.config.items():
                if binding["type"] == "joyhat" and tuple(binding["value"]) == event.value:
                    if action in ("up", "up_dpad"):
                        return "up"
                    elif action in ("down", "down_dpad"):
                        return "down"
                    elif action in ("left", "left_dpad"):
                        return "left"
                    elif action in ("right", "right_dpad"):
                        return "right"

        # Hiiren tapahtumat
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Hiiren vasen painike
                return "select"

        return None

    def esc_pressed(self):
        """Tarkistaa, onko ESC-painiketta painettu."""
        keys = pygame.key.get_pressed()
        return keys[pygame.K_ESCAPE]