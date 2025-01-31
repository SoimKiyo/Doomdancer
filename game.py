import pygame
from player import Player, player_animations, scale_img
from constants import *
from weapon import Weapon
from enemy import Enemy, enemy_animations
from ui import DamageText
from map import World, world_data, tile_list

# Arme du joueur
def weapon_images(element):
    toreturn = 0
    if element == "soulorb":
        toreturn = scale_img(pygame.image.load("assets/images/weapons/soulorb.png").convert_alpha(), WEAPON_SCALE)
    else:
        toreturn = scale_img(pygame.image.load("assets/images/weapons/projectile.png").convert_alpha(), WEAPON_SCALE)
    return toreturn

projectile_group = pygame.sprite.Group()
damage_text_group = pygame.sprite.Group()

# Classe du jeu
class Game:
    def __init__(self, screen_width, screen_height, joysticks, screen):
        # Dimensions de l'écran
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = screen

        self.joysticks = joysticks

        # Zone jouable (limites de l'écran)
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

        # Création du joueur
        self.player_animations = player_animations()
        self.player = Player(screen_width // 2, screen_height // 2, TILE_SIZE, TILE_SIZE, self.player_animations)

        # Création d'un ennemi
        self.mob_animations = enemy_animations()
        self.enemy = Enemy(screen_width // 4, screen_height // 4, ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_HEALTH, self.mob_animations, 1)
        self.enemy_list = []
        self.enemy_list.append(self.enemy)

        # Arme
        self.weapon = Weapon(weapon_images("soulorb"), self.joysticks, weapon_images("projectile"))

        # Couleurs du décor
        self.background_color = BLACK
        self.world = World()
        self.world.process_data(world_data, tile_list)

    # Met a jour la taille de l'écran
    def update_screen_limits(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player.update_screen_limits(screen_width, screen_height)

    # Met a jour les éléments du jeu (comme le joueur)
    def update(self, keys):
        # Screen scroll
        screen_scroll = self.player.move(keys, self.screen_rect)
        self.world.update(screen_scroll)

        # Joueur
        self.player.update()

        # Projectile
        projectile = self.weapon.update(self.player)
        if projectile:
            projectile_group.add(projectile)
        # Texte de dégats
        for projectile in projectile_group:
            damage, damage_pos = projectile.update(screen_scroll, self.enemy_list)
            if damage:
                damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), RED, screen_scroll)
                damage_text_group.add(damage_text)
        damage_text_group.update()

        # Enemies
        for enemy in self.enemy_list:
            enemy.update()

    # Dessine et affiche les éléments du jeu
    def draw(self, screen):
        screen.fill(self.background_color)  # Dessine le fond

        # Map
        self.world.draw(screen)

        # Joueur
        self.player.draw(screen)  # Dessine le joueur

        # Arme
        self.weapon.draw(screen) # Dessine l'arme

        # Enemie
        for enemy in self.enemy_list: # Dessine l'ennemi à l'écran
            enemy.ai(screen_scroll)
            enemy.draw(screen)
        
        # Projectile
        for projectile in projectile_group: # Dessine les flèches
            projectile.draw(screen)
        damage_text_group.draw(screen)

    # Réinitialise le jeu
    def reset(self):
        self.player.rect.x = self.screen_width // 2
        self.player.rect.y = self.screen_height // 2
