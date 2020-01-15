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


def button_control(x, y, width_b, height_b):
    mouse = pygame.mouse.get_pos()
    click_mouse = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width_b and y < mouse[1] < y + height_b:
        pygame.draw.rect(screen, (95, 158, 160), (x, y, width_b, height_b))
        if click_mouse[0] == 1:
            action()
    else:
        pygame.draw.rect(screen, (47, 79, 79), (x, y, width_b, height_b))
    font_b = pygame.font.Font('17810.ttf', 30)
    text = font_b.render(u'Управление', True, (176, 224, 230))
    screen.blit(text, (x + 10, y + 10))


def button_game(x, y, width_b, height_b):
    mouse = pygame.mouse.get_pos()
    click_mouse = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width_b and y < mouse[1] < y + height_b:
        pygame.draw.rect(screen, (95, 158, 160), (x, y, width_b, height_b))
        if click_mouse[0] == 1:
            action()
    else:
        pygame.draw.rect(screen, (47, 79, 79), (x, y, width_b, height_b))
    font_b = pygame.font.Font('17810.ttf', 26)
    text = font_b.render(u'Перейти к игре', True, (176, 224, 230))
    screen.blit(text, (x + 10, y + 10))


def start_screen():
    fon = pygame.transform.scale(load_image('fon_dark.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    pygame.font.init()
    myfont = pygame.font.Font('17810.ttf', 60)
    string_rendered = myfont.render(u'Witch adventure', 1, (47, 79, 79))
    screen.blit(string_rendered, (220, 50))
    intro_text = ["", "", "", "", ""
                                  "В нашей игре ведьма Моргана сталкивается",
                  " с разными испытаниями. На каждом уровне ",
                  "её ждет новое задание. Чтобы получить метлу, ",
                  "Ключ от тайной комнаты и суперспособности, ",
                  "Моргане придется бороться с монстрами и идти ",
                  "в нужном направлении. Но Моргана не сдается ",
                  "несмотря на все трудности."]
    newfont = pygame.font.Font('17810.ttf', 20)
    text_coord = 50
    for line in intro_text:
        string_rendered = newfont.render(line, 1, (176, 224, 230))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 180
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
            #  pause()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        button_control(130, 500, 210, 50)
        button_game(520, 500, 230, 50)
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