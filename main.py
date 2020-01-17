# import pygame
# import sys
# import os
import data.maps.tmx as tmx
# from pygame import *
from player import *
from enemies import *
import pygame


class Game:
    def __init__(self):
        self.tile_map = None
        self.sprites = tmx.SpriteLayer()
        self.player = None
        self.enemies = tmx.SpriteLayer()
        self.fps = 60
        self.is_GameOver = False
        # загрузака полос: здоровья, маны и выносливости
        self.HealthBar = load_image('Health Bar/Health.png')
        self.ManaBar = load_image('Health Bar/Mana.png')
        self.StaminaBar = load_image('Health Bar/Stamina.png')
        self.BG_Bar = load_image('Health Bar/BG bar.png')
        # координаты полос
        self.size_bar = self.HealthBar.get_size()
        self.coord_BG_Bar1 = (3, 3)
        self.coord_BG_Bar2 = (3, 38)
        self.coord_BG_Bar3 = (3, 73)
        self.coord_HealthBar = (7, 7)
        self.coord_ManaBar = (7, 42)
        self.coord_StaminaBar = (7, 77)
        # смещение полос
        self.offset_health = 0
        self.offset_mana = 0
        self.offset_stamina = 0

        # главное меню
        self.fons = [transform.scale(load_image('Main menu BG/0.jpg'), (900, 600)),
                     transform.scale(load_image('Main menu BG/1.jpg'), (900, 600)),
                     transform.scale(load_image('Main menu BG/2.jpg'), (900, 600)),
                     transform.scale(load_image('Main menu BG/3.jpg'), (900, 600)),
                     transform.scale(load_image('Main menu BG/4.jpg'), (900, 600)),
                     transform.scale(load_image('Main menu BG/5.jpg'), (900, 600)), ]
        self.frame_nomber_MAIN_MENU = 1
        self.update_rate_MainMenu = 0.2  # скорость обновления анимации в секунадх
        self.timer_of_update_MainMenu = 0  # таймер обновлений
        self.direction_MainMenu = 1

        self.flag = True
        self.start_game = True

        self.flag = True
        self.start_game = True

    def main(self, screen):
        clock = time.Clock()

        mouse.set_visible(False)  # мышь не отображается
        self.tile_map = load_map('testing.tmx')

        start_cell = self.tile_map.layers['Spawn'].find('player')[0]

        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tile_map.layers.append(self.sprites)

        for enemy in self.tile_map.layers['Triggers'].find('enemy'):
            Enemy((enemy.px, enemy.py), self.enemies)
        self.tile_map.layers.append(self.enemies)

        while 1:
            dt = clock.tick(self.fps)  # задержка игрового цикла
            self.player.left_MouseButton = False

            for ev in event.get():
                if ev.type == QUIT:
                    return
                if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                    return
                if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    self.player.left_MouseButton = True

            if not self.player.is_GameOver:
                self.tile_map.update(dt / 1000, self)  # обновление всех груп спрайтов добавленных к self.tile_map
                screen.fill(Color("black"))
                self.tile_map.draw(screen)  # отрисовка всех груп спрайтов добавленных к self.tile_map
                # смещение полос
                self.offset_health = self.size_bar[0] - self.size_bar[0] * (self.player.HP / self.player.max_HP)
                self.offset_mana = self.size_bar[0] - self.size_bar[0] * (self.player.MANA / self.player.max_mana)
                self.offset_stamina = self.size_bar[0] - self.size_bar[0] * (
                        self.player.STAMINA / self.player.max_stamina)
                # отрисовка полос
                screen.blit(self.BG_Bar, self.coord_BG_Bar1)
                screen.blit(self.BG_Bar, self.coord_BG_Bar2)
                screen.blit(self.BG_Bar, self.coord_BG_Bar3)
                screen.blit(self.HealthBar, self.coord_HealthBar,
                            ((0, 0), (self.size_bar[0] - self.offset_health, self.size_bar[1])))
                screen.blit(self.ManaBar, self.coord_ManaBar,
                            ((0, 0), (self.size_bar[0] - self.offset_mana, self.size_bar[1])))
                screen.blit(self.StaminaBar, self.coord_StaminaBar,
                            ((0, 0), (self.size_bar[0] - self.offset_stamina, self.size_bar[1])))

            else:
                if not self.is_GameOver:
                    self.is_GameOver = True
                    s = pygame.Surface((800, 600), pygame.SRCALPHA)  # per-pixel alpha
                    s.fill((0, 0, 0, 128))  # notice the alpha value in the color
                    display.blit(s, (0, 0))
            # обновление экрана
            display.flip()
            display.update()

    def action1(self):
        self.flag = False

    def action2(self):
        self.start_game = False

    def button_control(self, x, y, width_b, height_b, screen):
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

    def button_game(self, x, y, width_b, height_b, screen):
        mouse = pygame.mouse.get_pos()
        click_mouse = pygame.mouse.get_pressed()

        if x < mouse[0] < x + width_b and y < mouse[1] < y + height_b:
            pygame.draw.rect(screen, (95, 158, 160), (x, y, width_b, height_b))
            if click_mouse[0] == 1:
                self.action2()
                self.main(screen)
        else:
            pygame.draw.rect(screen, (47, 79, 79), (x, y, width_b, height_b))
        font_b = pygame.font.Font('17810.ttf', 26)
        text = font_b.render(u'Перейти к игре', True, (176, 224, 230))
        screen.blit(text, (x + 10, y + 10))

    def start_screen2(self, screen):
        fon = pygame.transform.scale(load_image('fon_dark.jpg'), (900, 600))
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
                    self.terminate()
                elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    self.pause()

            self.button_control(130, 500, 210, 50, screen)
            self.button_game(520, 500, 230, 50, screen)
            if self.start_game is False:
                break
            pygame.display.flip()
            clock.tick(self.fps)

    def button(self, x, y, width_b, height_b, screen):

        mouse = pygame.mouse.get_pos()
        click_mouse = pygame.mouse.get_pressed()

        if x < mouse[0] < x + width_b and y < mouse[1] < y + height_b:
            pygame.draw.rect(screen, (95, 158, 160), (x, y, width_b, height_b))
            if click_mouse[0] == 1:
                self.action1()
                self.start_screen2(screen)

        else:
            pygame.draw.rect(screen, (47, 79, 79), (x, y, width_b, height_b))
        font_b = pygame.font.Font('data/fonts/17810.ttf', 35)
        text = font_b.render(u'Начать игру', True, (176, 224, 230))
        screen.blit(text, (x + 10, y + 10))

    def main_menu(self, screen):
        clock = time.Clock()
        screen.blit(self.fons[0], (0, 0))
        font.init()
        my_font = font.Font('data/fonts/17810.ttf', 60)
        string_rendered = my_font.render(u'Witch adventure', 1, (47, 79, 79))

        while True:
            dt = clock.tick(60) / 1000
            clock.tick(self.fps)
            self.timer_of_update_MainMenu += dt
            for ev in event.get():
                if ev.type == QUIT:
                    return
                if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                    return

            if self.timer_of_update_MainMenu >= self.update_rate_MainMenu:
                screen.fill(Color("black"))
                if self.direction_MainMenu == 1:
                    screen.blit(self.fons[self.frame_nomber_MAIN_MENU], (0, 0))
                else:
                    if self.frame_nomber_MAIN_MENU == 0:
                        self.frame_nomber_MAIN_MENU += 1
                    screen.blit(self.fons[-1 - self.frame_nomber_MAIN_MENU], (0, 0))
                self.frame_nomber_MAIN_MENU = (self.frame_nomber_MAIN_MENU + 1) % len(self.fons)
                if self.frame_nomber_MAIN_MENU == 0:
                    self.direction_MainMenu *= -1
                self.timer_of_update_MainMenu = 0

            self.button(320, 280, 240, 55, screen)
            screen.blit(string_rendered, (200, 50))
            if self.flag is False:
                break
            display.flip()
            display.update()


def load_map(name):
    fullname = os.path.join('data/maps', name)
    return tmx.load(fullname, disp.get_size())


if __name__ == '__main__':
    init()
    disp = display.set_mode((900, 600))
    Game().main_menu(disp)
