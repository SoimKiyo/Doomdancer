import pygame
from player import Player, PowerUP, player_animations, scale_img
from constants import *
from weapon import Weapon, MeleeAttack
from enemy import Enemy, enemy_animations
from ui import DamageText, PlayerUI, ScreenFade, PowerupScreen
from map import World, world_data, tile_list, level
from sfx import levelclear_sound, levelchange_sound, powerup_sound, gamestart_sound
from random import choice
import csv 

# Arme du joueur
def weapon_images(element):
    if element == "basicgun":
        # Chargement de l'image statique pour l'arme "basicgun"
        return scale_img(
            pygame.image.load("assets/images/weapons/basicgun.png").convert_alpha(),
            WEAPON_SCALE
        )
    else:
        # Chargement de l'animation du projectile (8 frames)
        frames = []
        for i in range(8):
            # On charge chaque frame dans le dossier "assets/images/weapons/projectiles/basicgun/"
            frame = pygame.image.load(f"assets/images/weapons/projectiles/basicgun/{i}.png").convert_alpha()
            frame = scale_img(frame, WEAPON_SCALE)
            frames.append(frame)
        return frames


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

        # Création d'un ennemi
        self.mob_animations = enemy_animations()
        self.enemy = Enemy(screen_width // 4, screen_height // 4, TILE_SIZE, TILE_SIZE, ENEMY_HEALTH, self.mob_animations, 1)
        self.enemy.set_target(self.player)
        self.enemy_list = []
        self.enemy_list.append(self.enemy)

        # Arme
        self.weapon = Weapon(weapon_images("basicgun"), self.joysticks, weapon_images("projectile"))
        self.melee_attack = MeleeAttack(self.joysticks, damage_text_group)

        self.player_ui = PlayerUI(self.player, self.weapon, self.melee_attack, self.font)
        ## Animations
        # Animation de changement de niveau
        self.start_intro = True
        self.intro_fade = ScreenFade(1, BLACK, 15)
        # Animation de powerup
        self.poweruplist = ["speed", "heal"]
        self.activepowerups = []
        self.requirement = 10
        self.powerup_screen_active = False  # Pour bloquer le jeu pendant la sélection du power-up
        self.current_powerup = None  # Stocke le power-up sélectionné
        self.powerup_screen = None  # L'objet écran du power-up
        self.powerup_granted = False  # Indique si le power-up a été donné pour éviter les doublons

        self.levelclear_played = False 

        # Couleurs du décor
        self.levels_passed = 0
        # Liste des niveaux disponibles (correspond aux fichiers level1_data.csv, level2_data.csv, level3_data.csv)
        self.available_levels = [1, 2, 3]

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
            screen_scroll, level_complete = self.player.move(keys, self.screen_rect, self.weapon, self.world.obstacle_tiles, self.world.exit_tiles)
            self.screen_scroll = screen_scroll
            self.world.update(screen_scroll)
            
            # Mise à jour du Niveau
            if len(self.enemy_list) == 0 and self.levelclear_played == False:
                levelclear_sound.play()
                self.levelclear_played = True
            if level_complete and len(self.enemy_list) == 0:
                self.start_intro = True
                self.levels_passed += 1
                levelchange_sound.play()
                self.levelclear_played = False

                if self.levels_passed < 10:
                    # Choix aléatoire d'un niveau parmi les fichiers level1, level2 et level3
                    new_level = choice(self.available_levels)
                    world_data = reset_level()
                    with open(f"levels/level{new_level}_data.csv", newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    self.world = World()
                    self.world.process_data(world_data, tile_list)
                    # Réinitialiser certains éléments du niveau, par exemple les ennemis
                else:
                    # Fin du jeu après 10 niveaux
                    print("Fin du jeu ! Vous avez terminé 10 niveaux.")
        
            # Mise à jour de l'attaque melee
            self.melee_attack.update(self.player, self.enemy_list, coins_group)

            # Joueur
            self.player.update()
            self.powerup_system = PowerUP(self.player, self.activepowerups)

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
            if not self.player.alive and not self.powerup_granted:
                if self.player.coins >= self.requirement and not self.powerup_screen_active:
                    self.requirement += 10
                    self.player.coins -= 10
                    # Filtrer pour obtenir uniquement les powerups non encore acquis
                    available_powerups = [p for p in self.poweruplist if p not in self.activepowerups]
                    if available_powerups:
                        self.current_powerup = choice(available_powerups)
                        self.activepowerups.append(self.current_powerup)
                        self.powerup_screen = PowerupScreen(self.current_powerup, self.font)
                        powerup_sound.play()
                        self.powerup_screen_active = True
                        self.powerup_granted = True  # Marque que le powerup a été accordé une seule fois
                    else:
                        print("Tous les powerups ont déjà été débloqués !")


            # Tant que l'écran du power-up est actif, empêcher le jeu de continuer
            if self.powerup_screen_active:
                return  # Empêcher toute mise à jour tant que l’écran est actif

            # Si le power-up a été choisi et l'écran fermé, appliquer le power-up et relancer le jeu
            if not self.powerup_screen_active and self.powerup_screen is None:
                self.powerup_system = PowerUP(self.player, self.activepowerups)
                self.restart_game()

    # Dessine et affiche les éléments du jeu
    def draw(self, screen):
        screen.fill(self.background_color)  # Dessine le fond

        # Map
        self.world.draw(screen)

        # Joueur
        self.player.draw(screen)  # Dessine le joueur
        self.player_ui.draw(screen)

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
        
        # Dessiner l'écran de power-up s'il est actif
        if self.powerup_screen_active and self.powerup_screen:
            self.powerup_screen.draw(screen)
        
    def handle_input(self, event):
        if self.powerup_screen_active and self.powerup_screen:
            # On vérifie si l'écran doit être skippé :
            if (self.powerup_screen.handle_input(event) or 
                pygame.mouse.get_pressed()[0] or 
                (event.type == pygame.JOYBUTTONDOWN and event.button == 0)):
                self.powerup_screen_active = False
                self.powerup_screen = None
                self.powerup_system = PowerUP(self.player, self.activepowerups)  # Appliquer le power-up
                self.powerup_granted = False  # Réinitialise pour le prochain death
                self.restart_game()  # Relancer la partie

    # Relancer la partie
    def restart_game(self):
        global level, world_data

        # Sauvegarder le nombre de morts du joueur actuel
        previous_deaths = self.player.deaths

        self.start_intro = True
        self.levelclear_played = False 
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

        # Réinitialiser le joueur (la vie et autres attributs seront remis à la valeur par défaut)
        self.player = Player(self.screen_width // 2, self.screen_height // 2, TILE_SIZE, TILE_SIZE, player_animations())
        # Restaurer le nombre de morts sauvegardé
        self.player.deaths = previous_deaths
        # IMPORTANT : Mettre à jour la référence du joueur dans l’interface utilisateur
        self.player_ui.player = self.player

        # Réinitialiser les ennemis
        self.enemy_list = []
        enemy = Enemy(self.screen_width // 4, self.screen_height // 4, TILE_SIZE, TILE_SIZE, ENEMY_HEALTH, enemy_animations(), 1)
        enemy.set_target(self.player)
        self.enemy_list.append(enemy)

    # Réinitialise le jeu
    def reset(self):
        self.player.rect.x = self.screen_width // 2
        self.player.rect.y = self.screen_height // 2
        gamestart_sound.play()
