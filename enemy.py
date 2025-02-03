import pygame
from constants import *
from player import scale_img
from timer import *
from items import Coin
import random

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
    # Initialise l'ennemie et ses valeurs
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

        self.target = None  # Référence au joueur
        self.has_attacked = False # Savoir si l'ennemie vient d'attaquer
        self.attack_timer = None

    #fonction pour faire des dégats à l'ennemie
    def take_damage(self, damage, coins_group):

        self.health -= damage #fais des dégats à l'ennemie

        # Vérifier si l'ennemie n'as plus de vie
        if self.health <= 0:
            self.alive = False
            for _ in range(random.randint(1, 3)):
                coin = Coin(self.rect.centerx, self.rect.centery)
                coins_group.add(coin)

    def set_target(self, player):
        self.target = player

    def ai(self, screen_scroll):
        # Repositionner un ennemie par rapport au scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        if self.alive and self.target:
            self.move_towards_target()

    def move_towards_target(self):
        if self.target and self.alive:  # Vérifier que l'ennemi et le joueur sont en vie
            target_x, target_y = self.target.rect.center
            dx, dy = target_x - self.rect.centerx, target_y - self.rect.centery
            distance = max(abs(dx), abs(dy))

            # Vérifier si l'ennemi a attaqué récemment
            if self.has_attacked:
                if self.attack_timer and self.attack_timer.is_finished():
                    self.has_attacked = False  # Réinitialiser l'état d'attaque

            # Si l'ennemi est à portée d'attaque
            if distance < 30 and not self.has_attacked:
                self.attack()

            # Si l'ennemi doit se déplacer vers le joueur
            elif distance > 0:
                direction_x = dx / distance if distance != 0 else 0
                direction_y = dy / distance if distance != 0 else 0

                # Ajuster la vitesse en fonction de la distance
                if distance > 150:
                    move_speed = self.speed
                elif distance > 50:
                    move_speed = self.speed * 1.5
                else:
                    move_speed = self.speed * 2  # Sprint si proche

                self.rect.x += move_speed * direction_x
                self.rect.y += move_speed * direction_y
                self.flip = direction_x < 0
                self.update_action("run")
            else:
                self.update_action("idle")  # Met en idle si aucun mouvement

    def attack(self):
        if self.target.alive:  # Vérifie que le joueur est en vie avant d'attaquer
            print("L'ennemi attaque !")
            self.target.take_damage(10)  # Inflige 10 points de dégâts au joueur
            self.has_attacked = True
            self.attack_timer = Timer(2000)  # Attente de 2 secondes avant une nouvelle attaque
            self.attack_timer.start()
            self.update_action("idle")  # Passe en idle après l'attaque

        
        
    # Fonction pour gérer l'animation
    def update(self):
        # check if character has died
        if self.health <= 0:
            self.health = 0
            self.alive = False
        animation_cooldown = 60

        # Vérifier si l'ennemi court ou est inactif
        if self.speed != 0:  # Si l'ennemi se déplace
            self.update_action("run")
            self.running = True
            animation_cooldown = 100
        else:  # Si l'ennemi est immobile
            self.update_action("idle")
            self.running = False
            animation_cooldown = 60

        # Mettre à jour l'image de l'animation
        self.image = self.animation_list[self.action][self.frame_index]

        # Vérifier combien de temps il c'est écoulé depuis la dernière frame
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        
        # Vérifier si l'animation est fini
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

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
        surface.blit(flipped_image, (self.rect.x - SCALE * OFFSET_X * 3, self.rect.y - SCALE * OFFSET_Y * 2))
        pygame.draw.rect(surface, ENEMY_COLOR, self.rect, 1)