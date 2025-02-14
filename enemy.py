import pygame
from constants import *
from player import scale_img
from timer import *
from items import Coin
from sfx import enemydeath_sound
import random

# Fonction pour charger les animations
def enemy_animations():
    mob_animations = []
    mob_types = ["mob"]  # Différent type d'ennemie
    
    animation_frames = {  # Dictionnaire contenant les types d'animations et leur nombre de frames
        "idle": 8,
        "run": 6,
        "attack": 7
    }
    
    for mob in mob_types:
        animation_list = {key: [] for key in animation_frames}  # Dictionnaire pour stocker les animations
        for animation, num_frames in animation_frames.items():
            for i in range(num_frames):  # Charger chaque sprite
                img = pygame.image.load(f"assets/images/{mob}/{animation}/{i}.png").convert_alpha()  # Charger l'image depuis "mob"
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

        self.isattacking = False
        self.target = None  # Référence au joueur
        self.has_attacked = False # Savoir si l'ennemie vient d'attaquer
        self.attack_timer = None

    #fonction pour faire des dégâts à l'ennemie
    def take_damage(self, damage, coins_group):

        self.health -= damage #fais des dégâts à l'ennemie

        # Vérifier si l'ennemie n'as plus de vie
        if self.health <= 0:
            enemydeath_sound.play()
            self.alive = False
            for _ in range(random.randint(1, 3)):
                coin = Coin(self.rect.centerx, self.rect.centery)
                coins_group.add(coin)

    def set_target(self, player):
        self.target = player

    def ai(self, screen_scroll, obstacle_tiles):
        # Repositionner un ennemie par rapport au scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        if self.alive and self.target:
            self.move_towards_target(obstacle_tiles)

    def move_towards_target(self, obstacle_tiles):
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

                self.move_with_collision(direction_x * move_speed, direction_y * move_speed, obstacle_tiles)

                self.flip = direction_x < 0
                self.update_action("run")
            else:
                self.update_action("idle")  # Met en idle si aucun mouvement

    def attack(self):
        if self.target.alive:  # Vérifie que le joueur est en vie
            self.isattacking = True
            self.target.take_damage(5)  # Inflige 5 points de dégâts au joueur
            self.has_attacked = True
            self.attack_timer = Timer(500)  # Attente de 0,5 secondes avant une nouvelle attaque
            self.attack_timer.start()
            # Ne pas forcer l'animation à idle ici, c'est géré dans update()
    
    # Fonction pour permettre à l'ennemie d'avoir des collisions
    def move_with_collision(self, dx, dy, obstacle_tiles):
        # Déplacement horizontal
        self.rect.x += dx
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.rect):
                if dx > 0:  
                    self.rect.right = obstacle[1].left
                if dx < 0:  
                    self.rect.left = obstacle[1].right

        # Déplacement vertical
        self.rect.y += dy
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.rect):
                if dy > 0:  
                    self.rect.bottom = obstacle[1].top
                if dy < 0:  
                    self.rect.top = obstacle[1].bottom
        
    # Fonction pour gérer l'animation
    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False

        # Priorité à l'animation d'attaque
        if self.isattacking:
            if self.action != "attack":
                self.update_action("attack")
            animation_cooldown = 60
        elif self.speed != 0:
            if self.action != "run":
                self.update_action("run")
            animation_cooldown = 80
        else:
            if self.action != "idle":
                self.update_action("idle")
            animation_cooldown = 60

        # Met à jour l'image selon la frame actuelle
        self.image = self.animation_list[self.action][self.frame_index]

        # Gestion du temps d'affichage de chaque frame
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

            # Si on est en animation d'attaque et qu'on a atteint la dernière frame
            if self.action == "attack":
                if self.frame_index >= len(self.animation_list["attack"]):
                    self.frame_index = 0
                    self.isattacking = False  # Fin de l'attaque, on repasse en idle
                    self.update_action("idle")
            else:
                if self.frame_index >= len(self.animation_list[self.action]):
                    self.frame_index = 0

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
        # Récupère le rect de l'image retournée et centre-le sur la hitbox (self.rect)
        image_rect = flipped_image.get_rect(center=self.rect.center)
        # Affiche l'image à la bonne position
        surface.blit(flipped_image, image_rect.topleft)
        # Optionnel : Dessine la hitbox pour le débogage
        #pygame.draw.rect(surface, ENEMY_COLOR, self.rect, 1)