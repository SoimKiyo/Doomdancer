import pygame
import math
from constants import *
from ui import DamageText
from random import choice
from sfx import shoot_sound, reload_sound, attack_sound, attackvoice_sound1, attackvoice_sound2, attackvoice_sound3

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
        self.crosshair_pos = pygame.mouse.get_pos() # Mettre la position du crosshair à la position de la souris
        self.use_crosshair = True # Doit on utiliser le crosshair ?

        # Munitions et rechargement
        self.max_ammo = 5  # Munitions maximales
        self.ammo = self.max_ammo  # Munitions actuelles
        self.reloading = False # Est ce qu'on recharge ?
        self.reload_time = 1500  # Temps de rechargement en millisecondes
        self.last_reload = pygame.time.get_ticks()
        self.next_reload_time = 0  # Prochaine fin de rechargement
        
    # Fonction pour mettre à jour l'arme
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
                if abs(x) > 0.15 or abs(y) > 0.15: # Marge minimum pour considérer le joystick comme en mouvement
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


        # Priorisation quand manette et souris sont utilisés
        if joy_recent and mouse_recent:
            # Combinaison avec pondération : 80 % joystick et 20 % souris
            weight_joy = 0.8
            weight_mouse = 0.2
            # Calcul des longueurs des vecteurs de visée
            len_joy = math.hypot(aim_joy[0], aim_joy[1])
            len_mouse = math.hypot(aim_mouse[0], aim_mouse[1])
            # Normalisation des vecteurs de visée
            joy_norm = (aim_joy[0] / len_joy, aim_joy[1] / len_joy) if len_joy != 0 else (0, 0)
            mouse_norm = (aim_mouse[0] / len_mouse, aim_mouse[1] / len_mouse) if len_mouse != 0 else (0, 0)
            # Calcul de la moyenne pondérée des vecteurs normalisés
            combined_x = weight_joy * joy_norm[0] + weight_mouse * mouse_norm[0]
            combined_y = weight_joy * joy_norm[1] + weight_mouse * mouse_norm[1]
            # Calcul de la longueur du vecteur combiné
            combined_length = math.hypot(combined_x, combined_y)
            # Normalisation du vecteur combiné pour obtenir la direction de visée finale
            if combined_length != 0:
                aim_direction = (combined_x / combined_length, combined_y / combined_length)
            else:
                aim_direction = (1, 0)  # Direction par défaut si la longueur est nulle
        elif joy_recent:
            # Si seule la manette a été utilisée récemment
            aim_direction = aim_joy
        elif mouse_recent:
            # Si seule la souris a été utilisée récemment
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
        

        # Rechargement
        if self.reloading and current_time - self.last_reload >= self.reload_time:
            self.ammo = self.max_ammo
            self.reloading = False

        if  pygame.key.get_pressed()[pygame.K_r]:  # Clavier (touche R)
            current_time = pygame.time.get_ticks()
            if not self.reloading and self.ammo < self.max_ammo:
                reload_sound.play()
                self.reloading = True
                self.last_reload = current_time
                self.next_reload_time = pygame.time.get_ticks() + self.reload_time  # Définit le moment où le rechargement se termine

        for joystick in self.joysticks:
            if joystick.get_numbuttons() > 2:
                x_pressed = joystick.get_button(2)  # Bouton X
                if x_pressed:
                    current_time = pygame.time.get_ticks()
                    if not self.reloading and self.ammo < self.max_ammo:
                        reload_sound.play()
                        self.reloading = True
                        self.last_reload = current_time

        if self.ammo > 0 and self.reloading == False: # Si on a assez de munition et qu'on ne recharge pas
            # Tir avec la manette
            for joystick in self.joysticks:
                if joystick.get_numbuttons() > 5:
                    rb_pressed = joystick.get_button(5) # Bouton RB
                    if rb_pressed and not self.fired_joystick and (current_time - self.last_shot >= shot_cooldown):
                        projectile = Projectile(self.projectile_image, self.rect.centerx, self.rect.centery, self.angle)
                        self.fired_joystick = True # On marque qu'on a tiré avec la manette
                        self.last_shot = current_time
                        self.ammo -= 1 # Retire une balle pour chaque tire
                        shoot_sound.play()  # Joue le son du tir
                    if not rb_pressed:
                        self.fired_joystick = False

            # Tir avec la souris
            if pygame.mouse.get_pressed()[0] and not self.fired and (current_time - self.last_shot >= shot_cooldown): # Clique gauche
                projectile = Projectile(self.projectile_image, self.rect.centerx, self.rect.centery, self.angle)
                self.fired = True # On marque qu'on a tiré avec la souris
                self.last_shot = current_time
                self.ammo -= 1
                shoot_sound.play()  # Joue le son du tir
            if not pygame.mouse.get_pressed()[0]:
                self.fired = False

        # Rechargement automatique
        if self.ammo <= 0 and self.reloading == False and (self.fired_joystick or self.fired):
            self.reloading = True
            reload_sound.play()
            self.last_reload = current_time
            
        return projectile

    # Fonction pour dessiner l'arme
    def draw(self, surface, player):
        if player.hide_weapon or player.dash_active:
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
            surface.blit(self.crosshair_image, (mouse_x - self.crosshair_image.get_width() // 2, mouse_y - self.crosshair_image.get_height() // 2))

# Classe des projectiles
class Projectile(pygame.sprite.Sprite):
    def __init__(self, animation_frames, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.angle = angle
        self.animation_frames = animation_frames # La liste des frames d'animation
        self.frame_index = 0 # Frame courante
        self.update_time = pygame.time.get_ticks() # Temps de la dernière mise à jour
        self.animation_cooldown = 100 # Cooldown en ms entre chaque frame (ajuste si nécessaire)

        # Affiche la première frame avec la rotation appliquée
        self.image = pygame.transform.rotate(self.animation_frames[self.frame_index], self.angle - 90)
        self.rect = self.image.get_rect(center=(x, y))

        # Calcul de la vitesse en fonction de l'angle
        self.dx = math.cos(math.radians(self.angle)) * PROJECTILE_SPEED
        self.dy = math.sin(math.radians(self.angle)) * PROJECTILE_SPEED

    # Fonction pour mettre à jour les projectiles
    def update(self, screen_scroll, enemy_list):
        damage = 0
        damage_pos = None
        current_time = pygame.time.get_ticks()

        # Changer de frame si le cooldown est écoulé
        if current_time - self.update_time > self.animation_cooldown:
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames)
            self.update_time = current_time

        # Mettre à jour l'image en appliquant la rotation sur la frame courante
        self.image = pygame.transform.rotate(self.animation_frames[self.frame_index], self.angle - 90)

        # Déplacement du projectile
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy

        # Suppression si le projectile sort de l'écran
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT): 
            self.kill()

        # Détection de collision avec les ennemis
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                damage = 10 # Fait un dégât de 10
                damage_pos = enemy.rect # On marque l'emplacement du dégât comme étant celui de l'ennemie
                enemy.health -= damage # On enlève la vie à l'ennemie
                self.kill() # On supprime le projectile
                break

        return damage, damage_pos # On renvoie les dégâts et leur positions

    # Fonction pour dessiner les projectiles
    def draw(self, surface):
        # Affichage centré du projectile
        surface.blit(self.image, (self.rect.centerx - self.image.get_width() // 2, self.rect.centery - self.image.get_height() // 2))

# Classe des attaque melee
class MeleeAttack:
    def __init__(self, joysticks, damage_text_group):
        self.joysticks = joysticks # Les manettes
        self.damage = 30 # Nombre de dégâts
        self.attack_range = 60 # Portée de l'attaque
        self.attack_cooldown = 300 # Cooldown en ms
        self.attack_duration = 500 # Durée de l'attaque en ms
        self.last_attack = 0 # Temps de la dernière attaque
        self.attacking = False # Indique si on est en pleine attaque
        self.attack_start_time = 0 # Temps de début de l'attaque
        self.next_attack_time = 0 # Prochain moment où l'attaque sera possible

        self.damage_text_group = damage_text_group

        # Nouvel attribut pour éviter les déclenchements en continu
        self.trigger_released = True

    # Fonction pour mettre à jour les attaques de corp à corp
    def update(self, player, enemy_list, coins_group):
        current_time = pygame.time.get_ticks()
        melee_trigger = False

        # Vérification de l'entrée manette (bouton RT)
        for joystick in self.joysticks:
            if joystick.get_numbuttons() > 5:
                if joystick.get_button(4):
                    melee_trigger = True
                    break
                
        # Vérification de l'entrée souris (clic droit)
        if pygame.mouse.get_pressed()[2]:
            melee_trigger = True

        # On s'assure que le joueur relâche le bouton entre deux attaques
        if not melee_trigger:
            self.trigger_released = True

        # Lancer l'attaque seulement si le bouton vient d'être pressé ET le cooldown est terminé
        if melee_trigger and self.trigger_released and (current_time - self.last_attack >= self.attack_cooldown):
            self.attacking = True
            self.last_attack = current_time
            self.attack_start_time = current_time
            self.trigger_released = False  # On bloque jusqu'au prochain relâchement

            # On active l'animation d'attaque sur le joueur
            player.is_attacking = True

            # Cache l'arme pendant l'attaque
            player.hide_weapon = True

            # Joue le son d'attaque
            attack_sound.play()
            voice_sounds = [attackvoice_sound1, attackvoice_sound2, attackvoice_sound3]
            choice(voice_sounds).play()

            # Définit le prochain temps d'attaque
            self.next_attack_time = current_time + self.attack_cooldown

            # Définition de la hitbox pour l'attaque
            if player.flip:
                # Si le joueur regarde à gauche, la hitbox se place à gauche
                melee_rect = pygame.Rect(player.rect.left - self.attack_range, player.rect.top, self.attack_range, player.rect.height)
            else:
                melee_rect = pygame.Rect(player.rect.right, player.rect.top, self.attack_range, player.rect.height)

            # Collision de l'attaque avec chaque ennemi
            for enemy in enemy_list:
                if enemy.alive and melee_rect.colliderect(enemy.rect):
                    attack_sound.play()
                    enemy.take_damage(self.damage, coins_group)
                    damage_text = DamageText(enemy.rect.centerx, enemy.rect.y - 20, str(self.damage), RED, [0, 0])
                    self.damage_text_group.add(damage_text)

        # Fin de l'attaque après la durée définie
        if self.attacking and (current_time - self.attack_start_time >= self.attack_duration):
            self.attacking = False
            player.is_attacking = False
            player.hide_weapon = False # Réafficher l'arme
