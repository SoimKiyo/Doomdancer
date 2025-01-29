import pygame 
import math

class Weapon():
    def __init__(self, image, joysticks):
        self.original_image = image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.joysticks = joysticks


    def update(self, player):
            self.rect.center = player.rect.center

            # Récupère la position de la souris par défaut
            pos = pygame.mouse.get_pos()

            for joystick in self.joysticks:
                if joystick.get_numaxes() >= 4:
                    horiz_move = joystick.get_axis(2)
                    vert_move = joystick.get_axis(3)

                    if (abs(horiz_move) or abs(vert_move)) > 0.15:
                        pos = (self.rect.centerx + horiz_move, self.rect.centery + vert_move)

            # Calcul de l'angle entre la position actuelle et la cible
            x_dist = pos[0] - self.rect.centerx
            y_dist = pos[1] - self.rect.centery

            self.angle = math.degrees(math.atan2(y_dist, x_dist))

    def draw(self, surface):
        """Dessine l'image avec la bonne rotation"""
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), self.rect.centery - int(self.image.get_height()/2)))