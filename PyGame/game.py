import time

class Game:
    def __init__(self):
        self.start_time = time.time() # Pelin aloitusaika
        self.score = 0 # Pelin pistetilanne

    def update(self):
        self.elapsed_time = time.time() - self.start_time # Kulunut aika pelissä