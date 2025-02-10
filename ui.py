import pygame
from constants import *

# Classe de dégats (Affiche un texte quand il y a des dégâtes fait sur l'ennemie)
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color, screen_scroll):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("assets/other/fonts/font.otf", 24)
        self.image = self.font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0
        self.screen_scroll = screen_scroll

    def update(self):
        # Repositionner par rapport au scroll de l'écran
        self.rect.x += self.screen_scroll[0]
        self.rect.y += self.screen_scroll[1]
        
        # Déplacer le texte de dégât vers le haut
        self.rect.y -= 1
        # Supprimer le compte après quelques secondes
        self.counter += 1
        if self.counter > 30:
            self.kill()
            

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

    def draw_health_bar(self, screen):
        """Dessine une barre de vie stylisée avec coins arrondis et ombre, en bas à gauche."""
        health_ratio = self.player.health / self.player.max_health
        bar_width, bar_height = 300, 20
        x, y = 20, SCREEN_HEIGHT - 50

        # Dessiner une ombre pour donner un effet de profondeur
        shadow_offset = 3
        shadow_rect = pygame.Rect(x + shadow_offset, y + shadow_offset, bar_width, bar_height)
        pygame.draw.rect(screen, BLACK, shadow_rect, border_radius=10)

        # Fond de la barre (partie vide)
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(screen, BLACK_GRAY, bg_rect, border_radius=10)

        # Portion de vie (remplie) selon le ratio de vie
        fill_width = int(health_ratio * bar_width)
        if fill_width > 0:  # Pour éviter un dessin avec une largeur nulle
            fill_rect = pygame.Rect(x, y, fill_width, bar_height)
            pygame.draw.rect(screen, CRIMSON, fill_rect, border_radius=10)

        # Bordure
        pygame.draw.rect(screen, WHITE, bg_rect, width=2, border_radius=10)

    def draw_action_icons(self, screen):
        """Affiche les icônes d'attaque agrandies avec leurs inputs (en icônes) centrés, avec un petit décalage vers le bas,
        en intervertissant les positions en x de l'attaque de mêlée et du tir."""
        action_icon_size = 80   # Taille des icônes d'attaque
        input_icon_size = 40    # Taille des icônes de contrôles
        padding = 20            # Espacement entre les icônes
        vertical_offset = 40    # Décalage vertical supplémentaire pour l'input

        # On définit la nouvelle position de départ :
        # L'icône de tir sera à gauche et l'icône de mêlée à droite.
        x_shoot = 20
        x_melee = x_shoot + action_icon_size + padding
        y_action = SCREEN_HEIGHT - 150

        # --- Icône de tir (maintenant à gauche) ---
        shoot_icon = pygame.image.load("assets/images/ui/playerui/shoot_icon.png").convert_alpha()
        shoot_icon = pygame.transform.scale(shoot_icon, (action_icon_size, action_icon_size))
        screen.blit(shoot_icon, (x_shoot, y_action))

        # Choix de l'icône input pour le tir
        if self.player.using_gamepad:
            input_shoot_path = "assets/images/ui/buttons/button_RB.png"
        else:
            input_shoot_path = "assets/images/ui/buttons/button_left_click.png"
        input_shoot_icon = pygame.image.load(input_shoot_path).convert_alpha()
        input_shoot_icon = pygame.transform.scale(input_shoot_icon, (input_icon_size, input_icon_size))
        # Centrage de l'input sur l'icône de tir avec décalage vertical
        shoot_center = (x_shoot + action_icon_size // 2, y_action + action_icon_size // 2 + vertical_offset)
        input_shoot_rect = input_shoot_icon.get_rect(center=shoot_center)
        screen.blit(input_shoot_icon, input_shoot_rect.topleft)

        # --- Icône de mêlée (maintenant à droite) ---
        melee_icon = pygame.image.load("assets/images/ui/playerui/melee_icon.png").convert_alpha()
        melee_icon = pygame.transform.scale(melee_icon, (action_icon_size, action_icon_size))
        screen.blit(melee_icon, (x_melee, y_action))

        # Choix de l'icône input pour la mêlée
        if self.player.using_gamepad:
            input_melee_path = "assets/images/ui/buttons/button_RT.png"
        else:
            input_melee_path = "assets/images/ui/buttons/button_right_click.png"
        input_melee_icon = pygame.image.load(input_melee_path).convert_alpha()
        input_melee_icon = pygame.transform.scale(input_melee_icon, (input_icon_size, input_icon_size))
        # Centrage de l'input sur l'icône de mêlée avec décalage vertical
        melee_center = (x_melee + action_icon_size // 2, y_action + action_icon_size // 2 + vertical_offset)
        input_melee_rect = input_melee_icon.get_rect(center=melee_center)
        screen.blit(input_melee_icon, input_melee_rect.topleft)



    def draw_stats(self, screen):
        """
        Affiche les statistiques (pièces et morts) en bas à droite.
        Pour laisser de la place à la barre de munitions, on réserve un espace à droite.
        Chaque bloc affiche le nombre (texte) suivi de son icône.
        """
        margin = 20              # Marge par rapport au bord de l'écran
        ammo_bar_width = 20      # Largeur de la barre de munitions
        ammo_bar_padding = 10    # Espace entre les stats et la barre
        reserved_space = ammo_bar_width + ammo_bar_padding
        # On aligne les stats à gauche de l'espace réservé
        stats_right_x = SCREEN_WIDTH - margin - reserved_space

        # --- Bloc Pièces ---
        coins_icon = pygame.image.load("assets/images/items/fragments.png").convert_alpha()
        coins_icon = pygame.transform.scale(coins_icon, (30, 30))
        coins_surface = self.font.render(str(self.player.coins), True, WHITE)
        coins_rect = coins_surface.get_rect()
        coins_icon_rect = coins_icon.get_rect()
        padding_between = 10  # Espace entre texte et icône
        block_width = coins_rect.width + padding_between + coins_icon_rect.width
        block_height = max(coins_rect.height, coins_icon_rect.height)

        coins_block_x = stats_right_x - block_width
        coins_block_y = SCREEN_HEIGHT - margin - block_height  # Bloc aligné en bas
        coins_text_y = coins_block_y + (block_height - coins_rect.height) // 2
        coins_icon_y = coins_block_y + (block_height - coins_icon_rect.height) // 2
        screen.blit(coins_surface, (coins_block_x, coins_text_y))
        screen.blit(coins_icon, (coins_block_x + coins_rect.width + padding_between, coins_icon_y))

        # --- Bloc Morts (placé au-dessus du bloc pièces) ---
        deaths_icon = pygame.image.load("assets/images/ui/playerui/skull_icon.png").convert_alpha()
        deaths_icon = pygame.transform.scale(deaths_icon, (30, 30))
        deaths_surface = self.font.render(str(self.player.deaths), True, WHITE)
        deaths_rect = deaths_surface.get_rect()
        deaths_icon_rect = deaths_icon.get_rect()
        deaths_block_width = deaths_rect.width + padding_between + deaths_icon_rect.width
        deaths_block_height = max(deaths_rect.height, deaths_icon_rect.height)
        deaths_block_x = stats_right_x - deaths_block_width
        spacing = 10  # Espace entre les deux blocs
        deaths_block_y = coins_block_y - spacing - deaths_block_height
        deaths_text_y = deaths_block_y + (deaths_block_height - deaths_rect.height) // 2
        deaths_icon_y = deaths_block_y + (deaths_block_height - deaths_icon_rect.height) // 2
        screen.blit(deaths_surface, (deaths_block_x, deaths_text_y))
        screen.blit(deaths_icon, (deaths_block_x + deaths_rect.width + padding_between, deaths_icon_y))

        # Sauvegarde la zone verticale occupée par les stats pour centrer la barre de munitions
        self.stats_area_top = deaths_block_y
        self.stats_area_bottom = coins_block_y + block_height

    def draw_ammo_bar(self, screen):
        """
        Affiche une barre verticale de munitions stylisée à droite des stats.
        La barre représente le ratio d'ammunitions actuelles sur le maximum.
        """
        bar_width = 20
        bar_height = 100   # Hauteur de la barre
        margin = 20
        ammo_bar_padding = 10

        # Position horizontale : à droite des stats, en respectant la marge
        bar_x = SCREEN_WIDTH - margin - bar_width

        # Position verticale : centrer la barre par rapport à la zone des stats
        if hasattr(self, 'stats_area_top') and hasattr(self, 'stats_area_bottom'):
            stats_area_height = self.stats_area_bottom - self.stats_area_top
            bar_y = self.stats_area_top + (stats_area_height - bar_height) // 2
        else:
            bar_y = SCREEN_HEIGHT - margin - bar_height

        progress = self.weapon.ammo / self.weapon.max_ammo

        # Dessiner une ombre pour la barre de munitions
        shadow_offset = 2
        shadow_rect = pygame.Rect(bar_x + shadow_offset, bar_y + shadow_offset, bar_width, bar_height)
        pygame.draw.rect(screen, BLACK, shadow_rect, border_radius=5)

        # Fond de la barre
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, BLACK_GRAY, bg_rect, border_radius=5)

        # Portion remplie (du bas vers le haut)
        fill_height = int(progress * bar_height)
        if fill_height > 0:
            fill_rect = pygame.Rect(bar_x, bar_y + (bar_height - fill_height), bar_width, fill_height)
            pygame.draw.rect(screen, GOLD, fill_rect, border_radius=5)

        # Bordure de la barre
        pygame.draw.rect(screen, WHITE, bg_rect, width=2, border_radius=5)

    def draw_text(self, screen, text, x, y):
        rendered_text = self.font.render(text, True, WHITE)
        screen.blit(rendered_text, (x, y))


# Classe d'animation de transition entre niveau
class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0
    
    def fade(self, screen):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 -self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete

# Classe pour afficher l'écran des PowerUp
class PowerupScreen:
    def __init__(self, powerup, font):
        self.powerup = powerup
        # Chargement de l'image de la carte powerup
        self.powerup_image = pygame.image.load(f"assets/images/ui/powerup/card_{self.powerup}.png").convert_alpha()
        
        # Grossir la carte en appliquant un facteur de mise à l'échelle (passé de 1.5 à 2.0)
        scale_factor = 2.0
        new_width = int(self.powerup_image.get_width() * scale_factor)
        new_height = int(self.powerup_image.get_height() * scale_factor)
        self.powerup_image = pygame.transform.scale(self.powerup_image, (new_width, new_height))
        
        self.card_y = SCREEN_HEIGHT  # Position initiale de la carte en dehors de l'écran
        # Recalcule la position cible en fonction de la nouvelle taille de l'image
        self.card_target_y = SCREEN_HEIGHT // 2 - self.powerup_image.get_height() // 2
        self.animation_speed = 10  # Vitesse du mouvement de l'animation

        self.animation_complete = False 
        self.font = font 
        self.done = False  # Indique si l'écran a été fermé 

    def handle_input(self, event):
        """Ferme l'écran si le joueur appuie sur A (bouton de la manette/clavier) ou effectue un clic droit."""
        if self.animation_complete:
            # Bouton A (ou touche A sur le clavier)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                self.done = True  # Fermer l’écran
                return True
            # Clic droit de la souris
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.done = True
                return True
        return False

    def animate_card(self):
        """Animation de l'apparition de la carte"""
        if self.card_y > self.card_target_y:
            self.card_y -= self.animation_speed
        else:
            self.animation_complete = True

    def draw(self, screen):
        screen.fill(BLACK)  # Fond noir

        # Animation d'apparition
        if not self.animation_complete: 
            self.animate_card() 

        # Affichage du power-up 
        screen.blit(self.powerup_image, (SCREEN_WIDTH // 2 - self.powerup_image.get_width() // 2, self.card_y)) 

        # Texte d'instruction (raccourci)
        if self.animation_complete: 
            button_text = self.font.render("Cliquer sur A / clic droit", True, WHITE)
            button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(button_text, button_rect)
