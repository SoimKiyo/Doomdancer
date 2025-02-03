import pygame
from constants import *

# Classe de dégats (Affiche un texte quand il y a des dégâtes fait sur l'ennemie)
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color, screen_scroll):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("assets/other/fonts/font.otf", 24)
        self.image = self.font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0
        self.screen_scroll = screen_scroll

    def update(self):
        # Repositionner par rapport au scroll de l'écran
        self.rect.x += self.screen_scroll[0]
        self.rect.y += self.screen_scroll[1]
        
        # Déplacer le texte de dégât vers le haut
        self.rect.y -= 1
        # Supprimer le compte après quelques secondes
        self.counter += 1
        if self.counter > 30:
            self.kill()

# Classe de la bar de vie du joueur
class HealthBar:
    def __init__(self, x, y, width, height, player):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.player = player  # Référence au joueur

    def draw(self, screen):
        health_ratio = self.player.health / self.player.max_health
        pygame.draw.rect(screen, (150, 0, 0), (self.x, self.y, self.width, self.height))  # Fond rouge
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.width * health_ratio, self.height))  # Vie verte
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height), 2)  # Bordure blanche

# Classe d'animation de transition entre niveau
class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0
    
    def fade(self, screen):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 -self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete