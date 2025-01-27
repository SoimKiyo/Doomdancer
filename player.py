import pygame

# Constantes pour le joueur
playerSpeed = 5
playerColor = (0, 128, 255)

#Classe du joueur
class Player:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = playerSpeed

    def move(self, keys, screen_rect):
        if keys[pygame.K_z] or keys[pygame.k_UP]:  #Haut
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.k_DOWN]:  #Bas
            self.rect.y += self.speed
        if keys[pygame.K_q] or keys[pygame.k_LEFT]:  #Gauche
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.k_RIGHT]:  #Droite
            self.rect.x += self.speed

        # Limiter le joueur à l'écran

        self.rect.clamp_ip(screen_rect)

    def draw(self, surface):
        pygame.draw.rect(surface, playerColor, self.rect)