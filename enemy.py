import pygame
import math

# Constantes pour l'ennemie
ENEMY_SPEED = 4
ENEMY_COLOR = (255, 128, 0)

# Classe de l'enemie
class Enemy:
    # Initialise l'ennemie et ses valeurs
    def __init__(self, x, y, health, width, height):
        self.rect = pygame.Rect(x, y, width, height)  # Rectangle de l'ennemie
        self.rect.center = (x,y) # Positionne l'ennemie
        self.speed = ENEMY_SPEED  # Vitesse de déplacement
        self.health = health # Vie de l'ennemie

        # Controler la vitesse diagonale 
        if dx != 0 and dy != 0:
            dx = dx * (math.sqrt(2)/2)
            dy = dy * (math.sqrt(2)/2)
        
        # Appliquer le mouvement
        self.rect.x += dx
        self.rect.y += dy

    # Dessine et affiche l'ennemie
    def draw(self, surface):
        pygame.draw.rect(surface, ENEMY_COLOR, self.rect)