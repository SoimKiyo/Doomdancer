import pygame
from constants import *
import random

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/images/items/fragments.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE//2, TILE_SIZE//2))  # Taille ajustée
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Effet de dispersion
        self.vel_x = random.uniform(-2, 2)  # Déplacement horizontal
        self.vel_y = random.uniform(-2, 2)  # Déplacement vertical
        self.friction = 0.95  # Ralentissement progressif

    def update(self, screen_scroll, player):
        # Appliquer le scrolling de l'écran
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        # Appliquer la dispersion et ralentir progressivement
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.vel_x *= self.friction
        self.vel_y *= self.friction

        # Détection de collision avec le joueur
        if self.rect.colliderect(player.rect):
            player.collect_coin()  # Augmente le compteur de pièces
            self.kill()  # Supprime la pièce

    def draw(self, screen):
        screen.blit(self.image, self.rect)