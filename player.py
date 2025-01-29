import pygame
import math
from constants import *

joysticks = [] # Liste vide pour stocker les manettes

# Fonction pour mettre à jour la taille du joueur
def scale_img(image,scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (w * scale, h * scale))

# Fonction pour charger les animations
def load_animations():
    animation_frames = { # Dictionnaire contenant les types d'animations et leur nombre de frames
        "idle": 2,
        "run": 8 
    }
    animation_list = {key: [] for key in animation_frames}  # Dictionnaire pour stocker les animations
    for animation, num_frames in animation_frames.items():
        for i in range(num_frames):  # Charger chaque sprite
            img = pygame.image.load(f"assets/images/player/{animation}/{i}.png").convert_alpha() # Charger l'image
            img = scale_img(img, SCALE)  # Redimensionner
            animation_list[animation].append(img)  # Ajouter à la liste
    return animation_list

# Classe du joueur
class Player:
    # Initialise le joueur et ses valeurs
    def __init__(self, x, y, width, height, animation_list):
        # Animation/Sprite du personnage
        self.flip = False # Permet de tourner l'image du joueur
        self.animation_list = animation_list
        self.frame_index = 0 # Première frame de l'animation
        self.action = "idle"
        self.update_time = pygame.time.get_ticks() # Le nombre de ticks pour mettre à jour l'animation
        self.running = False
        self.image = animation_list[self.action][self.frame_index] # l'image du joueur

        self.rect = pygame.Rect(x, y, width, height)  # Rectangle du joueur
        self.rect.center = (x,y) # Positionne le personnage
        self.speed = PLAYER_SPEED  # Vitesse de déplacement
        self.screen_rect = pygame.Rect(0, 0, 800, 600)  # Limites par défaut de l'écran

    # Permet de mettre à jour les limite de la taille de l'écran
    def update_screen_limits(self, screen_width, screen_height):
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

    # Gère les déplacements de l'écran en fonction des entrées
    def move(self, keys, screen_rect):
        screen_scroll = [0,0]
        self.running = False
        # Initialisation des valeur de déplacement, delta x et y
        dx = 0
        dy = 0

        # Déplacement clavier
        dx += (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_q] or keys[pygame.K_LEFT])
        dy += (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_z] or keys[pygame.K_UP])
        
        # Déplacement via la manette (Joystick et D-Pad)
        for joystick in joysticks:
            # Utilisation du joystick
            if joystick.get_numaxes() >= 2:  # Vérifie si la manette a au moins 2 axes
                horiz_move = joystick.get_axis(0)  # Axe X (gauche/droite)
                vert_move = joystick.get_axis(1)  # Axe Y (haut/bas)

                # Meilleur gestion de la sensibilité du joystick (angle mort à 0.15)
                if abs(horiz_move) > 0.15: 
                    dx += horiz_move
                if abs(vert_move) > 0.15: 
                    dy += vert_move

            # Utilisation du D-Pad
            if joystick.get_numhats() > 0:  # Vérifie si la manette a un D-Pad
                hat_x, hat_y = joystick.get_hat(0)  # Récupère la direction du D-Pad
                if hat_x != 0:
                    dx = hat_x
                if hat_y != 0:
                    dy = -hat_y

        # Permet de savoir si le joueur se déplace
        if dx != 0 or dy != 0:
            self.running = True

        # Permet de retourner l'image du joueur en fonction de sa direction
        if dx < 0:
            self.flip = True
        if dx > 0:
            self.flip = False

        # Normalisation de la vitesse (car sinon sa adittionne la vitesse des deux axes par exemple en cas de déplacement diagonale)
        if dx or dy:
            norm = math.sqrt(dx ** 2 + dy ** 2) #Calcule de la norme de la vitesse
            # Ajustement des valeurs
            dx = (dx / norm) * self.speed
            dy = (dy / norm) * self.speed

        # Appliquer le mouvement
        self.rect.x += dx
        self.rect.y += dy

        ## Logique applicable qu'au joueur
        # Mettre à jour le défilement de l'écran en fonction de la position du joueur
        if self.rect.right > (SCREEN_WIDTH - SCROLL_THRESH):
            screen_scroll[0] = (SCREEN_WIDTH - SCROLL_THRESH) - self.rect.right
            self.rect.right = SCREEN_WIDTH - SCROLL_THRESH
        if self.rect.left < SCROLL_THRESH:
            screen_scroll[0] = SCROLL_THRESH - self.rect.left
            self.rect.left = SCROLL_THRESH

        return screen_scroll

        # Limite le joueur à l'intérieur de l'écran
        #self.rect.clamp_ip(self.screen_rect)

    # Fonction pour gérer l'animation
    def update(self):
        animation_cooldown = 350
        # Vérifier quelle action le joueur réalise
        if self.running == True:
            self.update_action("run")
            animation_cooldown = 120
        else:
            self.update_action("idle")
            animation_cooldown = 350

        # Mettre à jour l'image
        self.image = self.animation_list[self.action][self.frame_index]
        # Vérifier combien de temps il c'est écoulé depuis la dernière frame
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # Vérifier si l'animation est fini
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # Vérifier si la nouvelle action est différente de l'ancienne
        if new_action != self.action:
            self.action = new_action
            # Mettre à jour les paramètres de l'animation
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    # Dessine et affiche le joueur
    def draw(self, surface):
        flipped_image = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(flipped_image, (self.rect.x - SCALE * OFFSET_X, self.rect.y - SCALE * OFFSET_Y))
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect, 1)
