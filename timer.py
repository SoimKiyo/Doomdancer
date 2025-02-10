import pygame

# Classe du Timer pour les actions
class Timer:
    def __init__(self, duration):
        self.start_time = None
        self.duration = duration  # Durée en millisecondes (3000 ms = 3s)
        self.active = False

    def start(self):
        self.start_time = pygame.time.get_ticks()
        self.active = True

    def is_finished(self):
        if self.active and pygame.time.get_ticks() - self.start_time >= self.duration:
            self.active = False
            return True
        return False
