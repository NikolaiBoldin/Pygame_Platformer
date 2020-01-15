import pygame
import os
import sys

pygame.init()
screen_size = WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode(screen_size)
FPS = 50
clock = pygame.time.Clock()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def action():
    pass


def button(x, y, width_b, height_b):
    mouse = pygame.mouse.get_pos()
    click_mouse = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width_b and y < mouse[1] < y + height_b:
        pygame.draw.rect(screen, (95, 158, 160), (x, y, width_b, height_b))
        if click_mouse[0] == 1:
            action()
    else:
        pygame.draw.rect(screen, (47, 79, 79), (x, y, width_b, height_b))
    font_b = pygame.font.Font('17810.ttf', 35)
    text = font_b.render(u'Начать игру', True, (176, 224, 230))
    screen.blit(text, (x + 10, y + 10))


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    pygame.font.init()
    myfont = pygame.font.Font('17810.ttf', 60)
    string_rendered = myfont.render(u'Witch adventure', 1, (47, 79, 79))
    screen.blit(string_rendered, (200, 50))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
            #  pause()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        button(320, 280, 240, 55)
        pygame.display.flip()
        clock.tick(FPS)


# def pause():
#   screen2 = pygame.display.set_mode(screen_size)
#  fon = pygame.transform.scale(load_image('заливка.jpg'), (WIDTH, HEIGHT))
#  screen2.blit(fon, (0, 0))
#  screen.blit(screen2, (0, 0))
#  pause = True
#  while pause:
#     for event in pygame.event.get():
#        if event.type == pygame.QUIT:
#            terminate()

#   if pygame.key.get_pressed()[pygame.K_RETURN]:
#      pause = False
#       start_screen()
# pygame.display.update()
# clock.tick(FPS)


start_screen()
pygame.quit()
