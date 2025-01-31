import pygame
from constants import *
from player import scale_img

# Fonction pour charger les animations
def enemy_animations():
    mob_animations = []
    mob_types = ["player", "mob"]

    animation_frames = { # Dictionnaire contenant les types d'animations et leur nombre de frames
        "idle": 2,
        "run": 8 
    }
    for mob in mob_types:
        animation_list = {key: [] for key in animation_frames}  # Dictionnaire pour stocker les animations
        for animation, num_frames in animation_frames.items():
            for i in range(num_frames):  # Charger chaque sprite
                img = pygame.image.load(f"assets/images/{mob}/{animation}/{i}.png").convert_alpha() # Charger l'image
                img = scale_img(img, SCALE)  # Redimensionner
                animation_list[animation].append(img)  # Ajouter à la liste
        mob_animations.append(animation_list)
    return mob_animations

# Classe de l'ennemie
class Enemy:
    # Initialise l'ennemie' et ses valeurs
    def __init__(self, x, y, width, height, health, mob_animations, char_type):
        self.char_type = char_type
        self.flip = False  # Permet de tourner l'image de l'ennemie
        self.animation_list = mob_animations[char_type]
        self.frame_index = 0  # Première frame de l'animation
        self.action = "idle"
        self.update_time = pygame.time.get_ticks()  # Le nombre de ticks pour mettre à jour l'animation
        self.running = False
        self.image = self.animation_list[self.action][self.frame_index]  # l'image de l'ennemie

        self.rect = pygame.Rect(x, y, width, height)  # Rectangle de l'ennemie
        self.rect.center = (x, y)  # Positionne le monstre
        self.speed = ENEMY_SPEED  # Vitesse de déplacement
        self.screen_rect = pygame.Rect(0, 0, 800, 600)  # Limites par défaut de l'écran

        self.health = health
        self.alive = True

    #fonction pour faire des dégats à l'ennemie
    def take_damage(self, health, damage):

        self.health -= damage #fais des dégats à l'ennemie

        # Vérifier si l'ennemie n'as plus de vie
        if self.health <= 0:
            self.rect.x = 10000

    def ai(self, screen_scroll):
        # Repositionner un ennemie par rapport au scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        
    # Fonction pour gérer l'animation
    def update(self):
        # check if character has died
        if self.health <= 0:
            self.health = 0
            self.alive = False
        animation_cooldown = 350

        # Vérifier si l'ennemi court ou est inactif
        if self.speed != 0:  # Si l'ennemi se déplace
            self.update_action("run")
            self.running = True
            animation_cooldown = 120
        else:  # Si l'ennemi est immobile
            self.update_action("idle")
            self.running = False
            animation_cooldown = 350

        # Mettre à jour l'image de l'animation
        self.image = self.animation_list[self.action][self.frame_index]

        # Vérifier combien de temps il c'est écoulé depuis la dernière frame
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        
        # Vérifier si l'animation est fini
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

        # Déplacement de l'ennemi
        self.rect.x += self.speed  # Déplacer l'ennemi vers la droite

        # Inverser la direction si l'ennemi atteint les bords de l'écran
        if self.rect.right > self.screen_rect.right or self.rect.left < self.screen_rect.left:
            self.speed = -self.speed  # Inverser la direction
            self.flip = not self.flip  # Inverser l'orientation de l'ennemi (gauche/droite)

    def update_action(self, new_action):
        # Vérifier si la nouvelle action est différente de l'ancienne
        if new_action != self.action:
            self.action = new_action
            # Mettre à jour les paramètres de l'animation
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    # Dessine et affiche le monstre
    def draw(self, surface):
        flipped_image = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(flipped_image, (self.rect.x - SCALE * OFFSET_X, self.rect.y - SCALE * OFFSET_Y))
        pygame.draw.rect(surface, ENEMY_COLOR, self.rect, 1)