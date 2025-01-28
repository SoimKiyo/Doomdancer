import pygame
from player import Player

# Constantes pour la zone de jeu
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50

# Classe du jeu
class Game:
    def __init__(self, screen_width, screen_height):
        # Dimensions de l'écran
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Zone jouable (limites de l'écran)
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

        # Création du joueur
        self.player = Player(screen_width // 2, screen_height // 2, PLAYER_WIDTH, PLAYER_HEIGHT)

        # Couleurs du décor
        self.background_color = (20, 20, 20)

    # Met a jour la taille de l'écran
    def update_screen_limits(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player.update_screen_limits(screen_width, screen_height)

    # Met a jour les éléments du jeu (comme le joueur)
    def update(self, keys):
        self.player.move(keys, self.screen_rect)

    # Dessine et affiche les éléments du jeu
    def draw(self, screen):
        screen.fill(self.background_color)  # Dessine le fond
        self.player.draw(screen)  # Dessine le joueur

    # Réinitialise le jeu
    def reset(self):
        self.player.rect.x = self.screen_width // 2
        self.player.rect.y = self.screen_height // 2
