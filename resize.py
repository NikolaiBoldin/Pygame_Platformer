# Изменение разрешения картинки в N раз
import pygame
import os


def resize(filename1, filename2, zoom):
    image = pygame.image.load(filename1)
    x, y = image.get_size()
    image = pygame.transform.scale(image, (x * zoom, y * zoom))
    pygame.image.save(image, filename2)


resize('data/sprites/Skelet/Skeleton Walk.png', 'data/sprites/Skelet/Skeleton Walk.png', 2)
resize('data/sprites/Skelet/Skeleton React.png', 'data/sprites/Skelet/Skeleton React.png', 2)
resize('data/sprites/Skelet/Skeleton Idle.png', 'data/sprites/Skelet/Skeleton Idle.png', 2)
resize('data/sprites/Skelet/Skeleton Hit.png', 'data/sprites/Skelet/Skeleton Hit.png', 2)
resize('data/sprites/Skelet/Skeleton Dead.png', 'data/sprites/Skelet/Skeleton Dead.png', 2)
resize('data/sprites/Skelet/Skeleton Attack.png', 'data/sprites/Skelet/Skeleton Attack.png', 2)