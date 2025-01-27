import pygame

# Initialisation des Variables 
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Initialisation de Pygame
pygame.init
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Doomdancer")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Création des instances principales
# ...

# Variable d'état
running = True

# Boucle principale
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()