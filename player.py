# player.py

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
        # Animation/Sprite du personnage
        self.flip = False  # Permet de tourner l'image du joueur
        self.animation_list = animation_list
        self.frame_index = 0  # Première frame de l'animation
        self.action = "idle"
        self.update_time = pygame.time.get_ticks()  # Temps pour mettre à jour l'animation
        self.running = False
        self.image = self.animation_list[self.action][self.frame_index]
        # Rectangle du joueur
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.center = (x, y)
        self.speed = PLAYER_SPEED  # Vitesse de déplacement
        self.screen_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)  # Limites par défaut de l'écran
        # Attributs pour mémoriser la dernière direction de déplacement (normalisée)
        self.last_dx = 0
        self.last_dy = 0

    def update_screen_limits(self, screen_width, screen_height):
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

    def move(self, keys, screen_rect, weapon):
        screen_scroll = [0, 0]
        self.running = False
        dx = 0
        dy = 0

        # Déplacement clavier (ZQSD ou flèches directionnelles)
        dx += (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_q] or keys[pygame.K_LEFT])
        dy += (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_z] or keys[pygame.K_UP])
        
        # Déplacement via la manette (Joystick et D-Pad)
        for joystick in joysticks:
            # Utilisation du joystick
            if joystick.get_numaxes() >= 2:
                horiz_move = joystick.get_axis(0)  # Axe X (gauche/droite)
                vert_move = joystick.get_axis(1)   # Axe Y (haut/bas)
                # Gestion de la sensibilité du joystick (angle mort à 0.15)
                if abs(horiz_move) > 0.15:
                    dx += horiz_move
                if abs(vert_move) > 0.15:
                    dy += vert_move
            # Utilisation du D-Pad
            if joystick.get_numhats() > 0:
                hat_x, hat_y = joystick.get_hat(0)
                if hat_x != 0:
                    dx = hat_x
                if hat_y != 0:
                    dy = -hat_y

        # Si le joueur se déplace, enregistrer la direction pour orienter l'arme
        if dx != 0 or dy != 0:
            self.running = True
            if not weapon.using_right_stick and not weapon.using_mouse:
                self.flip = dx < 0  # Flip du joueur selon la direction de déplacement
            # Normalisation de la direction de déplacement
            norm = math.sqrt(dx ** 2 + dy ** 2)
            norm_dx = dx / norm
            norm_dy = dy / norm
            # Stocker la dernière direction pour que l'arme s'oriente en conséquence
            self.last_dx = norm_dx
            self.last_dy = norm_dy
            dx = norm_dx * self.speed
            dy = norm_dy * self.speed

        # Appliquer le mouvement au joueur
        self.rect.x += dx
        self.rect.y += dy

        # Gestion du défilement de l'écran en fonction de la position du joueur
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
        animation_cooldown = 60
        # Déterminer l'action (idle ou run) en fonction du déplacement
        if self.running:
            self.update_action("run")
            animation_cooldown = 100
        else:
            self.update_action("idle")
            animation_cooldown = 60

        # Mettre à jour l'image du joueur selon l'animation courante
        self.image = self.animation_list[self.action][self.frame_index]
        # Vérifier le temps écoulé depuis la dernière frame
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # Réinitialiser l'animation si nécessaire
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # Changer d'action si nécessaire et réinitialiser l'animation
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        # Afficher le joueur avec flip si nécessaire
        flipped_image = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(flipped_image, (self.rect.x - SCALE * OFFSET_X, self.rect.y - SCALE * OFFSET_Y))
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect, 1)
