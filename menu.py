import pygame

# Classe du menu
class Menu:
    # On initialise les options pour les menus en précisant les dimensions de la fenêtre
    def __init__(self, screen_width, screen_height):
        # Options du menu principal
        self.main_menu_options = ["Jouer", "Paramètres", "Quitter"] #Options pour le menu au démarrage
        self.pause_menu_options = ["Reprendre", "Paramètres", "Menu Principal"] #Options pour le menu pause
        self.selected = 0  # Indice de l'option sélectionnée
        self.is_pause_menu = False  # Le menu est t'il le menu de pause ?

        # Gestions des sous menus
        self.in_settings = False # Le menu est t'il le sous menu paramètres ?

        # Options des paramètres
        self.settings_options = ["Volume Musique", "Volume Effets", "Plein Écran", "Retour"] #Options pour le menu des paramètres
        self.music_volume = 0.5
        self.sound_effects_volume = 0.7
        self.fullscreen = False
        self.settings_selected = 0 # Indice de l'option sélectionnée

        # Dimensions de l'écran
        self.screen_width = screen_width
        self.screen_height = screen_height

    # Fonction pour afficher les menus (principal/pause/paramètres)
    def draw(self, screen, font_title, font_option):
        # Si le menu est le menu pause
        if self.is_pause_menu:
            screen.fill((30, 30, 30))  # Fond gris sombre
            title = font_title.render("PAUSE", True, (255, 215, 0))  # Or doré
        # Si le menu est le menu paramètres
        elif self.in_settings:
            screen.fill((20, 20, 50))  # Fond bleu foncé
            title = font_title.render("PARAMÈTRES", True, (135, 206, 235))  # Bleu clair
        # Si le menu est le menu principal
        else:
            screen.fill((10, 10, 20))  # Fond noir bleuté
            title = font_title.render("DOOMDANCER", True, (255, 0, 0))  # Rouge vif

        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 80)) #Permet de centrer le titre horizontalement (Différence entre la largeur de l'écran et celle du texte)

        # Affichage des options selon le menu actif
        if self.in_settings:
            # Pour chaque option dans les options des paramètres
            for i, option in enumerate(self.settings_options):
                color = (255, 255, 255) if i == self.settings_selected else (150, 150, 150)
                if option == "Volume Musique":
                    option_text = f"{option} : {int(self.music_volume * 100)}%"
                elif option == "Volume Effets":
                    option_text = f"{option} : {int(self.sound_effects_volume * 100)}%"
                elif option == "Plein Écran":
                    option_text = f"{option} : {'Oui' if self.fullscreen else 'Non'}"
                else:
                    option_text = option

                text = font_option.render(option_text, True, color)
                screen.blit(text, (self.screen_width // 2 - text.get_width() // 2, 200 + i * 50)) #Permet de centrer le texte horizontalement
        else:
            # Sinon si c'est le menu principal ou le menu principal
            options = self.pause_menu_options if self.is_pause_menu else self.main_menu_options
            for i, option in enumerate(options):
                color = (255, 255, 255) if i == self.selected else (150, 150, 150)
                text = font_option.render(option, True, color)
                screen.blit(text, (self.screen_width // 2 - text.get_width() // 2, 200 + i * 50)) #Permet de centrer le texte horizontalement

    # Fonction pour gérer les entrées dans le menu
    def handle_input(self, event):
        # Si les entrées sont des touches pressé
        if event.type == pygame.KEYDOWN:
            # Si ce n'est pas le menu des paramètres
            if not self.in_settings:
                # Navigation dans le menu principal ou pause
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % (len(self.pause_menu_options) if self.is_pause_menu else len(self.main_menu_options)) # Permet de sélectionner l'élement du haut
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % (len(self.pause_menu_options) if self.is_pause_menu else len(self.main_menu_options)) # Permet de sélectionner l'élément du bas
                elif event.key == pygame.K_RETURN: # Permet de gérer l'action quand on presse la touche entrée
                    # Si c'est le menu pause
                    if self.is_pause_menu:
                        return self.handle_pause_selection()
                    # Si c'est le menu principal
                    else:
                        return self.handle_main_menu_selection()
            
            # Si c'est le menu des paramètres
            else:
                # Navigation dans les paramètres
                if event.key == pygame.K_UP:
                    self.settings_selected = (self.settings_selected - 1) % len(self.settings_options) # Permet de sélectionner l'élement du haut
                elif event.key == pygame.K_DOWN:
                    self.settings_selected = (self.settings_selected + 1) % len(self.settings_options) # Permet de sélectionner l'élément du bas
                elif event.key == pygame.K_RIGHT: # Permet de changer la valeur de l'élément sélectionné vers des valeur plus grande
                    #Si c'est le premier élément c'est à dire le volume
                    if self.settings_selected == 0:
                        self.music_volume = min(1.0, self.music_volume + 0.1) #Augmente
                    #Si c'est les effets sonnores
                    elif self.settings_selected == 1:
                        self.sound_effects_volume = min(1.0, self.sound_effects_volume + 0.1) #Augmente
                    # Si c'est le plein écran
                    elif self.settings_selected == 2:
                        self.fullscreen = True #Active
                elif event.key == pygame.K_LEFT: # Permet de changer la valeur de l'élément sélectionné vers des valeur plus basse
                    if self.settings_selected == 0:
                        self.music_volume = max(0.0, self.music_volume - 0.1) #Diminue
                    elif self.settings_selected == 1:
                        self.sound_effects_volume = max(0.0, self.sound_effects_volume - 0.1) #Diminue
                    elif self.settings_selected == 2:
                        self.fullscreen = False #Désactive
                elif event.key == pygame.K_RETURN: # Si on appuie sur la touche entrée
                    if self.settings_selected == 3:  # Retourne en arrière
                        self.in_settings = False
        return None

    # Fonctions pour gérer les sélections dans le menu principal
    def handle_main_menu_selection(self):
        if self.selected == 0:  # Jouer
            return "play"
        elif self.selected == 1:  # Paramètres
            self.in_settings = True
            self.settings_selected = 0
        elif self.selected == 2:  # Quitter
            return "quit"

    # Fonctions pour gérer les sélections dans le menu pause
    def handle_pause_selection(self):
        if self.selected == 0:  # Reprendre
            return "resume"
        elif self.selected == 1:  # Paramètres
            self.in_settings = True
            self.settings_selected = 0
        elif self.selected == 2:  # Menu Principal
            return "menu"

    # Fonctions pour appliquer les paramètres (ici le plein éran)
    def apply_settings(self, screen):
        if self.fullscreen:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Remettre à la taille par défaut
            return pygame.display.set_mode((800, 600))
