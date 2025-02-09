import pygame
import math
from constants import *
from random import choice
from map import world_data
from sfx import collect_sound, damage_sound, damagevoice_sound1, damagevoice_sound2, damagevoice_sound3, moveongrass_sound, moveonrock_sound, death_sound, dash_sound

joysticks = []  # Liste vide pour stocker les manettes

def scale_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (int(w * scale), int(h * scale)))

def player_animations():
    # Dictionnaire contenant les types d'animations et leur nombre de frames 
    animation_frames = { 
        "idle": 30, 
        "run": 8,
        "slash": 11
    }
    animation_list = {key: [] for key in animation_frames}  # Dictionnaire pour stocker les animations 
    for animation, num_frames in animation_frames.items():
        for i in range(num_frames):
            # Charger chaque sprite et le redimensionner
            img = pygame.image.load(f"assets/images/player/{animation}/{i}.png").convert_alpha()
            img = scale_img(img, SCALE)
            animation_list[animation].append(img)
    return animation_list

class Player:
    def __init__(self, x, y, width, height, animation_list):
        # Animation / Sprite du personnage
        self.flip = False  # Permet de retourner l'image du joueur
        self.animation_list = animation_list
        self.frame_index = 0  # Frame de départ
        self.action = "idle"
        self.update_time = pygame.time.get_ticks()  # Temps de mise à jour de l'animation
        self.running = False
        self.is_attacking = False
        self.image = self.animation_list[self.action][self.frame_index]
        # Rectangle du joueur
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.center = (x, y)
        self.speed = PLAYER_SPEED  # Vitesse de déplacement
        self.screen_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)  # Limites de l'écran
        # Création d'une hitbox
        self.hitbox = pygame.Rect(0, 0, width - 10, height - 10)
        self.hitbox.center = self.rect.center

        self.hide_weapon = False
        
        # Vie du joueur
        self.max_health = 100  # Vie maximale
        self.health = self.max_health  # Vie actuelle
        self.alive = True
        self.is_invincible = False  # Empêche les dégâts en boucle
        self.invincibility_timer = 0  # Temps d'invincibilité après un coup
        self.deaths = 0  # Nombre de fois où le joueur est mort

        self.coins = 0 # Nombre de fragments du joueur

        # Pour mémoriser la dernière direction de déplacement (normalisée)
        self.last_dx = 0
        self.last_dy = 0
        # Pour conserver la dernière position connue de la souris
        self.last_mouse_pos = None
        self.using_mouse = False # La souris est-elle utilisé ?

        self.using_gamepad = False  # Indique si le joueur utilise une manette

        self.last_step_sound_time = 0
        self.distance_since_last_step = 0

        self.dash_active = False
        self.dash_duration = 300 # Durée du dash en millisecondes
        self.dash_cooldown = 1300 # Cooldown entre dash
        self.last_dash_time = 0
        self.dash_multiplier = 3 # Facteur de multiplication de la vitesse durant le dash
        self.dash_trigger_released = True # Pour éviter les déclenchements répétés


    def update_screen_limits(self, screen_width, screen_height):
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

    def collect_coin(self):
        self.coins += 1
        collect_sound.play()

    def move(self, keys, screen_rect, weapon, obstacle_tiles, exit_tile):
        if self.alive == False:  # Si le joueur est mort, il ne peut pas bouger
            return [0, 0], False

        screen_scroll = [0, 0]
        level_complete = False
        self.running = False

        # Entrées clavier (ZQSD/Flèches directionnel)
        dx_keyboard = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_q] or keys[pygame.K_LEFT])
        dy_keyboard = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_z] or keys[pygame.K_UP])
        
        # Entrées manettes (Dpad/Joystick Gauche)
        dx_gamepad = 0
        dy_gamepad = 0
        for joystick in joysticks:
            # Joystick gauche
            if joystick.get_numaxes() >= 2:
                horiz_move = joystick.get_axis(0)
                vert_move = joystick.get_axis(1)
                if abs(horiz_move) > 0.15:
                    dx_gamepad += horiz_move
                if abs(vert_move) > 0.15:
                    dy_gamepad += vert_move
            # D-Pad
            if joystick.get_numhats() > 0:
                hat_x, hat_y = joystick.get_hat(0)
                if hat_x != 0:
                    dx_gamepad += hat_x
                if hat_y != 0:
                    dy_gamepad -= hat_y
        # Vérifie si le joueur utilise une manette
        self.using_gamepad = any(abs(joystick.get_axis(0)) > 0.15 or abs(joystick.get_axis(1)) > 0.15 for joystick in joysticks)


        # Calcul du déplacement total
        dx = dx_keyboard + dx_gamepad
        dy = dy_keyboard + dy_gamepad

        # Mise à jour de l'info sur la souris
        rel = pygame.mouse.get_rel()  # Renvoie le mouvement relatif depuis le dernier appel
        if rel != (0, 0):
            self.using_mouse = True
            self.last_mouse_pos = pygame.mouse.get_pos()
        # Si aucun mouvement n'est détecté et qu'on n'a jamais eu d'info sur la souris, on garde les mouvements du clavier
        elif self.last_mouse_pos is None:
            self.using_mouse = False

        # Gestion du dash
        current_time = pygame.time.get_ticks()
        dash_input = keys[pygame.K_SPACE]
        for joystick in joysticks:
            if joystick.get_button(0):
                dash_input = True
                break

        if dash_input:
            if self.dash_trigger_released and (current_time - self.last_dash_time >= self.dash_cooldown) and not self.dash_active:
                dash_sound.play()
                self.dash_active = True
                self.dash_trigger_released = False
                self.last_dash_time = current_time
                self.dash_start_time = current_time
        else:
            self.dash_trigger_released = True
        
        # Si le dash est actif, on force l'invincibilité
        if self.dash_active:
            self.is_invincible = True

        # Si le joueur se déplace
        if dx != 0 or dy != 0:
            self.running = True
            # Priorité à la souris pour le flip si elle a bougé
            if self.using_mouse and self.last_mouse_pos:
                self.flip = self.last_mouse_pos[0] < self.rect.centerx
            # Sinon, on se base sur la direction clavier (ou manette)
            else:
                # Pour le clavier (dx_keyboard)
                if dx_keyboard != 0:
                    self.flip = dx_keyboard < 0
                # Pour la manette (si aucun input clavier)
                elif dx_gamepad != 0:
                    self.flip = dx_gamepad < 0

            # Normalisation de la direction pour conserver le dernier vecteur de déplacement
            norm = math.sqrt(dx ** 2 + dy ** 2)
            if norm != 0:
                norm_dx = dx / norm
                norm_dy = dy / norm
            else:
                norm_dx, norm_dy = 0, 0

            self.last_dx = norm_dx
            self.last_dy = norm_dy

            # Appliquer le dash si actif
            if self.dash_active:
                dx = norm_dx * self.speed * self.dash_multiplier
                dy = norm_dy * self.speed * self.dash_multiplier
            else:
                dx = norm_dx * self.speed
                dy = norm_dy * self.speed

        # Appliquer le déplacement et regarder les collisions
        self.rect.x += dx
        for obstacle in obstacle_tiles:
            # Regarder les collisions
            if obstacle[1].colliderect(self.rect):
                # Regarder de qu'elle côté et la collision
                if dx > 0:
                    self.rect.right = obstacle[1].left
                if dx < 0:
                    self.rect.left = obstacle[1].right
        self.rect.y += dy
        for obstacle in obstacle_tiles:
            # Regarder les collisions
            if obstacle[1].colliderect(self.rect):
                # Regarder de qu'elle côté et la collision
                if dy > 0:
                    self.rect.bottom = obstacle[1].top
                if dy < 0:
                    self.rect.top = obstacle[1].bottom

        # Mise à jour de la hitbox pour qu'elle suive le joueur
        self.hitbox.center = self.rect.center

        # Vérifier la collission avec l'élément permettant de changer de niveau
        for tile in exit_tile:
            if tile[1].colliderect(self.rect):
                level_complete = True
                break

        # Défilement de l'écran en fonction de la position du joueur
        if self.rect.right > (SCREEN_WIDTH - SCROLL_THRESH):
            screen_scroll[0] = (SCREEN_WIDTH - SCROLL_THRESH) - self.rect.right
            self.rect.right = SCREEN_WIDTH - SCROLL_THRESH
        if self.rect.left < SCROLL_THRESH:
            screen_scroll[0] = SCROLL_THRESH - self.rect.left
            self.rect.left = SCROLL_THRESH
        if self.rect.bottom > (SCREEN_HEIGHT - SCROLL_THRESH):
            screen_scroll[1] = (SCREEN_HEIGHT - SCROLL_THRESH) - self.rect.bottom
            self.rect.bottom = SCREEN_HEIGHT - SCROLL_THRESH
        if self.rect.top < SCROLL_THRESH:
            screen_scroll[1] = SCROLL_THRESH - self.rect.top
            self.rect.top = SCROLL_THRESH

        if self.running:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_step_sound_time >= 300:  # 200 ms entre chaque son
                tile_x = self.rect.centerx // TILE_SIZE
                tile_y = self.rect.centery // TILE_SIZE
                if tile_y < len(world_data) and tile_x < len(world_data[0]):
                    tile_value = world_data[tile_y][tile_x]
                    if 12 < tile_value < 29:  # Si c'est de la pierre
                        moveonrock_sound.play()
                    else:
                        moveongrass_sound.play()
                self.last_step_sound_time = current_time

        # Fin du dash après la durée définie
        if self.dash_active and (current_time - self.dash_start_time >= self.dash_duration):
            self.dash_active = False

        return screen_scroll, level_complete
    
    def take_damage(self, damage):
        # Si le dash est actif, on ignore les dégâts
        if self.dash_active:
            return
        if not self.is_invincible:
            self.health -= damage
            damage_sound.play()
            voice_sounds = [damagevoice_sound1, damagevoice_sound2, damagevoice_sound3]
            choice(voice_sounds).play()
            if self.health <= 0:
                self.health = 0  # Empêche la vie d'aller en dessous de 0
                death_sound.play()
                self.alive = False
                self.deaths += 1
            #self.is_invincible = True
            self.invincibility_timer = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        animation_cooldown = 60  # Valeur par défaut

        if self.is_attacking:
            self.update_action("slash")
            animation_cooldown = 60
        elif self.running:
            self.update_action("run")
            animation_cooldown = 100
        else:
            self.update_action("idle")
            animation_cooldown = 60

        self.image = self.animation_list[self.action][self.frame_index]
        if current_time - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = current_time
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

        if self.is_invincible and current_time - self.invincibility_timer > 1000:
            self.is_invincible = False  # Désactive l'invincibilité après 1 seconde

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        if not self.dash_active:
            flipped_image = pygame.transform.flip(self.image, self.flip, False)
            # Positionner le sprite par rapport à la hitbox
            surface.blit(flipped_image, (self.hitbox.x - SCALE * OFFSET_X, self.hitbox.y - SCALE * OFFSET_Y))
        # Dessine la hitbox (optionnel, pour le debug)
        #pygame.draw.rect(surface, PLAYER_COLOR, self.hitbox, 1)


class PowerUP:
    def __init__(self, player, activepowerups):
        self.player = player
        self.activepowerups = activepowerups
        self.apply_powerups()  # Appliquer immédiatement les effets

    def apply_powerups(self):
        # Powerup "speed" : double la vitesse s'il est actif
        if "speed" in self.activepowerups:
            self.player.speed = PLAYER_SPEED * 2
        else:
            self.player.speed = PLAYER_SPEED

        # Powerup "heal" : augmente le max_health et applique un bonus de soin une seule fois
        if "heal" in self.activepowerups:
            self.player.max_health = 200
            # On applique le bonus de soin uniquement s'il n'a pas déjà été appliqué
            if not hasattr(self.player, "heal_applied") or not self.player.heal_applied:
                self.player.health = min(self.player.health + 50, self.player.max_health)
                self.player.heal_applied = True
        else:
            self.player.max_health = 100
            # Réinitialiser le flag au cas où le joueur perd le powerup
            self.player.heal_applied = False
