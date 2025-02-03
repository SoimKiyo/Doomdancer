## Configuration générale du jeu
SCREEN_WIDTH = 960  # Largeur de l'écran en pixels
SCREEN_HEIGHT = 540  # Hauteur de l'écran en pixels
FPS = 60  # Nombre d'images par seconde (Max)

## Paramètres du joueur
PLAYER_WIDTH = 50  # Largeur du joueur
PLAYER_HEIGHT = 50  # Hauteur du joueur
PLAYER_SPEED = 5  # Vitesse de déplacement du joueur
PLAYER_COLOR = (0, 128, 255)  # Couleur de la box du joueur (bleu)

## Échelle de mise à l'échelle des sprites
SCALE = 3  # Mise à l'échelle des sprites du joueur et des éléments
WEAPON_SCALE = 2  # Mise à l'échelle des armes

## Paramètres des projectiles
PROJECTILE_SPEED = 10  # Vitesse des projectiles lorsqu'ils sont tirés
MOUSE_TIMEOUT = 150  # Durée pour considérer une entrée comme "récente"

## Décalage des sprites
OFFSET_Y = 25  # Décalage vertical appliqué aux sprites
OFFSET_X = 20  # Décalage horizontal appliqué aux sprites

WEAPON_OFFSET_X = 40  # Décalage horizontal de l'arme
WEAPON_OFFSET_Y = -5   # Décalage vertical de l'arme

## Paramètres des ennemis
ENEMY_WIDTH = 40  # Largeur des ennemis
ENEMY_HEIGHT = 40  # Hauteur des ennemis
ENEMY_SPEED = 4  # Vitesse de déplacement des ennemis
ENEMY_COLOR = (255, 128, 0)  # Couleur de la box des ennemies (orange)
ENEMY_HEALTH = 100  # Points de vie des ennemis

## Paramètres du scrolling
SCROLL_THRESH = 200  # Distance à partir de laquelle l'écran commence à défiler
screen_scroll = [0, 0]  # Stocke le décalage du scrolling en (x, y)

## Paramètres de la carte
TILE_SIZE = 24 * SCALE  # Taille des tiles en pixels après mise à l'échelle
TILE_TYPES = 52  # Nombre total de types de tiles
ROWS = 16  # Nombre de lignes dans la carte (Fichier CSV)
COLS = 150  # Nombre de colonnes dans la carte (Fichier CSV)

## Couleurs de base
RED = (255, 0, 0)  # Rouge
WHITE = (255, 255, 255)  # Blanc
BLACK = (0, 0, 0)  # Noir

## Musiques
MENU_MUSIC = "assets/audio/music/ScreenTitleMusic.mp3"
GAME_MUSIC = "assets/audio/music/AmbiantMusic.mp3"
BOSS_MUSIC = "assets/audio/music/BossMusic.mp3"