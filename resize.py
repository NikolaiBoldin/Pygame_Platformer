# Изменение разрешения картинки в N раз
import pygame


def resize(filename1, filename2, zoom):
    image = pygame.image.load(filename1)
    x, y = image.get_size()
    image = pygame.transform.scale(image, (x * zoom, y * zoom))
    pygame.image.save(image, filename2)


resize('data/tiles/tileset.png', 'data/tiles/tileset2.png', 2)
