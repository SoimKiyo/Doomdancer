import pygame
from player import Player, PowerUP, player_animations, scale_img
from constants import *
from weapon import Weapon, MeleeAttack
from enemy import Enemy, enemy_animations
from ui import DamageText, HealthBar, ScreenFade, PowerupScreen
from map import World, world_data, tile_list, level
from random import choice
import csv 

# Arme du joueur
def weapon_images(element):
    toreturn = 0
    if element == "basicgun":
        toreturn = scale_img(pygame.image.load("assets/images/weapons/basicgun.png").convert_alpha(), WEAPON_SCALE)
    else:
        toreturn = scale_img(pygame.image.load("assets/images/weapons/projectile.png").convert_alpha(), WEAPON_SCALE)
    return toreturn

projectile_group = pygame.sprite.Group()
damage_text_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()

# Fonction pour remettre à zéro le niveau
def reset_level():
    damage_text_group.empty()
    projectile_group.empty()
    coins_group.empty()

    # Créer une liste de tile vide
    data = []
    for row in range(ROWS):
        r= [-1]*COLS
        data.append(r)

    return data

# Classe du jeu
class Game:
    def __init__(self, screen_width, screen_height, joysticks, screen, font_option):
        # Dimensions de l'écran
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = screen
        self.font = font_option

        self.joysticks = joysticks

        self.screen_scroll = screen_scroll

        # Zone jouable (limites de l'écran)
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

        # Création du joueur
        self.player_animations = player_animations()
        self.player = Player(screen_width // 2, screen_height // 2, TILE_SIZE, TILE_SIZE, self.player_animations)
        self.health_bar = HealthBar(20, 20, 200, 20, self.player)  # Barre de vie en haut à gauche

        # Création d'un ennemi
        self.mob_animations = enemy_animations()
        self.enemy = Enemy(screen_width // 4, screen_height // 4, ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_HEALTH, self.mob_animations, 1)
        self.enemy.set_target(self.player)
        self.enemy_list = []
        self.enemy_list.append(self.enemy)

        # Arme
        self.weapon = Weapon(weapon_images("basicgun"), self.joysticks, weapon_images("projectile"))
        self.melee_attack = MeleeAttack(self.joysticks, damage_text_group)

        ## Animations
        # Animation de changement de niveau
        self.start_intro = True
        self.intro_fade = ScreenFade(1, BLACK, 15)
        # Animation de powerup
        self.poweruplist = ["speed", "heal"]
        self.activepowerups = []
        self.requirement = 10


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
        global level, world_data
        if self.player.alive == True:
            # Screen scroll
            screen_scroll, level_complete = self.player.move(keys, self.screen_rect, self.weapon, self.world.obstacle_tiles, self.world.exit_tile)
            self.screen_scroll = screen_scroll
            self.world.update(screen_scroll)
            
            # Mise à jour du Niveau
            if level_complete and len(self.enemy_list) == 0:
                self.start_intro = True
                level += 1
                world_data = reset_level()
                with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter=",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                self.world = World()
                self.world.process_data(world_data, tile_list)
                #temp_hp = self.player.health
                #self.player = self.world.player
                #self.player.health = temp_hp
                #self.enemy_list = self.world.enemy_list
        
            # Mise à jour de l'attaque melee
            self.melee_attack.update(self.player, self.enemy_list, coins_group)

            # Joueur
            self.player.update()
            PowerUP(self.activepowerups)

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
                if not enemy.alive:
                    enemy.take_damage(0, coins_group)  # Drop des fragments
                    self.enemy_list.remove(enemy)
                enemy.update()
            coins_group.update(self.screen_scroll, self.player)
        else:
            # Si le joueur est mort on réinitialise
            self.restart_game()

    # Dessine et affiche les éléments du jeu
    def draw(self, screen):
        screen.fill(self.background_color)  # Dessine le fond

        # Map
        self.world.draw(screen)

        # Joueur
        self.player.draw(screen)  # Dessine le joueur
        self.health_bar.draw(screen)  # Dessine la barre de vie

        # Arme
        self.weapon.draw(screen, self.player) # Dessine l'arme

        # Enemie
        for enemy in self.enemy_list: # Dessine l'ennemi à l'écran
            enemy.ai(self.screen_scroll)
            enemy.draw(screen)
        
        # Projectile
        for projectile in projectile_group: # Dessine les flèches
            projectile.draw(screen)
        damage_text_group.draw(screen)

        coins_group.draw(screen)

        # Commencer l'intro de transition de niveau
        if self.start_intro == True:
            if self.intro_fade.fade(self.screen):
                self.start_intro = False
                self.intro_fade.fade_counter = 0
        
        # Ecran de Powerup
        if self.player.coins >= self.requirement and self.player.alive == False: # Si le joueur a suffisament de piece et n'est pas en vie
            self.requirement += 10 # Augment la somme nécéssaire
            self.player.coins -= 10 # Retire les pieces du joueurs
            if self.poweruplist:
                selected_powerup = choice(self.poweruplist) # Choisis aléatoirement un powerup de la liste
                self.activepowerups.append(selected_powerup) # Ajoute le powerup dans la liste des powerup actif
                PowerupScreen(self.activepowerups, self.font)
        
        
    # Relancer la partie
    def restart_game(self):
        global level, world_data

        self.start_intro = True
        level = 0  # Revenir au premier niveau
        world_data = reset_level()

        # Recharger les données du niveau
        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)
        self.world = World()
        self.world.process_data(world_data, tile_list)

        # Réinitialiser le joueur
        self.player = Player(self.screen_width // 2, self.screen_height // 2, TILE_SIZE, TILE_SIZE, player_animations())
        self.health_bar = HealthBar(20, 20, 200, 20, self.player)

        # Réinitialiser les ennemis
        self.enemy_list = []
        enemy = Enemy(self.screen_width // 4, self.screen_height // 4, ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_HEALTH, enemy_animations(), 1)
        enemy.set_target(self.player)
        self.enemy_list.append(enemy)


    # Réinitialise le jeu
    def reset(self):
        self.player.rect.x = self.screen_width // 2
        self.player.rect.y = self.screen_height // 2
