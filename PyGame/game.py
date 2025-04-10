import time

class Game:
    def __init__(self):
        self.start_time = time.time()
        self.score = 0

    def update(self):
        self.elapsed_time = time.time() - self.start_time