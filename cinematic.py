# cinematic.py
import pygame
import math
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE
from sfx import dialog_sound, scene1_sound, scene2_sound, scene3_sound, scene4_sound, scene5_sound

def wrap_text(text, font, max_width):
    """
    Découpe le texte en lignes qui ne dépassent pas max_width en pixels.
    """
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line != "" else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line != "":
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

class Cinematic:
    def __init__(self, screen, font):
        """
        Initialise la cinématique avec la fenêtre d'affichage et une police.
        Chaque scène est une liste de phrases qui seront animées une à une.
        """
        self.screen = screen
        self.font = font
        self.finished = False
        self.current_scene_index = 0

        # Définition des scènes (réduites et combinées)
        self.scenes = [
            [
                "Système en ligne... Erreur : données manquantes.",
                "Reconstruction de la mémoire... Statut : Unité autonome - Déconnectée du réseau."
            ],
            [
                "(Bruits d'interface corrompue, réveil et machine qui s'active.)",
                "L'écran s'illumine, révélant une silhouette dans l'obscurité."
            ],
            [
                "Unit A-1N se réveille dans une cité en ruine envahie par la nature.",
                "Bâtiments effondrés, forêts sur les rues et drones corrompus patrouillent au loin.",
                "Un symbole sur son torse s'illumine, témoignant de son humanité."
            ],
            [
                "Voix intérieure : 'Où suis-je ? Qui suis-je ? Pourquoi suis-je seule ?'"
            ],
            [
                "L'humanité a presque disparu. La nature et une force magique étrange ont repris le monde.",
                "Sa mission : retrouver les survivants et redonner espoir."
            ]
        ]

        # Liste des sons pour chaque scène
        self.scene_sounds = [
            scene1_sound,
            scene2_sound,
            scene3_sound,
            scene4_sound,
            scene5_sound
        ]

        # Paramètres d'animation
        self.char_delay = 30    # Délai (en ms) entre chaque caractère
        self.line_spacing = 5   # Espace entre les lignes
        self.max_text_width = SCREEN_WIDTH - 100  # On fixe une marge de 50 de chaque côté

    def run(self):
        """
        Lance la cinématique. Pour chaque scène, on anime chaque phrase.
        """
        clock = pygame.time.Clock()
        while not self.finished:
            if self.current_scene_index >= len(self.scenes):
                self.finished = True
                break

            # Joue le son illustrant la scène
            self.scene_sounds[self.current_scene_index].play()

            scene = self.scenes[self.current_scene_index]
            for sentence in scene:
                self.animate_sentence_with_indicator(sentence, clock)
            self.current_scene_index += 1
            pygame.time.delay(500)  # Délai entre les scènes
        return True

    def animate_sentence_with_indicator(self, sentence, clock):
        """
        Anime la phrase en affichant progressivement ses caractères,
        puis, une fois la phrase terminée, affiche un indicateur clignotant.
        """
        # Joue le son dialog (pour le texte) au début de la phrase
        dialog_sound.play()

        wrapped_lines = wrap_text(sentence, self.font, self.max_text_width)
        rendered_lines = ["" for _ in wrapped_lines]
        last_char_time = pygame.time.get_ticks()
        animating = True

        # Phase 1 : Animation progressive du texte
        while animating:
            dt = clock.tick(60)
            current_time = pygame.time.get_ticks()
            if current_time - last_char_time >= self.char_delay:
                for i, line in enumerate(wrapped_lines):
                    if len(rendered_lines[i]) < len(line):
                        rendered_lines[i] = line[:len(rendered_lines[i]) + 1]
                        break
                last_char_time = current_time

            self.screen.fill(BLACK)
            y_offset = SCREEN_HEIGHT // 2 - (len(rendered_lines) * self.font.get_height() + (len(rendered_lines)-1) * self.line_spacing) // 2
            for line in rendered_lines:
                rendered_text = self.font.render(line, True, WHITE)
                # Centrer horizontalement : calcule la position en x
                x_pos = (SCREEN_WIDTH - rendered_text.get_width()) // 2
                self.screen.blit(rendered_text, (x_pos, y_offset))
                y_offset += rendered_text.get_height() + self.line_spacing
            pygame.display.flip()

            if all(rendered_lines[i] == wrapped_lines[i] for i in range(len(wrapped_lines))):
                animating = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finished = True
                    return

        # Phase 2 : Affichage de l'indicateur clignotant jusqu'à ce que l'utilisateur appuie sur une touche
        waiting = True
        indicator_text = "Appuyez sur une touche..."
        indicator_surface = self.font.render(indicator_text, True, WHITE).convert_alpha()
        indicator_rect = indicator_surface.get_rect()
        # Centrer l'indicateur en bas
        indicator_rect.centerx = SCREEN_WIDTH // 2
        indicator_rect.bottom = SCREEN_HEIGHT - 50

        while waiting:
            dt = clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finished = True
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False

            alpha = int((math.sin(pygame.time.get_ticks() / 300.0) + 1) / 2 * 255)
            indicator_surface.set_alpha(alpha)

            self.screen.fill(BLACK)
            y_offset = SCREEN_HEIGHT // 2 - (len(rendered_lines) * self.font.get_height() + (len(rendered_lines)-1) * self.line_spacing) // 2
            for line in rendered_lines:
                rendered_text = self.font.render(line, True, WHITE)
                x_pos = (SCREEN_WIDTH - rendered_text.get_width()) // 2
                self.screen.blit(rendered_text, (x_pos, y_offset))
                y_offset += rendered_text.get_height() + self.line_spacing

            self.screen.blit(indicator_surface, indicator_rect.topleft)
            pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cinematic Test")
    # Utilise la police par défaut ou spécifie un chemin vers une police personnalisée
    font = pygame.font.Font(None, 32)
    cinematic = Cinematic(screen, font)
    cinematic.run()
    pygame.quit()
