import pygame
import math
from constants import *

joysticks = []  # Liste vide pour stocker les manettes

def scale_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (int(w * scale), int(h * scale)))

def player_animations():
    # Dictionnaire contenant les types d'animations et leur nombre de frames 
    animation_frames = { 
        "idle": 30, 
        "run": 8  
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
        self.image = self.animation_list[self.action][self.frame_index]
        # Rectangle du joueur
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.center = (x, y)
        self.speed = PLAYER_SPEED  # Vitesse de déplacement
        self.screen_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)  # Limites de l'écran
        # Création d'une hitbox
        self.hitbox = pygame.Rect(0, 0, width - 10, height - 10)
        self.hitbox.center = self.rect.center

        # Pour mémoriser la dernière direction de déplacement (normalisée)
        self.last_dx = 0
        self.last_dy = 0
        # Pour conserver la dernière position connue de la souris
        self.last_mouse_pos = None
        self.using_mouse = False # La souris est-elle utilisé ?

    def update_screen_limits(self, screen_width, screen_height):
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

    def move(self, keys, screen_rect, weapon):
        screen_scroll = [0, 0]
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
            norm_dx = dx / norm
            norm_dy = dy / norm
            self.last_dx = norm_dx
            self.last_dy = norm_dy

            dx = norm_dx * self.speed
            dy = norm_dy * self.speed

        # Appliquer le déplacement
        self.rect.x += dx
        self.rect.y += dy

        # Mise à jour de la hitbox pour qu'elle suive le joueur
        self.hitbox.center = self.rect.center

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

        return screen_scroll

    def update(self):
        animation_cooldown = 60 # Temps entre chaque frame
        if self.running:
            self.update_action("run")
            animation_cooldown = 100
        else:
            self.update_action("idle")
            animation_cooldown = 60

        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown: # Changer de frame en fonction du cooldown
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        flipped_image = pygame.transform.flip(self.image, self.flip, False)
        # Positionner le sprite par rapport à la hitbox
        surface.blit(flipped_image, (self.hitbox.x - SCALE * OFFSET_X, self.hitbox.y - SCALE * OFFSET_Y))
        # Dessine la hitbox (optionnel, pour le debug)
        pygame.draw.rect(surface, PLAYER_COLOR, self.hitbox, 1)