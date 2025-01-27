from main import SCREEN_WIDTH
import pygame

class Menu:
    def __init__(self):
        self.options = ["Jouer", "Parametres", "Quitter"]
        self.selected = 0 # Index de l'option utilisé

        # Options du menu paramètres
        self.in_settings = False
        self.music_volume = 0.5
        self.sound_effects_volume = 0.7
    
    def draw(self, screen, font):
        # Affichr le menu principal/parametres
        screen.fill((0,0,0))

        if not self.in_settings:
            # Menu principal
            title = font.render("DOOMDANCER", True, (255,0,0))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_witdh() // 2, 100))

            