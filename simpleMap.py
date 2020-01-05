# Генерирует только карту

import pygame
import data.maps.tmx as tmx

pygame.init()
screen = pygame.display.set_mode((500, 500))

# tmx.load анализирует myMap.tmx файл и возвращает tilemap со всеми соответствующими атрибутами.
# Примечание. необходимо также указать размер видового экрана.
tilemap = tmx.load('D:/Лицей_Проекты/Pygame_Platformer/data/maps/testing.tmx', screen.get_size())

# Установите фокус представления tilemap на координату x, y.
# Обычно это будет установлено в исходное положение спрайта основного игрока.
tilemap.set_focus(0, 0)
clock = pygame.time.Clock()

while 1:
    dt = clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    # tilemap.update вызывает метод update для каждого слоя карты.
    # Метод update можно настроить для каждого слоя,
    # чтобы включить логику для анимации позиций спрайтов и обнаружения пересечений.
    tilemap.update(dt)
    # Заполните экран цветом R, G, B, чтобы стереть предыдущие рисунки.
    screen.fill((0, 0, 0))
    # Нарисуйте все слои tilemap на экране.
    tilemap.draw(screen)
    # Обновите окно отображения.
    pygame.display.flip()
