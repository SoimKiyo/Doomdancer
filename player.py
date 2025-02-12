import pygame
import math
from constants import *
from random import choice
from map import world_data
from sfx import collect_sound, damage_sound, damagevoice_sound1, damagevoice_sound2, damagevoice_sound3, moveongrass_sound, moveonrock_sound, death_sound, dash_sound

joysticks = []  # Liste vide pour stocker les manettes

# Fonction pour redimenssioner les images
def scale_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (int(w * scale), int(h * scale)))

# Fonction pour l'animation du joueur
def player_animations():
    # Dictionnaire contenant les types d'animations et leur nombre de frames 
    animation_frames = {
        "idle": 30, 
        "run": 8,
        "slash": 11
    }
    animation_list = {key: [] for key in animation_frames}  # Dictionnaire pour stocker les animations 
    for animation, num_frames in animation_frames.items(): # Pour chacune des animations, et chacune de leur frames
        for i in range(num_frames): # Pour chaque frames
            # Charger chaque sprite et le redimensionner
            img = pygame.image.load(f"assets/images/player/{animation}/{i}.png").convert_alpha()
            img = scale_img(img, SCALE)
            animation_list[animation].append(img) # On ajoute chaque image dans la liste de l'animation
    return animation_list

# Classe du Joueur
class Player:
    def __init__(self, x, y, width, height, animation_list):
        # Animation / Sprite du personnage
        self.flip = False  # Permet de retourner l'image du joueur
        self.animation_list = animation_list
        self.frame_index = 0  # Frame de départ
        self.action = "idle" # Animation de base
        self.update_time = pygame.time.get_ticks()  # Temps de mise à jour de l'animation
        self.running = False # Le joueur est-il entrain de courir ?
        self.is_attacking = False # Le joueur est-il entrain d'attaquer ?
        self.image = self.animation_list[self.action][self.frame_index] # On récupère l'image de l'animation et de la frame donné
        # Rectangle du joueur
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.center = (x, y) # Centrer la box
        self.speed = PLAYER_SPEED  # Vitesse de déplacement
        self.screen_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)  # Limites de l'écran
        # Création d'une hitbox
        self.hitbox = pygame.Rect(0, 0, width - 10, height - 10) # Nouvelle box représentant la hitbox
        self.hitbox.center = self.rect.center # On centre la hitbox

        self.hide_weapon = False # L'arme doit-elle être caché
        
        # Vie du joueur
        self.max_health = 100 # Vie maximale
        self.health = self.max_health # Vie actuelle
        self.alive = True # Le joueur est-il vivant ?
        self.is_invincible = False # Empêche les dégâts en boucle
        self.invincibility_timer = 0 # Temps d'invincibilité après un coup
        self.deaths = 0 # Nombre de fois où le joueur est mort

        self.coins = 0 # Nombre de fragments du joueur

        # Pour mémoriser la dernière direction de déplacement (normalisée)
        self.last_dx = 0 # dernière valeur Delta X
        self.last_dy = 0 # dernière valeur Delta Y
        # Pour conserver la dernière position connue de la souris
        self.last_mouse_pos = None # Dernière position de la souris enregistré
        self.using_mouse = False # La souris est-elle utilisé ?

        self.using_gamepad = False  # Indique si le joueur utilise une manette

        self.last_step_sound_time = 0 # Dernière utilisation du son de la souris

        self.dash_active = False # Le dash est il actif (en cours d'utilisation) ?
        self.dash_duration = 300 # Durée du dash en millisecondes
        self.dash_cooldown = 1300 # Cooldown entre dash
        self.last_dash_time = 0 # Temps depuis le dernié dash
        self.dash_multiplier = 3 # Facteur de multiplication de la vitesse durant le dash
        self.dash_trigger_released = True # Pour éviter les déclenchements répétés

    # Fonction pour mettre à jour les limites de l'écran
    def update_screen_limits(self, screen_width, screen_height):
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

    # Fonction pour ramasser les pièces
    def collect_coin(self):
        self.coins += 1
        collect_sound.play()

    # Fonction pour les mouvements du joueurs
    def move(self, keys, screen_rect, weapon, obstacle_tiles, exit_tile, can_exit):
        if self.alive == False:  # Si le joueur est mort, il ne peut pas bouger
            return [0, 0], False # On retourne [0,0] pour le screen_scroll, et False pour le level_complete

        screen_scroll = [0, 0] # On initialise le défilement de l'écran
        level_complete = False # On initialise la boolean du niveau_complété
        self.running = False # On initialise la boolean pour savoir si on cours ou non

        # Entrées clavier (ZQSD/Flèches directionnel)
        dx_keyboard = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_q] or keys[pygame.K_LEFT])
        dy_keyboard = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_z] or keys[pygame.K_UP])
        
        # Entrées manettes (Dpad/Joystick Gauche)
        dx_gamepad = 0
        dy_gamepad = 0
        for joystick in joysticks: # Pour chacune des manettes dans la liste des manettes
            # Joystick gauche
            if joystick.get_numaxes() >= 2:
                horiz_move = joystick.get_axis(0) # Déplacement horizontal
                vert_move = joystick.get_axis(1) # Déplacement vertical
                if abs(horiz_move) > 0.15: # Marge pour vérifier qu'il y a un minimum de mouvement sur le joystick
                    dx_gamepad += horiz_move
                if abs(vert_move) > 0.15: # Marge pour vérifier qu'il y a un minimum de mouvement sur le joystick
                    dy_gamepad += vert_move
            # D-Pad
            if joystick.get_numhats() > 0:
                hat_x, hat_y = joystick.get_hat(0) # Mouvement vetical/horizontal
                if hat_x != 0: # Si on appuie sur une flèche du dpad
                    dx_gamepad += hat_x
                if hat_y != 0: # Si on appuie sur une flèche du dpad
                    dy_gamepad -= hat_y
        # Vérifie si le joueur utilise une manette
        self.using_gamepad = any(abs(joystick.get_axis(0)) > 0.15 or abs(joystick.get_axis(1)) > 0.15 for joystick in joysticks)

        # Calcul du déplacement total
        dx = dx_keyboard + dx_gamepad
        dy = dy_keyboard + dy_gamepad

        # Mise à jour de l'info sur la souris
        rel = pygame.mouse.get_rel()  # Renvoie le mouvement relatif depuis le dernier appel
        if rel != (0, 0): # S'il y a un mouvement
            self.using_mouse = True
            self.last_mouse_pos = pygame.mouse.get_pos()
        # Si aucun mouvement n'est détecté et qu'on n'a jamais eu d'info sur la souris, on garde les mouvements du clavier
        elif self.last_mouse_pos is None:
            self.using_mouse = False

        # Gestion du dash
        current_time = pygame.time.get_ticks()
        dash_input = keys[pygame.K_SPACE] # Barre espace sur le clavier pour déclencher le dash
        for joystick in joysticks:
            if joystick.get_button(0): # Bouton A pour dash sur manette
                dash_input = True
                break # On continue le déroulé de la fonction

        if dash_input: # Si une touche de dash est déclenché
            if self.dash_trigger_released and (current_time - self.last_dash_time >= self.dash_cooldown) and not self.dash_active: # Si le cooldown est fini et qu'on n'est pas entrain de dash
                dash_sound.play()
                self.dash_active = True # On marque le dash comme actif
                self.dash_trigger_released = False # On marque la touche du dash comme appuyé pour éviter les répétitions
                self.last_dash_time = current_time # On met à jour la date de la dernière utilisation du dash
                self.dash_start_time = current_time # On met à jour la date du début du dash
        else:
            self.dash_trigger_released = True # On marque la touche du dash comme relaché
        
        # Si le dash est actif, on force l'invincibilité
        if self.dash_active:
            self.is_invincible = True

        # Si le joueur se déplace
        if dx != 0 or dy != 0:
            self.running = True # Le joueur cours donc
            # Priorité à la souris pour le flip si elle a bougé
            if self.using_mouse and self.last_mouse_pos: # Si la souris est utilisé et qu'il y a une valeur renvoyé par last_mouse_pos qui n'est pas null
                self.flip = self.last_mouse_pos[0] < self.rect.centerx # On tourne le sprite du personnage par rapport à la position de la souris
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
            if norm != 0: # Si la norme n'est pas 0
                norm_dx = dx / norm # On divise la valeur delta X par la norme
                norm_dy = dy / norm # On divise la valeur delta Y par la norme
            else: # Sinon on renvoie 0 pour les deux valeurs (x,y)
                norm_dx, norm_dy = 0, 0

            # On met à jour le dernier déplacement du joueur
            self.last_dx = norm_dx
            self.last_dy = norm_dy

            # Appliquer le dash si actif
            if self.dash_active: # Si le dash est actif on multiplie le déplacement par le boost du dash
                dx = norm_dx * self.speed * self.dash_multiplier
                dy = norm_dy * self.speed * self.dash_multiplier
            else: # Sinon on renvoie la vitesse normal du joueur
                dx = norm_dx * self.speed
                dy = norm_dy * self.speed

        # Appliquer le déplacement et regarder les collisions
        self.rect.x += dx # Pour les mouvements horizontal
        for obstacle in obstacle_tiles: # S'il y a des obstacles dans la liste des obstacles
            # Regarder les collisions
            if obstacle[1].colliderect(self.rect):
                # Regarder de qu'elle côté et la collision
                if dx > 0: # Si elle est a droite
                    self.rect.right = obstacle[1].left
                if dx < 0: # Si elle est a gauche
                    self.rect.left = obstacle[1].right
        self.rect.y += dy # Pour les mouvements vertical
        for obstacle in obstacle_tiles: # S'il y a des obstacles dans la liste des obstacles
            # Regarder les collisions
            if obstacle[1].colliderect(self.rect):
                # Regarder de qu'elle côté et la collision
                if dy > 0: # Si elle est en bas
                    self.rect.bottom = obstacle[1].top
                if dy < 0: # Si elle est en haut
                    self.rect.top = obstacle[1].bottom

        # Mise à jour de la hitbox pour qu'elle suive le joueur
        self.hitbox.center = self.rect.center

        # Vérifier la collission avec l'élément permettant de changer de niveau
        for tile in exit_tile:
            if tile[1].colliderect(self.rect): # S'il y a une collision
                if can_exit: # Si le joueur peut sortir du niveau (c'est à dire s'il n'y a plus d'ennemie vivant dans celui-ci)
                    level_complete = True # On marque le niveau comme fini
                    break
                else : # Sinon
                    overlap_rect = self.rect.clip(tile[1])
                    if overlap_rect.width < overlap_rect.height:
                        if self.rect.centerx < tile[1].centerx:
                            self.rect.right = tile[1].left
                        else:
                            self.rect.left = tile[1].right
                    else:
                        if self.rect.centery < tile[1].centery:
                            self.rect.bottom = tile[1].top
                        else:
                            self.rect.top = tile[1].bottom


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
    
    # Fonction pour mettre des dégâts au joueur
    def take_damage(self, damage):
        # Si le dash est actif, on ignore les dégâts
        if self.dash_active:
            return
        if not self.is_invincible: # Si le joueur n'est pas invincible
            self.health -= damage # On lui enlève le nombre de dégât à sa vie
            damage_sound.play()
            voice_sounds = [damagevoice_sound1, damagevoice_sound2, damagevoice_sound3]
            choice(voice_sounds).play()
            if self.health <= 0: # Si le joueur est mort
                self.health = 0  # Empêche la vie d'aller en dessous de 0
                death_sound.play()
                self.alive = False
                self.deaths += 1 # On rajoute 1 au compteur de mort
            #self.is_invincible = True
            self.invincibility_timer = pygame.time.get_ticks()

    # Fonction pour mettre à jour le joueur
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

        self.image = self.animation_list[self.action][self.frame_index] # On récupère l'image du sprite par rapport à l'action/la frame
        if current_time - self.update_time > animation_cooldown: # Si le cooldown est passer
            self.frame_index += 1 # On passe à la frame suivante
            self.update_time = current_time # On met à jour le temps pour le remettre à zéro
        if self.frame_index >= len(self.animation_list[self.action]): # Si la frame actuel dépasse la dernière frame
            self.frame_index = 0 # On repasse à la première

        if self.is_invincible and current_time - self.invincibility_timer > 1000:
            self.is_invincible = False  # Désactive l'invincibilité après 1 seconde

    # Fonction pour mettre à jour les actions du joueurs
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    # Fonction pour dessiner le joueur
    def draw(self, surface):
        if not self.dash_active:
            flipped_image = pygame.transform.flip(self.image, self.flip, False)
            # Positionner le sprite par rapport à la hitbox
            surface.blit(flipped_image, (self.hitbox.x - SCALE * OFFSET_X, self.hitbox.y - SCALE * OFFSET_Y))
        # Dessine la hitbox (optionnel, pour le debug)
        #pygame.draw.rect(surface, PLAYER_COLOR, self.hitbox, 1)


# Classe des PowerUP 
class PowerUP:
    def __init__(self, player, activepowerups):
        self.player = player
        self.activepowerups = activepowerups # Liste des pouvoirs actifs
        self.apply_powerups()  # Appliquer immédiatement les effets

    # Fonction pour appliquer les effets des améliorations
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
