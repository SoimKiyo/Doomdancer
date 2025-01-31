import pygame

# Classe de dégats (Affiche un texte quand il y a des dégâtes fait sur l'ennemie)
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color, screen_scroll):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 36)
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
