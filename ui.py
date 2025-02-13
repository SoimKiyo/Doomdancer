import pygame
from constants import *

# Classe de dégâts (Affiche un texte quand des dégâts sont infligés à l'ennemi)
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color, screen_scroll):
        pygame.sprite.Sprite.__init__(self) # Initialise la classe parente Sprite
        self.font = pygame.font.Font("assets/other/fonts/font.otf", 24)  # Charge la police
        self.image = self.font.render(damage, True, color) # Crée une image du texte des dégâts
        self.rect = self.image.get_rect() 
        self.rect.center = (x, y)
        self.counter = 0  # Initialise un compteur pour la durée d'affichage du texte
        self.screen_scroll = screen_scroll

    # Fonction pour mettre à jour le texte
    def update(self):
        # Repositionner par rapport au défilement de l'écran
        self.rect.x += self.screen_scroll[0]  # Ajuste la position horizontale en fonction du défilement de l'écran
        self.rect.y += self.screen_scroll[1]  # Ajuste la position verticale en fonction du défilement de l'écran
        
        # Déplacer le texte de dégât vers le haut
        self.rect.y -= 1  # Déplace le texte vers le haut de 1 pixel à chaque mise à jour
        
        # Supprimer le texte après quelques secondes
        self.counter += 1  # Incrémente le compteur
        if self.counter > 30:  # Si le compteur dépasse 30 (environ 0,5 seconde à 60 FPS)
            self.kill()  # Supprime le sprite du groupe de sprites

            
# Classe de l'UI du joueur
class PlayerUI:
    def __init__(self, player, weapon, melee_attack, font):
        self.player = player
        self.weapon = weapon
        self.melee_attack = melee_attack
        self.font = font

    def draw(self, screen):
        # Barre de vie en bas à gauche
        self.draw_health_bar(screen)
        # Icônes d'attaque (mêlée et tir) avec leurs inputs centrés
        self.draw_action_icons(screen)
        # Statistiques (pièces et morts) à gauche de la barre de munitions
        self.draw_stats(screen)
        # Barre verticale de munitions à droite des stats
        self.draw_ammo_bar(screen)

    # Fonction pour dessiner la barre de vie
    def draw_health_bar(self, screen):
        # Calculer le ratio de vie du joueur
        health_ratio = self.player.health / self.player.max_health

        # Définir les dimensions et la position de la barre de vie
        bar_width = 300
        bar_height = 20
        x = 20
        y = SCREEN_HEIGHT - 50

        # Dessiner une "ombre"
        shadow_offset = 3
        shadow_rect = pygame.Rect(x + shadow_offset, y + shadow_offset, bar_width, bar_height)
        pygame.draw.rect(screen, BLACK, shadow_rect, border_radius=10)

        # Fond de la barre (partie vide)
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(screen, BLACK_GRAY, bg_rect, border_radius=10)

        # Portion de vie (remplie) selon la vie du joueur
        fill_width = int(health_ratio * bar_width)
        if fill_width > 0:  # Pour éviter un dessin avec une largeur nulle
            fill_rect = pygame.Rect(x, y, fill_width, bar_height)
            pygame.draw.rect(screen, CRIMSON, fill_rect, border_radius=10)

        # Bordure de la barre de vie
        pygame.draw.rect(screen, WHITE, bg_rect, width=2, border_radius=10)
    
    # Fonction pour dessiner les Images d'actions (armes/touches)
    def draw_action_icons(self, screen):
        action_icon_size = 80 # Taille des Images d'attaque
        input_icon_size = 40 # Taille des Images des entrées
        padding = 20 # Espacement entre les Images
        vertical_offset = 40 # Décalage vertical supplémentaire pour l'input

        # L'Image pour le tir est à gauche et l'Image pour la mêlée à droite.
        x_shoot = 20
        x_melee = x_shoot + action_icon_size + padding
        y_action = SCREEN_HEIGHT - 150

        # Image pour le tir
        shoot_icon = pygame.image.load("assets/images/ui/playerui/shoot_icon.png").convert_alpha()
        shoot_icon = pygame.transform.scale(shoot_icon, (action_icon_size, action_icon_size))
        screen.blit(shoot_icon, (x_shoot, y_action))

        # Image des entrées en fonction de si on utilise la manette ou le clavier
        if self.player.using_gamepad: # Si on utilise la manette
            input_shoot_path = "assets/images/ui/buttons/button_RB.png"
        else: # Si on utilise le clavier
            input_shoot_path = "assets/images/ui/buttons/button_left_click.png"
        input_shoot_icon = pygame.image.load(input_shoot_path).convert_alpha() # On charge l'image
        input_shoot_icon = pygame.transform.scale(input_shoot_icon, (input_icon_size, input_icon_size)) # On redimensionne l'image
        # Centrage de l'input sur l'image pour le tir avec le décalage vertical
        shoot_center = (x_shoot + action_icon_size // 2, y_action + action_icon_size // 2 + vertical_offset)
        input_shoot_rect = input_shoot_icon.get_rect(center=shoot_center)
        screen.blit(input_shoot_icon, input_shoot_rect.topleft)

        # Image pour la mêlée
        melee_icon = pygame.image.load("assets/images/ui/playerui/melee_icon.png").convert_alpha()
        melee_icon = pygame.transform.scale(melee_icon, (action_icon_size, action_icon_size))
        screen.blit(melee_icon, (x_melee, y_action))

        # Image des entrées en fonction de si on utilise la manette ou le clavier
        if self.player.using_gamepad: # Si on utilise la manette
            input_melee_path = "assets/images/ui/buttons/button_RT.png"
        else: # Si on utilise le clavier
            input_melee_path = "assets/images/ui/buttons/button_right_click.png"
        input_melee_icon = pygame.image.load(input_melee_path).convert_alpha() # On charge l'image
        input_melee_icon = pygame.transform.scale(input_melee_icon, (input_icon_size, input_icon_size)) # On redimensionne l'image
        # Centrage de l'input sur l'image pour le tir avec le décalage vertical
        melee_center = (x_melee + action_icon_size // 2, y_action + action_icon_size // 2 + vertical_offset)
        input_melee_rect = input_melee_icon.get_rect(center=melee_center)
        screen.blit(input_melee_icon, input_melee_rect.topleft)

    # Fonction pour dessiner les statistiques du joueur (mort/pièces)
    def draw_stats(self, screen):
        margin = 20 # Marge par rapport au bord de l'écran
        ammo_bar_width = 20 # Largeur de la barre de munitions
        ammo_bar_padding = 10 # Espace entre les stats et la barre
        reserved_space = ammo_bar_width + ammo_bar_padding
        # On aligne les stats à gauche de l'espace réservé
        stats_right_x = SCREEN_WIDTH - margin - reserved_space

        # Pièces
        coins_icon = pygame.image.load("assets/images/items/fragments.png").convert_alpha() # Chargement de l'image des pièces et conversion pour la transparence
        coins_icon = pygame.transform.scale(coins_icon, (30, 30)) # Redimensionne l'image

        # Afficher le texte du nombre de pièces du joueur
        coins_surface = self.font.render(str(self.player.coins), True, WHITE)
        coins_rect = coins_surface.get_rect() # On récupère le rectangle du texte
        coins_icon_rect = coins_icon.get_rect() # On récupère le rectangle de l'image des pièces

        # Espace entre le texte et l'image des pièces
        padding_between = 10

        # Calcul de la largeur totale du bloc contenant le texte et l'image
        block_width = coins_rect.width + padding_between + coins_icon_rect.width
        # Calcul de la hauteur du bloc en récupérant la hauteur maximale entre le texte et l'image
        block_height = max(coins_rect.height, coins_icon_rect.height)

        # Calcul de la position x du bloc de pièces (aligné à droite)
        coins_block_x = stats_right_x - block_width
        # Calcul de la position y du bloc de pièces (aligné en bas)
        coins_block_y = SCREEN_HEIGHT - margin - block_height

        # Calcul de la position y du texte des pièces pour le centrer verticalement dans le bloc
        coins_text_y = coins_block_y + (block_height - coins_rect.height) // 2
        # Calcul de la position y de l'image des pièces pour la centrer verticalement dans le bloc
        coins_icon_y = coins_block_y + (block_height - coins_icon_rect.height) // 2

        # Affichage du texte des pièces à l'écran
        screen.blit(coins_surface, (coins_block_x, coins_text_y))
        # Affichage de l'icône des pièces à l'écran, avec un décalage horizontal pour laisser de l'espace pour le texte
        screen.blit(coins_icon, (coins_block_x + coins_rect.width + padding_between, coins_icon_y))


        # Morts
        deaths_icon = pygame.image.load("assets/images/ui/playerui/skull_icon.png").convert_alpha() # Chargement de l'image de mort et conversion pour la transparence
        deaths_icon = pygame.transform.scale(deaths_icon, (30, 30)) # Redimensionne l'image
        
        # Afficher le texte du nombre de morts du joueur
        deaths_surface = self.font.render(str(self.player.deaths), True, WHITE)
        deaths_rect = deaths_surface.get_rect() # On récupère le rectangle du texte
        deaths_icon_rect = deaths_icon.get_rect() # On récupère le rectangle de l'image de mort

        # Calcul de la largeur totale du bloc contenant le texte et l'image
        deaths_block_width = deaths_rect.width + padding_between + deaths_icon_rect.width
        # Calcul de la hauteur du bloc en récupérant la hauteur maximale entre le texte et l'image
        deaths_block_height = max(deaths_rect.height, deaths_icon_rect.height)
        # Calcul de la position x du bloc de pièces (aligné à droite)
        deaths_block_x = stats_right_x - deaths_block_width
        # Calcul de la hauteur du bloc en récupérant la hauteur maximale entre le texte et l'image
        spacing = 10  # Espace entre les deux blocs (pièces/morts)
        deaths_block_y = coins_block_y - spacing - deaths_block_height

        # Calcul de la position y du texte des pièces pour le centrer verticalement dans le bloc
        deaths_text_y = deaths_block_y + (deaths_block_height - deaths_rect.height) // 2
        # Calcul de la position y de l'image des pièces pour la centrer verticalement dans le bloc
        deaths_icon_y = deaths_block_y + (deaths_block_height - deaths_icon_rect.height) // 2

        # Affichage du texte des pièces à l'écran
        screen.blit(deaths_surface, (deaths_block_x, deaths_text_y))
        # Affichage de l'icône des pièces à l'écran, avec un décalage horizontal pour laisser de l'espace pour le texte
        screen.blit(deaths_icon, (deaths_block_x + deaths_rect.width + padding_between, deaths_icon_y))

        # Sauvegarde la zone verticale occupée par les stats pour centrer la barre de munitions
        self.stats_area_top = deaths_block_y
        self.stats_area_bottom = coins_block_y + block_height
    
    # Fonction pour dessiner la barre de munitions
    def draw_ammo_bar(self, screen):
        bar_width = 20 # Largeur de la barre de munitions
        bar_height = 100 # Hauteur de la barre de munitions
        margin = 20 # Marge par rapport au bord de l'écran
        ammo_bar_padding = 10 # Espace de remplissage pour la barre de munitions

        # Position horizontale de la barre (alignée à droite des statistiques avec la marge)
        bar_x = SCREEN_WIDTH - margin - bar_width

        # Position verticale pour centrer la barre par rapport à la zone des statistiques
        if hasattr(self, 'stats_area_top') and hasattr(self, 'stats_area_bottom'):
            stats_area_height = self.stats_area_bottom - self.stats_area_top
            bar_y = self.stats_area_top + (stats_area_height - bar_height) // 2
        else:
            bar_y = SCREEN_HEIGHT - margin - bar_height

        # Calcul du pourcentage de munitions restantes
        progress = self.weapon.ammo / self.weapon.max_ammo

        # Dessiner une ombre pour la barre de munitions
        shadow_offset = 2 # Décalage pour l'ombre
        shadow_rect = pygame.Rect(bar_x + shadow_offset, bar_y + shadow_offset, bar_width, bar_height)
        pygame.draw.rect(screen, BLACK, shadow_rect, border_radius=5)

        # Fond de la barre de munitions
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, BLACK_GRAY, bg_rect, border_radius=5)

        # Partie remplie de la barre (du bas vers le haut)
        fill_height = int(progress * bar_height)
        if fill_height > 0:
            fill_rect = pygame.Rect(bar_x, bar_y + (bar_height - fill_height), bar_width, fill_height)
            pygame.draw.rect(screen, GOLD, fill_rect, border_radius=5)

        # Bordure de la barre de munitions
        pygame.draw.rect(screen, WHITE, bg_rect, width=2, border_radius=5)

    # Fonction pour dessiner les textes
    def draw_text(self, screen, text, x, y):
        # Rendu du texte avec la police et la couleur blanche
        rendered_text = self.font.render(text, True, WHITE)
        # Affichage du texte à l'écran aux coordonnées spécifiées
        screen.blit(rendered_text, (x, y))



# Classe d'animation de transition entre niveau
class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction # Direction du fondu (1 pour un fondu spécifique)
        self.color = color # Couleur du fondu
        self.speed = speed # Vitesse du fondu
        self.fade_counter = 0 # Compteur pour la progression du fondu

    # Fonction pour le fondu
    def fade(self, screen):
        fade_complete = False # Le fondu est-il terminé ?
        self.fade_counter += self.speed # Incrémentation du compteur de fondu par la vitesse

        # Si la direction est 1 dessiner les rectangles pour le fondu
        if self.direction == 1:
            # Dessine des rectangles pour créer l'effet de fondu
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Vérifier si le fondu est fini
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete  # Retourne si le fondu est fini ou non


# Classe pour afficher l'écran des PowerUp
class PowerupScreen:
    def __init__(self, powerup, font):
        self.powerup = powerup
        # Chargement de l'image de la carte powerup
        self.powerup_image = pygame.image.load(f"assets/images/ui/powerup/card_{self.powerup}.png").convert_alpha()
        
        # Grossir la carte en appliquant un facteur de mise à l'échelle
        scale_factor = 2.0
        new_width = int(self.powerup_image.get_width() * scale_factor)
        new_height = int(self.powerup_image.get_height() * scale_factor)
        self.powerup_image = pygame.transform.scale(self.powerup_image, (new_width, new_height))
        
        self.card_y = SCREEN_HEIGHT  # Position initiale de la carte en dehors de l'écran
        # Recalcule la position cible en fonction de la taille de l'image
        self.card_target_y = SCREEN_HEIGHT // 2 - self.powerup_image.get_height() // 2
        self.animation_speed = 10  # Vitesse du mouvement de l'animation

        self.animation_complete = False 
        self.font = font 
        self.done = False  # Indique si l'écran a été fermé 

    # Fonction pour l'animation de la carte de powerup
    def animate_card(self):
        if self.card_y > self.card_target_y:
            self.card_y -= self.animation_speed
        else:
            self.animation_complete = True

    # Fonction pour dessiner l'écran du powerup 
    def draw(self, screen):
        screen.fill(BLACK)  # Fond noir

        # Animation d'apparition
        if not self.animation_complete: 
            self.animate_card() 

        # Affichage du power-up 
        screen.blit(self.powerup_image, (SCREEN_WIDTH // 2 - self.powerup_image.get_width() // 2, self.card_y)) 

        # Texte en bas pour les touches
        if self.animation_complete: 
            button_text = self.font.render("Cliquer sur A / clic droit", True, WHITE)
            button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(button_text, button_rect)
