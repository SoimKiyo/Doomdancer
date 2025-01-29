import pygame
from player import Player, load_animations, scale_img
from constants import *
from weapon import Weapon

# Arme du joueur
def soulorb_image():
    return scale_img(pygame.image.load("assets/images/weapons/soulorb.png").convert_alpha(), WEAPON_SCALE)


# Classe du jeu
class Game:
    def __init__(self, screen_width, screen_height, joysticks):
        # Dimensions de l'écran
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.joysticks = joysticks

        # Zone jouable (limites de l'écran)
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

        # Création du joueur
        self.mob_animations = load_animations()
        self.player = Player(screen_width // 2, screen_height // 2, PLAYER_WIDTH, PLAYER_HEIGHT, self.mob_animations, 0)

        # Arme
        self.weapon = Weapon(soulorb_image(), self.joysticks)

        # Couleurs du décor
        self.background_color = (20, 20, 20)

    # Met a jour la taille de l'écran
    def update_screen_limits(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player.update_screen_limits(screen_width, screen_height)

    # Met a jour les éléments du jeu (comme le joueur)
    def update(self, keys):
        screen_scroll = self.player.move(keys, self.screen_rect)
        self.player.update()
        self.weapon.update(self.player)

    # Dessine et affiche les éléments du jeu
    def draw(self, screen):
        screen.fill(self.background_color)  # Dessine le fond
        self.player.draw(screen)  # Dessine le joueur
        self.weapon.draw(screen) # Dessine l'arme

    # Réinitialise le jeu
    def reset(self):
        self.player.rect.x = self.screen_width // 2
        self.player.rect.y = self.screen_height // 2
