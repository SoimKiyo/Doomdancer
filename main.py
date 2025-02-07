import pygame
from menu import Menu
from game import Game
from player import joysticks
from constants import *
from map import map_sprites

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Taille de l'écran
pygame.display.set_caption("RemnA.I.nt") # Titre du jeu
clock = pygame.time.Clock() # FramesRate
font_title = pygame.font.Font("assets/other/fonts/font.otf", 80)  # Police pour les titres
font_option = pygame.font.Font("assets/other/fonts/font.otf", 36)  # Police pour les options
pygame.joystick.init() # Initialiser les manettes

# Chargement des tiles de la map
map_sprites()

# Création de l'instance du menu
menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, joysticks, screen, font_option)

# Variables d'état
running = True # Le jeu est il actif ?
in_game = False # Le joueur est il entrain de jouer ?
paused = False # Le jeu est en pause ?


# Variables pour appliquer les paramètres
#current_fullscreen = False
#current_resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Fonction pour mettre à jour les dimensions de l'écran
def update_screen_dimensions():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    menu.screen_width = SCREEN_WIDTH
    menu.screen_height = SCREEN_HEIGHT
    game.update_screen_limits(SCREEN_WIDTH, SCREEN_HEIGHT)

# Fonction pour jouer la musique en boucle
def play_music(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # -1 signifie jouer en boucle

play_music(MENU_MUSIC)
pygame.mixer.music.set_volume(menu.music_volume) # Applique le volume à la musique

# Boucle principale
while running:
    # Récupère les évènements pygame (Clavier/Souris/etc)
    for event in pygame.event.get():
        # Ajout de la manette
        if event.type == pygame.JOYDEVICEADDED :
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joy)
        # Si on ferme le jeu
        if event.type == pygame.QUIT:
            running = False
        
        # Si le jeu n'est pas fermé et que on n'est pas dans une partie
        if not in_game:
            # Gestion du menu principal et de ses entrées
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
            action = menu.handle_input(event)
            if action == "play":
                in_game = True
                game.reset()  # Réinitialiser le jeu au démarrage
                play_music(GAME_MUSIC)
            elif action == "quit":
                running = False
        elif paused:
            # Gestion du menu pause
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
            action = menu.handle_input(event)
            if action == "resume":
                paused = False
            elif action == "menu":
                paused = False
                in_game = False
                play_music(MENU_MUSIC)
            elif action == "quit":
                running = False
        else:
            # Gestion du jeu en cours (Si le joueur appuie sur echape/start button il est enmené sur le menu pause)
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (event.type == pygame.JOYBUTTONDOWN and event.button == 7): # Keydown est utilisé pour écouter que quand la touche est pressé et pas relâché
                paused = True

    # Appliquer les paramètres d'écran si nécessaires
    #if current_fullscreen != menu.fullscreen:
        #screen = menu.apply_settings(screen) #Modifie le mode d'affichage
        #current_fullscreen = menu.fullscreen
        #update_screen_dimensions() # Met a jour les dimensions

    # Affichage (On dessine le menu principal)
    if not in_game or paused:
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        menu.is_pause_menu = paused
        menu.draw(screen, font_title, font_option)
    # Sinon on est en jeu
    else:
        if not paused:
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)
            # Appeler les mises à jour et le rendu du jeu
            keys = pygame.key.get_pressed()
            game.update(keys)  # Met à jour le joueur
            game.draw(screen)  # Dessine la scène de jeu
        
    # On raffraichit et limite les FPS
    pygame.display.flip() #Met a jour l'affichage (tout sans spécification)
    clock.tick(FPS) # Limite le taux de FPS max

pygame.quit()
