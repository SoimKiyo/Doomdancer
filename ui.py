import pygame

# Classe de dégats (Affiche un texte quand il y a des dégâtes fait sur l'ennemie)
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 36)
        self.image = self.font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0
    def update(self):
        # Déplacer le texte de dégât vers le haut
        self.rect.y -= 1
        # Supprimer le compte après quelques secondes
        self.counter += 1
        if self.counter > 30:
            self.kill()
