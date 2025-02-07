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

# Classe pour afficher l'écran des PowerUp
class PowerupScreen:
    def __init__(self, powerup, font):
        self.powerup = powerup
        self.powerup_image = pygame.image.load(f"assets/images/ui/powerup/card_{self.powerup}.png").convert_alpha()
        self.card_y = SCREEN_HEIGHT  # Position initiale de la carte en dehors de l'écran
        self.card_target_y = SCREEN_HEIGHT // 2 - self.powerup_image.get_height() // 2
        self.animation_speed = 10  # Vitesse du mouvement de l'animation

        self.animation_complete = False
        self.font = font
        self.done = False  # Indique si l'écran a été fermé

    def handle_input(self, event):
        """Ferme l'écran si le joueur appuie sur A"""
        if self.animation_complete and event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            self.done = True  # Fermer l’écran
            return True
        return False
    
    def animate_card(self):
        """Animation de l'apparition de la carte"""
        if self.card_y > self.card_target_y:
            self.card_y -= self.animation_speed
        else:
            self.animation_complete = True
    
    def draw(self, screen):
        screen.fill(BLACK)  # Fond noir

        # Animation d'apparition
        if not self.animation_complete:
            self.animate_card()

        # Affichage du power-up
        screen.blit(self.powerup_image, (SCREEN_WIDTH // 2 - self.powerup_image.get_width() // 2, self.card_y))

        # Texte d'instruction
        if self.animation_complete:
            button_text = self.font.render("Appuie sur A pour continuer", True, WHITE)
            button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(button_text, button_rect)