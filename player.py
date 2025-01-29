import pygame
import math

# Constantes pour le joueur
PLAYER_SPEED = 5
PLAYER_COLOR = (0, 128, 255)

joysticks = [] # Liste vide pour stocker les manettes


# Classe du joueur
class Player:
    # Initialise le joueur et ses valeurs
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)  # Rectangle du joueur
        self.rect.center = (x,y) # Positionne le personnage
        self.speed = PLAYER_SPEED  # Vitesse de déplacement
        self.screen_rect = pygame.Rect(0, 0, 800, 600)  # Limites par défaut de l'écran

    # Permet de mettre à jour les limite de la taille de l'écran
    def update_screen_limits(self, screen_width, screen_height):
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)

    # Gère les déplacements de l'écran en fonction des entrées
    def move(self, keys, screen_rect):
        # Initialisation des valeur de déplacement dans les directions x et y
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

        # Normalisation de la vitesse (car sinon sa adittionne la vitesse des deux axes par exemple en cas de déplacement diagonale)
        if dx or dy:
            norm = math.sqrt(dx ** 2 + dy ** 2) #Calcule de la norme de la vitesse
            # Ajustement des valeurs
            dx = (dx / norm) * self.speed
            dy = (dy / norm) * self.speed

        # Appliquer le mouvement
        self.rect.x += dx
        self.rect.y += dy

        # Limite le joueur à l'intérieur de l'écran
        self.rect.clamp_ip(self.screen_rect)

    # Dessine et affiche le joueur
    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)
