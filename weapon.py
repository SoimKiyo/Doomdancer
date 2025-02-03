import pygame
import math
import random
from constants import *
from ui import DamageText

# Classe de l'arme
class Weapon():
    def __init__(self, image, joysticks, projectile_image):
        # Initialisation des images et paramètres de l'arme
        self.original_image = image # Image de l'arme sans modification
        self.angle = 0 # Angle pour orienter l'arme
        self.image = pygame.transform.rotate(self.original_image, self.angle) # L'image orienter
        self.rect = self.image.get_rect() 
        self.projectile_image = projectile_image # L'image du projectile
        self.joysticks = joysticks # Les Manettes

        # Variables pour le tir
        self.fired = False # Est ce qu'on a tiré ?
        self.fired_joystick = False # Est ce qu'on a tiré avec la manette ?
        self.last_shot = pygame.time.get_ticks() # Temps avant le dernier tir

        # Indicateur de flip (pour retourner l'image)
        self.flip = False

        # Derniere utilisations de chaque entrées
        self.last_mouse_time = 0
        self.last_joystick_time = 0

        self.crosshair_image = pygame.image.load("assets/images/weapons/crosshair.png").convert_alpha()  # Charge l'image du crosshair
        self.crosshair_pos = pygame.mouse.get_pos()
        self.use_crosshair = True
        

    def update(self, player):
        shot_cooldown = 200
        projectile = None
        current_time = pygame.time.get_ticks()

       # Entrées de la Manette (Joystick)
        aim_joy = None
        joystick_active = False
        for joystick in self.joysticks:
            if joystick.get_numaxes() >= 4: # Joystick droit
                x = joystick.get_axis(2)
                y = joystick.get_axis(3)
                if abs(x) > 0.15 or abs(y) > 0.15:
                    aim_joy = (x, y)
                    self.last_joystick_time = current_time
                    joystick_active = True
                    break  # On prend le premier Joystick actif

        # Entrées de la Souris
        aim_mouse = None
        mouse_active = False
        if player.using_mouse and player.last_mouse_pos:
            dx = player.last_mouse_pos[0] - player.rect.centerx
            dy = player.last_mouse_pos[1] - player.rect.centery
            if math.hypot(dx, dy) > 5:  # Seuil pour ignorer les petits mouvements
                aim_mouse = (dx, dy)
                self.last_mouse_time = current_time 
                mouse_active = True

        if aim_mouse is not None:
            self.crosshair_pos = pygame.mouse.get_pos()

        # On vérifie si les entrées sont récentes ou non
        joy_recent = (aim_joy is not None) and ((current_time - self.last_joystick_time) < MOUSE_TIMEOUT)
        mouse_recent = (aim_mouse is not None) and ((current_time - self.last_mouse_time) < MOUSE_TIMEOUT)

        # Détermine si le crosshair doit être affiché
        if joystick_active:
            self.use_crosshair = False  # Désactiver le crosshair si la manette est utilisée
        elif mouse_active:
            self.use_crosshair = True  # Réactiver le crosshair si la souris est utilisée


        # Prioritésation quand manette et souris sont utilisé
        if joy_recent and mouse_recent:
            # Combinaison avec pondération : 80 % joystick et 20 % souris
            weight_joy = 0.8
            weight_mouse = 0.2
            len_joy = math.hypot(aim_joy[0], aim_joy[1])
            len_mouse = math.hypot(aim_mouse[0], aim_mouse[1])
            # Normalisation des vecteurs
            joy_norm = (aim_joy[0] / len_joy, aim_joy[1] / len_joy) if len_joy != 0 else (0, 0)
            mouse_norm = (aim_mouse[0] / len_mouse, aim_mouse[1] / len_mouse) if len_mouse != 0 else (0, 0)
            # Calcul de la moyenne pondérée
            combined_x = weight_joy * joy_norm[0] + weight_mouse * mouse_norm[0]
            combined_y = weight_joy * joy_norm[1] + weight_mouse * mouse_norm[1]
            combined_length = math.hypot(combined_x, combined_y)
            if combined_length != 0:
                aim_direction = (combined_x / combined_length, combined_y / combined_length)
            else:
                aim_direction = (1, 0)
        elif joy_recent:
            aim_direction = aim_joy
        elif mouse_recent:
            aim_direction = aim_mouse
        else:
            # Si aucun input récent, utiliser la dernière direction du joueur (ou viser par défaut à droite)
            if (player.last_dx, player.last_dy) != (0, 0):
                aim_direction = (player.last_dx, player.last_dy)
            else:
                aim_direction = (1, 0)

        # Calcul de l'angle et mise à jour de la rotation des sprites
        self.angle = math.degrees(math.atan2(aim_direction[1], aim_direction[0]))
        self.flip = (self.angle > 90 or self.angle < -90)
        player.flip = (aim_direction[0] < 0)

        # Positionnement de l'arme en fonction de la direction du sprite du joueur
        if player.flip:
            self.rect.center = (player.rect.centerx - WEAPON_OFFSET_X, player.rect.centery + WEAPON_OFFSET_Y)
        else:
            self.rect.center = (player.rect.centerx + WEAPON_OFFSET_X, player.rect.centery + WEAPON_OFFSET_Y)

        # Tir avec la manette
        for joystick in self.joysticks:
            if joystick.get_numbuttons() > 5:
                rb_pressed = joystick.get_button(5) # Bouton RB
                if rb_pressed and not self.fired_joystick and (current_time - self.last_shot >= shot_cooldown):
                    projectile = Projectile(self.projectile_image, self.rect.centerx, self.rect.centery, self.angle)
                    self.fired_joystick = True
                    self.last_shot = current_time
                if not rb_pressed:
                    self.fired_joystick = False

        # Tir avec la souris
        if pygame.mouse.get_pressed()[0] and not self.fired and (current_time - self.last_shot >= shot_cooldown): # Clique gauche
            projectile = Projectile(self.projectile_image, self.rect.centerx, self.rect.centery, self.angle)
            self.fired = True
            self.last_shot = current_time
        if not pygame.mouse.get_pressed()[0]:
            self.fired = False

        return projectile

    def draw(self, surface, player):
        if player.hide_weapon:
            return
            
        # Retourner l'image si nécessaire avant la rotation
        image_to_draw = self.original_image
        if self.flip:
            image_to_draw = pygame.transform.flip(self.original_image, False, True)
        # Appliquer la rotation en fonction de l'angle
        rotated_image = pygame.transform.rotate(image_to_draw, -self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect.topleft)
        # Afficher le crosshair uniquement si la souris est utilisée
        if self.use_crosshair:
            mouse_x, mouse_y = self.crosshair_pos
            surface.blit(self.crosshair_image, (mouse_x - self.crosshair_image.get_width() // 2,
                                                mouse_y - self.crosshair_image.get_height() // 2))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.angle = angle
        # Rotation de l'image de la projectile (ajustement de 90°)
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # Calcul de la vitesse en fonction de l'angle
        self.dx = math.cos(math.radians(self.angle)) * PROJECTILE_SPEED
        self.dy = math.sin(math.radians(self.angle)) * PROJECTILE_SPEED

    def update(self, screen_scroll, enemy_list):
        damage = 0
        damage_pos = None
        # Déplacement de la projectile
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy
        # Suppression si hors de l'écran
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()
        # Détection de collision avec un ennemi
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                damage = 10 + random.randint(-5, 5)
                damage_pos = enemy.rect
                enemy.health -= damage
                self.kill()
                break
        return damage, damage_pos

    def draw(self, surface):
        # Affichage centré de la projectile
        surface.blit(self.image, (
            self.rect.centerx - self.image.get_width() // 2,
            self.rect.centery - self.image.get_height() // 2
        ))


class MeleeAttack:
    def __init__(self, joysticks, damage_text_group):
        self.joysticks = joysticks # Les manettes
        self.damage = 30 # Nombre de dégâts
        self.attack_range = 50 # Porté de l'attaque
        self.attack_cooldown = 300 # Temps avant de pouvoir réattaquer
        self.attack_duration = 300 # Temps de l'attaque
        self.last_attack = 0 # Depuis combien temps a était faite la dernier attaque
        self.attacking = False # Somme nous entrain d'attaquer ?
        self.attack_start_time = 0 # Depuis quand a commencer l'attaque

        self.damage_text_group = damage_text_group

    def update(self, player, enemy_list, coins_group):
        current_time = pygame.time.get_ticks()
        melee_trigger = False

        # Vérifier l'entrée de la manette (bouton A)
        for joystick in self.joysticks:
            if joystick.get_numbuttons() > 0 and joystick.get_button(0):
                melee_trigger = True
                break

        # Vérifier l'entrée de la souris (clic droit)
        if pygame.mouse.get_pressed()[2]:
            melee_trigger = True

        # Lancer l'attaque si le cooldown est écoulé
        if melee_trigger and (current_time - self.last_attack >= self.attack_cooldown):
            self.attacking = True
            self.last_attack = current_time
            self.attack_start_time = current_time
            # On active le mode "attaque" sur le joueur pour bloquer l’animation
            player.is_attacking = True
            # On met l’animation melee
            #player.update_action("melee")

            # Cache l'arme pendant l'attaque
            player.hide_weapon = True
            
            # Hitbox pour l'attaque
            if player.flip:
                # Si le joueur regarde à gauche, la hitbox est à gauche
                melee_rect = pygame.Rect(player.rect.left - self.attack_range, player.rect.top, self.attack_range, player.rect.height)
            else:
                # Sinon, à droite
                melee_rect = pygame.Rect(player.rect.right, player.rect.top, self.attack_range, player.rect.height)
            
            # On vérifie la collision avec chaque ennemi
            for enemy in enemy_list:
                if enemy.alive and melee_rect.colliderect(enemy.rect):
                    enemy.take_damage(self.damage, coins_group)
                    damage_text = DamageText(enemy.rect.centerx, enemy.rect.y - 20, str(self.damage), RED, [0, 0])
                    self.damage_text_group.add(damage_text)

        # Fin de l'attaque après la durée définie
        if self.attacking and (current_time - self.attack_start_time >= self.attack_duration):
            self.attacking = False
            player.is_attacking = False
            player.hide_weapon = False  # Réaffiche l'arme après l'attaque
