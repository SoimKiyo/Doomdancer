import pygame 
import math
import random
from constants import *

class Weapon():
    def __init__(self, image, joysticks, projectile_image):
        self.original_image = image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.projectile_image = projectile_image
        self.joysticks = joysticks
        self.fired = False
        self.fired_joystick = False
        self.last_shot = pygame.time.get_ticks()

    def update(self, player):
            shot_cooldown = 200
            projectile = None
            self.rect.center = player.rect.center

            # Récupère la position de la souris par défaut
            pos = pygame.mouse.get_pos()

            for joystick in self.joysticks:
                if joystick.get_numaxes() >= 4:
                    horiz_move = joystick.get_axis(2)
                    vert_move = joystick.get_axis(3)

                    if (abs(horiz_move) or abs(vert_move)) > 0.15:
                        pos = (self.rect.centerx + horiz_move, self.rect.centery + vert_move)
                    
                if joystick.get_numaxes() >= 5:
                    trigger_value = joystick.get_axis(5)  # Gâchette droite

                    # Vérifier si la gâchette est suffisamment pressée (exemple : plus de 0.5)
                    if trigger_value > 0.5 and self.fired_joystick == False and (pygame.time.get_ticks() - self.last_shot >= shot_cooldown):
                        projectile = Projectile(self.projectile_image, self.rect.centerx, self.rect.centery, self.angle)
                        self.fired_joystick = True
                        self.last_shot = pygame.time.get_ticks()
                    if trigger_value <= 0.1:
                        self.fired_joystick = False

            # Calcul de l'angle entre la position actuelle et la cible
            x_dist = pos[0] - self.rect.centerx
            y_dist = pos[1] - self.rect.centery

            self.angle = math.degrees(math.atan2(y_dist, x_dist))

            # Clique de la souris pour tirer
            if pygame.mouse.get_pressed()[0] and self.fired == False and (pygame.time.get_ticks() - self.last_shot >= shot_cooldown):
                projectile = Projectile(self.projectile_image, self.rect.centerx, self.rect.centery, self.angle)
                self.fired = True
                self.last_shot = pygame.time.get_ticks()
            if pygame.mouse.get_pressed()[0] == False:
                self.fired = False
            
            return projectile

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), self.rect.centery - int(self.image.get_height()/2)))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Calculer la vitesse horizontal/vertical en fonction de l'angle
        self.dx = math.cos(math.radians(self.angle)) * PROJECTILE_SPEED
        self.dy = math.sin(math.radians(self.angle)) * PROJECTILE_SPEED

    def update(self, screen_scroll, enemy_list):
        damage = 0
        damage_pos = None

        # Repositionner par rapport à la vitesse
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy

        # Vérifier que les projectiles soit hors de l'écran
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()
        
        # Vérifier la collision entre ennemies/projectile
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                damage = 10 + random.randint(-5,5)
                damage_pos = enemy.rect
                enemy.health -= damage
                self.kill()
                break
        
        return damage, damage_pos
        
    def draw(self, surface):
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), self.rect.centery - int(self.image.get_height()/2)))