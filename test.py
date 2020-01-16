import pygame
import sys
import os
import data.maps.tmx as tmx
from pygame import *


class Enemy(pygame.sprite.Sprite):
    image = pygame.image.load(os.path.join('data/sprites/', 'Skeleton.png'))

    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.image = Enemy.image
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.direction = 1
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt, game):
        self.rect.x += self.direction * 2
        for cell in game.tile_map.layers['Triggers'].collide(self.rect, 'reverse'):
            if self.direction == 1:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break


# class Bullet(pygame.sprite.Sprite):
#     image = pygame.image.load('bullet.png')
#
#     def __init__(self, location, direction, *groups):
#         super(Bullet, self).__init__(*groups)
#         self.rect = pygame.rect.Rect(location, self.image.get_size())
#         self.direction = direction
#         self.lifespan = 1
#
#     def update(self, dt, game):
#         self.lifespan -= dt
#         if self.lifespan < 0:
#             self.kill()
#             return
#         self.rect.x += self.direction * 400 * dt
#
#         if pygame.sprite.spritecollide(self, game.enemies, True):
#             self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, location, *groups):
        super().__init__(*groups)
        # self.image = pygame.image.load(os.path.join('data/sprites/Witch', 'Witch2.png'))
        self.image = (pygame.image.load(os.path.join('data/sprites/Witch', 'Witch.png')))
        self.right_image = self.image
        self.left_image = pygame.transform.flip(self.image, True, False)
        X, Y = location
        x, y = self.image.get_size()
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.mask_for_platform = pygame.rect.Rect((X + 23, Y + 15), (x - 46, y - 15))  # маска для корректного падения
        self.on_the_ground = False  # находится ли персонаж на земле
        self.is_dead = False
        self.direction = 1  # направление персонажа: 1 -> право, -1 -> лево
        self.gun_cooldown = 0
        # характеристики
        self.HP = 100
        self.max_HP = 100
        self.mana = 100
        self.max_mana = 100
        self.stamina = 100
        self.max_stamina = 100
        # физика
        self.jumpforce = 0  # сила прыжка
        self.gravityforce = 0  # сила гравитации
        self.maxgravityforce = 50  # сила максимальная сила гравитации

        self.mask = pygame.mask.from_surface(self.image)

    def gravity(self):
        # Событие начала прыжка игрока
        self.jumpforce = 15
        self.gravityforce = 0

    def update(self, dt, game):

        last_masc = self.mask_for_platform.copy()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 7
            self.mask_for_platform.x -= 7
            self.image = self.left_image
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.rect.x += 7
            self.mask_for_platform.x += 7
            self.image = self.right_image
            self.direction = 1

        # if keys[pygame.K_LSHIFT] and not self.gun_cooldown:
        #     if self.direction > 0:
        #         Bullet(self.rect.midright, 1, game.sprites)
        #     else:
        #         Bullet(self.rect.midleft, -1, game.sprites)
        #     self.gun_cooldown = 1

        self.gun_cooldown = max(0, self.gun_cooldown - dt)

        if self.on_the_ground:
            if keys[pygame.K_SPACE]:  # прыжок
                self.gravity()
                self.on_the_ground = False
        if not self.on_the_ground:
            if self.gravityforce >= self.maxgravityforce:
                self.gravityforce = self.maxgravityforce
            else:
                self.gravityforce += 1
            self.rect.y -= self.jumpforce
            self.rect.y += self.gravityforce
            self.mask_for_platform.y -= self.jumpforce
            self.mask_for_platform.y += self.gravityforce

        new = self.rect
        new_masc = self.mask_for_platform
        self.on_the_ground = False
        for cell in game.tile_map.layers['Blocking'].collide(new_masc, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last_masc.right <= cell.left < new_masc.right:
                new.right = cell.left + 23
                new_masc.right = cell.left
            if 'r' in blockers and last_masc.left >= cell.right > new_masc.left:
                new.left = cell.right - 23
                new_masc.left = cell.right
            if 't' in blockers and last_masc.bottom <= cell.top < new_masc.bottom:
                self.jumpforce = 0
                self.gravityforce = 0
                self.on_the_ground = True
                new.bottom = cell.top
                new_masc.bottom = cell.top
            if 'b' in blockers and last_masc.top >= cell.bottom > new_masc.top:
                self.gravityforce = self.jumpforce
                new.top = cell.bottom - 15
                new_masc.top = cell.bottom

        for enemy in sprite.spritecollide(self, game.enemies, False):
            if pygame.sprite.collide_mask(self, enemy):
                if self.HP > 0:
                    self.HP -= 0.5

        game.tile_map.set_focus(new.x, new.y)  # камера


class Game:
    def __init__(self):
        self.tile_map = None
        self.sprites = tmx.SpriteLayer()
        self.player = None
        self.enemies = tmx.SpriteLayer()
        self.fps = 60
        # загрузака полос: здоровья, маны и выносливости
        self.HealthBar = load_image('sprites/Health Bar/Health.png')
        self.ManaBar = load_image('sprites/Health Bar/Mana.png')
        self.StaminaBar = load_image('sprites/Health Bar/Stamina.png')
        self.BG_Bar = load_image('sprites/Health Bar/BG bar.png')
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
        self.flag = True
        self.start_game = True

    def main(self, screen):
        clock = pygame.time.Clock()

        self.tile_map = load_map('testing.tmx')

        start_cell = self.tile_map.layers['Spawn'].find('player')[0]

        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tile_map.layers.append(self.sprites)

        for enemy in self.tile_map.layers['Triggers'].find('enemy'):
            Enemy((enemy.px, enemy.py), self.enemies)
        self.tile_map.layers.append(self.enemies)

        while 1:
            dt = clock.tick(self.fps)  # задержка игрового цикла

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            self.tile_map.update(dt / 1000, self)  # обновление всех груп спрайтов добавленных к self.tile_map
            screen.fill(Color("black"))
            self.tile_map.draw(screen)  # отрисовка всех груп спрайтов добавленных к self.tile_map
            # смещение полос
            self.offset_health = self.size_bar[0] - self.size_bar[0] * (self.player.HP / self.player.max_HP)
            self.offset_mana = self.size_bar[0] - self.size_bar[0] * (self.player.mana / self.player.max_mana)
            self.offset_stamina = self.size_bar[0] - self.size_bar[0] * (self.player.stamina / self.player.max_stamina)
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
            # обновление экрана
            pygame.display.flip()
            pygame.display.update()

            # if self.player.is_dead:
            #     print('YOU DIED')
            #     return

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
            clock.tick(FPS)

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
        font_b = pygame.font.Font('17810.ttf', 35)
        text = font_b.render(u'Начать игру', True, (176, 224, 230))
        screen.blit(text, (x + 10, y + 10))

    def start_screen1(self, screen):
        fon = pygame.transform.scale(load_image('fon.jpg'), (900, 600))
        screen.blit(fon, (0, 0))
        pygame.font.init()
        myfont = pygame.font.Font('17810.ttf', 60)
        string_rendered = myfont.render(u'Witch adventure', 1, (47, 79, 79))
        screen.blit(string_rendered, (200, 50))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    self.pause()
            self.button(320, 280, 240, 55, screen)
            if self.flag is False:
                break
            pygame.display.flip()
            clock.tick(FPS)


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
    return image


def load_map(name):
    fullname = os.path.join('data/maps', name)
    return tmx.load(fullname, screen.get_size())


if __name__ == '__main__':
    pygame.init()
    screen_size = WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode(screen_size)
    FPS = 50
    clock = pygame.time.Clock()
    Game().start_screen1(screen)

