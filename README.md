# ECOCOM-Game
This project is licensed under the [Creative Commons Attribution-NonCommercial (CC BY-NC)](https://creativecommons.org/licenses/by-nc/4.0/) license.

This repository contains my thesis, which I developed as a commissioned work. It is a 2D game, developed with PyGame on RaspberryPi to run on RetroPie.
In the game, you collect computer parts that fall from above, getting the right parts earns you points and getting the wrong parts loses you lives.
The game works with a joystick, controller and keyboard.

The game saves scores to a JSON file, and the scores are displayed in the leaderboard table in the Main Menu. 
Players can enter a nickname for saving purposes, and when selecting a nickname, they can navigate back to the buttons by pressing "E" on the computer keyboard. 
If you're using a game controller/joystick, navigation to the buttons is done by pressing the "select" button on the controller when interacting with buttons.

The game can be run on a computer by setting up a virtual environment (venv) required by Python and running the main.py file in the terminal: python main.py.

If you want to test the game on RetroPie, you need to first install Python and PyGame on RetroPie (sudo apt install python3-pygame). 
Then, you need the following Shell Script:

#!/bin/bash
python3 /home/pi/RetroPie/roms/ports/PyGame/main.py

The Shell Script is executed in RetroPie's terminal with the command: 
chmod +x /home/pi/RetroPie/roms/ports/nameOfTheShellScript.sh

After this, by launching RetroPie, the game should appear in the ports folder. 
If it doesn't, install some a ROM game into the ports folder. 
Then, the Shell Script will also become visible.
