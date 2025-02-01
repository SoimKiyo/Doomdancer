# weapon.py

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
        self.flip = False  # Permet de tourner l'image de l'arme
        self.using_right_stick = False
        self.using_mouse = False 

    def update(self, player):
        shot_cooldown = 200
        projectile = None
        # L'arme reste centrée sur le joueur
        self.rect.center = player.rect.center

        aim_direction = None

        # Priorité : si le stick droit est utilisé, on se base dessus pour viser
        for joystick in self.joysticks:
            if joystick.get_numaxes() >= 4:
                horiz_move = joystick.get_axis(2)
                vert_move = joystick.get_axis(3)
                # Vérifier si le stick droit est suffisamment dévié pour viser
                if abs(horiz_move) > 0.15 or abs(vert_move) > 0.15:
                    self.using_right_stick = True
                    aim_direction = (horiz_move, vert_move)
                    player.flip = horiz_move < 0  # Flip du joueur selon la visée
                    break
                else:
                    self.using_right_stick = False

        # Sinon, si le joueur se déplace (clavier/D-Pad), on utilise cette direction pour viser
        if aim_direction is None:
            if player.running and (player.last_dx != 0 or player.last_dy != 0):
                aim_direction = (player.last_dx, player.last_dy)
            else:
                # Fallback : utilisation de la souris pour viser
                mouse_pos = pygame.mouse.get_pos()
                dx = mouse_pos[0] - self.rect.centerx 
                dy = mouse_pos[1] - self.rect.centery 
                aim_direction = (dx, dy)
                self.using_mouse = True
                player.flip = mouse_pos[0] < self.rect.centerx

        # Calcul de l'angle à partir de la direction de visée obtenue
        self.angle = math.degrees(math.atan2(aim_direction[1], aim_direction[0]))
        self.flip = self.angle > 90 or self.angle < -90  # Flip si l'arme vise à gauche

        # Gestion du tir via la manette (par exemple, bouton RB)
        for joystick in self.joysticks:
            if joystick.get_numbuttons() > 5:  # Vérifie si la manette a au moins 6 boutons
                rb_pressed = joystick.get_button(5)  # Bouton RB (Right Bumper)
                if rb_pressed and not self.fired_joystick and (pygame.time.get_ticks() - self.last_shot >= shot_cooldown):
                    projectile = Projectile(self.projectile_image, self.rect.centerx, self.rect.centery, self.angle)
                    self.fired_joystick = True
                    self.last_shot = pygame.time.get_ticks()
                if not rb_pressed:
                    self.fired_joystick = False

        # Gestion du tir via la souris
        if pygame.mouse.get_pressed()[0] and not self.fired and (pygame.time.get_ticks() - self.last_shot >= shot_cooldown):
            projectile = Projectile(self.projectile_image, self.rect.centerx, self.rect.centery, self.angle)
            self.fired = True
            self.last_shot = pygame.time.get_ticks()
        if not pygame.mouse.get_pressed()[0]:
            self.fired = False
            
        return projectile

    def draw(self, surface):
        # Appliquer le flip à l'image d'origine AVANT la rotation
        image_to_draw = self.original_image 
        if self.flip: 
            image_to_draw = pygame.transform.flip(self.original_image, False, True)  # Flip vertical pour garder l'arme dans le bon sens 
        # Appliquer la rotation
        rotated_image = pygame.transform.rotate(image_to_draw, -self.angle)
        # Obtenir le nouveau rectangle après rotation
        new_rect = rotated_image.get_rect(center=self.rect.center)
        # Affichage de l'arme
        surface.blit(rotated_image, new_rect.topleft)

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
        # Repositionner le projectile selon sa vitesse et le défilement de l'écran
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy
        # Vérifier si le projectile est hors de l'écran
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()
        # Vérifier la collision entre le projectile et les ennemis
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                damage = 10 + random.randint(-5, 5)
                damage_pos = enemy.rect
                enemy.health -= damage
                self.kill()
                break
        return damage, damage_pos
         
    def draw(self, surface): 
        surface.blit(self.image, ((self.rect.centerx - self.image.get_width() // 2),
                                   (self.rect.centery - self.image.get_height() // 2)))
