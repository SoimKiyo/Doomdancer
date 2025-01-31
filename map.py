import pygame
import csv
from constants import *

# Charger les tiles de la map
tile_list = []
def map_sprites():
    for x in range(TILE_TYPES):
        tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
        tile_image = pygame.transform.scale(tile_image, (TILE_SIZE, TILE_SIZE))
        tile_list.append(tile_image)

# Variable du niveau à charger
level = 1

# Données de la map
world_data = []
for row in range(ROWS):
    r= [-1]*COLS
    world_data.append(r)
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

class World():
    def __init__(self):
        self.map_tiles = []

    def process_data(self, data, tile_list):
        self.level_lengh = len(data)
        # Reitérer pour chaque niveau du data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                image = tile_list[tile]
                image_rect = image.get_rect()
                image_x = x * TILE_SIZE
                image_y = y * TILE_SIZE
                image_rect.center = (image_x, image_y)
                tile_data = [image, image_rect, image_x, image_y]

                # Ajouter l'image data à la liste des tiles
                if tile >= 0:
                    self.map_tiles.append(tile_data)
    
    def update(self, screen_scroll):
        for tile in self.map_tiles:
            tile[2] += screen_scroll[0]
            tile[3] += screen_scroll[1]
            tile[1].center = (tile[2], tile[3])
                
    def draw(self, surface):
        for tile in self.map_tiles:
            surface.blit(tile[0], tile[1])