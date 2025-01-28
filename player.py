import pygame
import math

# Constantes pour le joueur
PLAYER_SPEED = 5
PLAYER_COLOR = (0, 128, 255)

# Classe du joueur
class Player:
    # Initialise le joueur et ses valeurs
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)  # Rectangle du joueur
        self.rect.center = (x,y) # Positionne le personnage
        self.speed = PLAYER_SPEED  # Vitesse de déplacement
        self.screen_rect = pygame.Rect(0, 0, 800, 600)  # Limites par défaut de l'écran

    # Permet de mettre à jour les limite de la taille de l'écran
    def update_screen_limits(self, screen_width, screen_height):
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

    # Gère les déplacements de l'écran en fonction des entrées
    def move(self, keys, screen_rect):
        UP_KEYS = keys[pygame.K_z] or keys[pygame.K_UP]
        DOWN_KEYS = keys[pygame.K_s] or keys[pygame.K_DOWN]
        RIGHT_KEYS = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        LEFT_KEYS = keys[pygame.K_q] or keys[pygame.K_LEFT]

        dx = (RIGHT_KEYS - LEFT_KEYS) * self.speed
        dy = (DOWN_KEYS - UP_KEYS) * self.speed
        # Controler la vitesse diagonale 
        if dx != 0 and dy != 0:
            dx = dx * (math.sqrt(2)/2)
            dy = dy * (math.sqrt(2)/2)
        
        # Appliquer le mouvement
        self.rect.x += dx
        self.rect.y += dy

        # Limite le joueur à l'intérieur de l'écran
        self.rect.clamp_ip(self.screen_rect)

    # Dessine et affiche le joueur
    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)
