import pygame

# Constantes pour le joueur
PLAYER_SPEED = 5
PLAYER_COLOR = (0, 128, 255)

# Classe du joueur
class Player:
    # Initialise le joueur et ses valeurs
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)  # Rectangle du joueur
        self.speed = PLAYER_SPEED  # Vitesse de déplacement
        self.screen_rect = pygame.Rect(0, 0, 800, 600)  # Limites par défaut de l'écran

    # Permet de mettre à jour les limite de la taille de l'écran
    def update_screen_limits(self, screen_width, screen_height):
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

    # Gère les déplacements de l'écran en fonction des entrées
    def move(self, keys, screen_rect):
        if keys[pygame.K_z] or keys[pygame.K_UP]:  # Haut
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  # Bas
            self.rect.y += self.speed
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:  # Gauche
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:  # Droite
            self.rect.x += self.speed

        # Limite le joueur à l'intérieur de l'écran
        self.rect.clamp_ip(self.screen_rect)

    # Dessine et affiche le joueur
    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)
