import pygame
from player import Player, PowerUP, player_animations, scale_img
from constants import *
from weapon import Weapon, MeleeAttack
from enemy import Enemy, enemy_animations
from ui import DamageText, PlayerUI, ScreenFade, PowerupScreen
from map import World, world_data, tile_list, level
from sfx import levelclear_sound, levelchange_sound, powerup_sound, gamestart_sound
from random import *
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

# Creations des groupes des sprites
projectile_group = pygame.sprite.Group()
damage_text_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()

# Fonction pour remettre à zéro le niveau
def reset_level():
    # On vide les groupes
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
        self.font = font_option # Police d'écriture

        self.joysticks = joysticks # Manettes 

        self.screen_scroll = screen_scroll # Scroll de l'écran

        # Zone jouable (limites de l'écran)
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

        # Création du joueur
        self.player_animations = player_animations()
        self.player = Player(screen_width // 2, screen_height // 2, TILE_SIZE, TILE_SIZE, self.player_animations)

        # Création d'ennemies
        self.mob_animations = enemy_animations()
        self.enemy_list = []
        for i in range(randint(3,4)):
            self.enemy = Enemy(screen_width // randint(1, 4), screen_height // randint(1, 4), TILE_SIZE, TILE_SIZE, ENEMY_HEALTH, self.mob_animations, 0)
            self.enemy.set_target(self.player)
            self.enemy_list.append(self.enemy)

        # Arme
        self.weapon = Weapon(weapon_images("basicgun"), self.joysticks, weapon_images("projectile"))
        self.melee_attack = MeleeAttack(self.joysticks, damage_text_group)
        
        # UI
        self.player_ui = PlayerUI(self.player, self.weapon, self.melee_attack, self.font)

        ## Animations
        # Animation de changement de niveau
        self.start_intro = True
        self.intro_fade = ScreenFade(1, BLACK, 15)
        # Animation de powerup
        self.poweruplist = ["speed", "heal"] # Liste des powerups
        self.activepowerups = [] # Liste des powerups actif
        self.requirement = 20 # Nombre de pieces necessaires
        self.powerup_screen_active = False  # Pour bloquer le jeu pendant la sélection du power-up
        self.current_powerup = None  # Stocke le power-up sélectionné
        self.powerup_screen = None  # L'objet écran du power-up
        self.powerup_granted = False  # Indique si le power-up a été donné pour éviter les doublons

        # Map
        self.background_color = WHITE # Couleurs du décor
        self.world = World() # Instance de world
        self.world.process_data(world_data, tile_list) # Process Data de la map
        self.levelclear_played = False # Son a jouer quand un niveau est fini
        self.levels_passed = 0 # Nombre de level complété
        self.available_levels = [1, 2, 3] # Liste des niveaux disponibles (level1_data.csv, level2_data.csv, level3_data.csv,...)

    # Fonction qui met a jour la taille de l'écran
    def update_screen_limits(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player.update_screen_limits(screen_width, screen_height)

    # Fonction qui fait apparaître les ennemies
    def enemy_spawn(self, screen_width, screen_height):
        for i in range(randint(3,4)): # Nombre d'ennemie à faire apparaître
            self.enemy = Enemy(screen_width // randint(1, 4), screen_height // randint(1, 4), TILE_SIZE, TILE_SIZE, ENEMY_HEALTH, self.mob_animations, 0)
            self.enemy.set_target(self.player)
            self.enemy_list.append(self.enemy)

    # Fonction pour mettre a jour les éléments du jeu
    def update(self, keys):
        global level, world_data # Définition global des variables pour y avoir accès
        if self.player.alive == True: # Si le joueur est en vie
            # Screen scroll
            can_exit = (len(self.enemy_list) == 0) # Le joueur peut sortir quand il n'y a plus d'ennemie vivant
            screen_scroll, level_complete = self.player.move(keys, self.screen_rect, self.weapon, self.world.obstacle_tiles, self.world.exit_tiles, can_exit) # On récupère les infos retourner par le joueur
            self.screen_scroll = screen_scroll
            self.world.update(screen_scroll) # On applique le défilement de l'écran
            
            # Mise à jour du Niveau
            if len(self.enemy_list) == 0 and self.levelclear_played == False: # S'il n'y a plus d'ennemie et que le son n'a pas était joué
                levelclear_sound.play() # On joue le son de fin de niveau
                self.levelclear_played = True # On dit que le son a été joué

            if level_complete and len(self.enemy_list) == 0: # Si le niveau est complété et qu'il n'y a plus d'ennemie
                self.start_intro = True # On active l'animation de transition de niveau
                self.levels_passed += 1 # On passe d'un niveau
                levelchange_sound.play() # On joue le son de changement de niveau
                self.levelclear_played = False # On marque le son de fin de niveau comme n'ayant pas était joué

                if self.levels_passed < 10: # Si le joueur a fait moins de 10 niveaux
                    new_level = choice(self.available_levels) # Choix aléatoire d'un niveau parmi les fichiers level1, level2 et level3
                    world_data = reset_level() # On remet à zéro le niveau
                    with open(f"levels/level{new_level}_data.csv", newline="") as csvfile: # On charge les tiles du nouveau niveau
                        reader = csv.reader(csvfile, delimiter=",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    self.world = World()
                    self.world.process_data(world_data, tile_list)
                    self.enemy_spawn(SCREEN_WIDTH, SCREEN_HEIGHT) #Créer de nouveaux ennemies
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
            if projectile: # Si on crée des projectiles alors les ajoutés dans le groupe
                projectile_group.add(projectile)
            # Texte de dégats
            for projectile in projectile_group: #Pour chacun des projectiles dans le groupe
                damage, damage_pos = projectile.update(screen_scroll, self.enemy_list) # On récupère la position et les dégâts infligé au ennemies 
                if damage: # S'il y a des dégâts
                    damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), RED, screen_scroll)
                    damage_text_group.add(damage_text) # Ajouter dans le groupe les valeurs des dégâts
            damage_text_group.update()

            # Enemies
            for enemy in self.enemy_list: # Pour chacun des ennemies
                if not enemy.alive: # Si l'ennemie est mort
                    enemy.take_damage(0, coins_group)  # Dispersion des fragments (coins)
                    self.enemy_list.remove(enemy) # On retire l'ennemie de la liste
                enemy.update() # On met à jour l'ennemie
            coins_group.update(self.screen_scroll, self.player) # On met à jour les coins
        else:
            if not self.player.alive and not self.powerup_granted: # Si le joueur est mort et qu'il n'a pas eu de powerup
                if self.player.coins >= self.requirement and not self.powerup_screen_active: # On vérifie qu'il n'est pas dans l'écran de powerup et qu'il a le nb nécéssaire de fragments
                    self.player.coins -= self.requirement # On retire les pièces du joueurs
                    self.requirement += 10 # On incrémente le nécéssaire
                    # Filtrer pour obtenir uniquement les powerups non encore acquis
                    available_powerups = [p for p in self.poweruplist if p not in self.activepowerups]
                    if available_powerups: # S'il y a encore des éléments dans la liste
                        self.current_powerup = choice(available_powerups) # On choisis aléatoirement un powerup
                        self.activepowerups.append(self.current_powerup) # On l'ajoute dans la liste des pouvoirs actif
                        self.powerup_screen = PowerupScreen(self.current_powerup, self.font) # On Affiche l'écran des powerup
                        powerup_sound.play() # On joue le son de powerup
                        self.powerup_screen_active = True # On marque comme actif l'écran de powerup
                        self.powerup_granted = True  # On marque que le powerup a été accordé
                    else:
                        print("Tous les powerups ont déjà été débloqués !")


            # Tant que l'écran du power-up est actif, empêcher le jeu de continuer
            if self.powerup_screen_active:
                return  # Empêcher toute mise à jour tant que l’écran est actif

            # Si le power-up a été choisi et l'écran fermé, appliquer le power-up et relancer le jeu
            if not self.powerup_screen_active and self.powerup_screen is None:
                self.powerup_system = PowerUP(self.player, self.activepowerups) # On applique le powerup
                self.restart_game() # On recommence la partie (car le joueur est mort)

    # Fonction pour dessiner et afficher les éléments du jeu
    def draw(self, screen):
        screen.fill(self.background_color)  # Dessine le fond

        # Map
        self.world.draw(screen)

        # Joueur
        self.player.draw(screen)  # Dessine le joueur

        # Enemie
        for enemy in self.enemy_list: # Dessine l'ennemi à l'écran
            enemy.ai(self.screen_scroll, self.world.obstacle_tiles)
            enemy.draw(screen)

        coins_group.draw(screen) # Dessine les pièces

        # Projectile
        for projectile in projectile_group: # Dessine les flèches
            projectile.draw(screen)
        damage_text_group.draw(screen)

        # Arme
        self.weapon.draw(screen, self.player) # Dessine l'arme

        self.player_ui.draw(screen) # Dessine l'ui

        # Commencer l'intro de transition de niveau
        if self.start_intro == True:
            if self.intro_fade.fade(self.screen):
                self.start_intro = False
                self.intro_fade.fade_counter = 0
        
        # Dessiner l'écran de power-up s'il est actif
        if self.powerup_screen_active and self.powerup_screen:
            self.powerup_screen.draw(screen)
        
    # Fonction pour gérer les entrés dans le menu de powerup
    def handle_input(self, event):
        if self.powerup_screen_active and self.powerup_screen: # Si le menu est actif
            # On vérifie si l'écran doit être skippé :
            if (pygame.mouse.get_pressed()[0] or (event.type == pygame.JOYBUTTONDOWN and event.button == 0)): # (Boutton A de la manette ou Clique Gauche)
                self.powerup_screen_active = False
                self.powerup_screen = None
                self.powerup_system = PowerUP(self.player, self.activepowerups)  # Appliquer le power-up
                self.powerup_granted = False  # Réinitialise pour la prochaine mort
                self.restart_game()  # Relancer la partie

    # Fonction pour relancer la partie
    def restart_game(self):
        global level, world_data # Définition global des variables pour y avoir accès

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

        # Réinitialiser le joueur (vie/et autre)
        self.player = Player(self.screen_width // 2, self.screen_height // 2, TILE_SIZE, TILE_SIZE, player_animations())
        # Restaurer le nombre de morts sauvegardé
        self.player.deaths = previous_deaths
        # Met à jour la référence du joueur dans l’UI
        self.player_ui.player = self.player

        # Réinitialiser les ennemis
        self.enemy_list = []
        enemy = Enemy(self.screen_width // 4, self.screen_height // 4, TILE_SIZE, TILE_SIZE, ENEMY_HEALTH, enemy_animations(), 1)
        enemy.set_target(self.player)
        self.enemy_list.append(enemy)