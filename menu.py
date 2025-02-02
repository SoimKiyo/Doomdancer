import pygame

# Classe du menu
class Menu:
    def __init__(self, screen_width, screen_height):
        
        # Options du menu principal
        self.main_menu_options = ["Jouer", "Paramètres", "Quitter"]
        # Options du menu pause
        self.pause_menu_options = ["Reprendre", "Paramètres", "Menu Principal"]
        self.selected = 0 # Index de l'option sélectionnée
        self.is_pause_menu = False # Le menu pause est t'il actif ?
        self.in_settings = False # Le menu paramètres est t'il actif ?

        # Options du menu des paramètres
        self.settings_options = ["Volume Musique", "Volume Effets", "Retour"]
        self.music_volume = 0.5
        self.sound_effects_volume = 0.7
        #self.fullscreen = False
        self.settings_selected = 0 # Index de l'option sélectionnée

        # Dimensions de l'écran
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Position verticale du premier élément du menu
        self.option_start_y = 200
        self.option_spacing = 50

    # Fonction pour afficher les menu
    def draw(self, screen, font_title, font_option):
        # Déterminer quel menu afficher (Pause, Paramètres, ou Principal)
        if self.is_pause_menu:
            screen.fill((30, 30, 30)) # Fond gris foncé pour le menu pause
            title = font_title.render("PAUSE", True, (255, 215, 0)) # Texte jaune
        elif self.in_settings:
            screen.fill((20, 20, 50)) # Fond bleu foncé pour les paramètres
            title = font_title.render("PARAMÈTRES", True, (135, 206, 235)) # Texte bleu clair
        else:
            screen.fill((10, 10, 20)) # Fond noir pour le menu principal
            title = font_title.render("DOOMDANCER", True, (255, 0, 0)) # Texte rouge

        # Affichage du titre centré en haut de l'écran
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 80))

        # Affichage des options selon le menu actuel
        if self.in_settings:
            for i, option in enumerate(self.settings_options):
                # Détermine la couleur de l'option sélectionnée
                color = (255, 255, 255) if i == self.settings_selected else (150, 150, 150)
                # Affiche la valeur des paramètres si besoins
                option_text = f"{option} : {int(self.music_volume * 100)}%" if option == "Volume Musique" else \
                              f"{option} : {int(self.sound_effects_volume * 100)}%" if option == "Volume Effets" else option
                              #f"{option} : {'Oui' if self.fullscreen else 'Non'}" if option == "Plein Écran" else option
                text = font_option.render(option_text, True, color)
                screen.blit(text, (self.screen_width // 2 - text.get_width() // 2, 200 + i * 50))
        else:
            # Déterminer les options à afficher (Menu principal ou menu pause)
            options = self.pause_menu_options if self.is_pause_menu else self.main_menu_options
            for i, option in enumerate(options):
                color = (255, 255, 255) if i == self.selected else (150, 150, 150)

                text = font_option.render(option, True, color)
                text_x = self.screen_width // 2 - text.get_width() // 2
                text_y = self.option_start_y + i * self.option_spacing
                screen.blit(text, (text_x, text_y))

    # Fonction pour gérer les entrées clavier/manette dans les menu
    def handle_input(self, event):
        # Vérifie si un événement a était déclanché par une touche de clavier, un bouton de manette ou le D-Pad
        if event.type in (pygame.KEYDOWN, pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION):
            # Récupère la touche du clavier si l'événement concerne le clavier, sinon None
            key = getattr(event, 'key', None)
            # Récupère le bouton de la manette si l'événement concerne la manette, sinon None
            button = getattr(event, 'button', None)
            # Récupère la direction du D-Pad si l'événement concerne la croix directionnelle, sinon (0, 0)
            hat_value = getattr(event, 'value', (0, 0))

            # Si on n'est pas dans le menu des paramètres
            if not self.in_settings:
                # Aller vers le haut (flèche haut, Z, ou D-Pad haut)
                if key in (pygame.K_UP, pygame.K_w) or hat_value[1] == 1:
                    self.selected = (self.selected - 1) % (len(self.pause_menu_options) if self.is_pause_menu else len(self.main_menu_options))
                # Aller vers le bas (flèche bas, S, ou D-Pad bas)
                elif key in (pygame.K_DOWN, pygame.K_s) or hat_value[1] == -1:
                    self.selected = (self.selected + 1) % (len(self.pause_menu_options) if self.is_pause_menu else len(self.main_menu_options))
                # Valider (Touche Entrée ou bouton A de la manette)
                elif key == pygame.K_RETURN or button == 0:
                    return self.handle_pause_selection() if self.is_pause_menu else self.handle_main_menu_selection()
                # Retour (Echape ou bouton B de la manette)
                elif key == pygame.K_ESCAPE or button == 1:
                    self.in_settings = False
            # Sinon, si on est dans le menu des paramètres
            else:
                # Aller vers le haut (flèche haut, Z, ou D-Pad haut)
                if key in (pygame.K_UP, pygame.K_w) or hat_value[1] == 1:
                    self.settings_selected = (self.settings_selected - 1) % len(self.settings_options)
                # Aller vers le bas (flèche bas, S, ou D-Pad bas)
                elif key in (pygame.K_DOWN, pygame.K_s) or hat_value[1] == -1:
                    self.settings_selected = (self.settings_selected + 1) % len(self.settings_options)
                # Augmenter une valeur (flèche droite, D-Pad droit)
                elif key in (pygame.K_RIGHT, pygame.K_d) or hat_value[0] == 1:
                    if self.settings_selected == 0: # Musique
                        self.music_volume = min(1.0, self.music_volume + 0.1)
                    elif self.settings_selected == 1: # Effets sonores
                        self.sound_effects_volume = min(1.0, self.sound_effects_volume + 0.1)
                    #elif self.settings_selected == 2: # Plein écrans
                    #    self.fullscreen = True
                # Descendre une valeur (flèche gauche, D-Pad gauche)
                elif key in (pygame.K_LEFT,  pygame.K_q) or hat_value[0] == -1:
                    if self.settings_selected == 0: # Musique
                        self.music_volume = max(0.0, self.music_volume - 0.1)
                    elif self.settings_selected == 1: # Effets sonores
                        self.sound_effects_volume = max(0.0, self.sound_effects_volume - 0.1)
                    #elif self.settings_selected == 2: # Plein écrans
                    #    self.fullscreen = False
                # Valider (Touche Entrée ou bouton A de la manette)
                elif key == pygame.K_RETURN or button == 0:
                    if self.settings_selected == 2: # Retour au menu précédent
                        self.in_settings = False
                # Retour (Echape ou bouton B de la manette)
                elif key == pygame.K_ESCAPE or button == 1:
                    self.in_settings = False

        # Vérifie si un clic de souris a été fait ou si la souris est en mouvement
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            return self.handle_mouse(event.pos, click)

        
        # Retourne None par défaut (aucune action déclenchée)
        return None

    # Fonction pour gérer la souris dans les menus
    def handle_mouse(self, mouse_pos, click=False):
        x, y = mouse_pos # Récupère la position de la souris
        options = self.settings_options if self.in_settings else (self.pause_menu_options if self.is_pause_menu else self.main_menu_options) # Détermine les options du menu actuel (paramètres, pause ou menu principal)

        self.hovered_option = None  # Réinitialise l'option survolée

        # Parcours les options du menu
        for i, option in enumerate(options):
            option_y = self.option_start_y + i * self.option_spacing # Position Y de l'option
            option_x = self.screen_width // 2 - 100  # Centrage horizontal

            # Vérifie si la souris est sur une option
            if option_x <= x <= option_x + 200 and option_y <= y <= option_y + 40:
                self.hovered_option = i # Enregistre l'option survolée
                self.settings_selected = i if self.in_settings else i # Met à jour le hover
                self.selected = i # Met à jour l'option sélectionnée

                if click: # Si un clic a été détecté
                    if self.in_settings and i == 2: # Vérifie si "Retour" a été sélectionné dans les paramètres
                        self.in_settings = False # Ferme le menu des paramètres
                    else:
                        # Fait l'action correspondant à l'option sélectionnée
                        return self.handle_pause_selection() if self.is_pause_menu else self.handle_main_menu_selection()

        # Retourne None par défaut (aucune action déclenchée)
        return None


    # Fonction pour gérer la sélection d'une option dans le menu principal
    def handle_main_menu_selection(self):
        if self.selected == 0:
            return "play"
        elif self.selected == 1:
            self.in_settings = True
            self.settings_selected = 0
        elif self.selected == 2:
            return "quit"

    # Fonction pour gérer la sélection d'une option dans le menu pause
    def handle_pause_selection(self):
        if self.selected == 0:
            return "resume"
        elif self.selected == 1:
            self.in_settings = True
            self.settings_selected = 0
        elif self.selected == 2:
            return "menu"

    # Fonction pour appliquer les paramètres (ici le plein écran)
    #def apply_settings(self, screen):
    #    return pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if self.fullscreen else pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
