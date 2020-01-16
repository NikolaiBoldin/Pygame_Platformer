import pygame
import sys
import os
import data.maps.tmx as tmx
from pygame import *


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


def get_list_sprites(sheet, line, count_frames, x, y):
    list_frames = []
    for i in range(count_frames):
        list_frames.append(sheet.subsurface(pygame.Rect(
            (x * i, y * line), (x, y))))
    return list_frames


class Enemy(pygame.sprite.Sprite):
    image = pygame.image.load(os.path.join('data/sprites/', 'Skeleton.png'))

    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.image = Enemy.image
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.direction = 1
        self.mask = pygame.mask.from_surface(self.image)
        self.damege = 30
        self.stun = 1

    def update(self, dt, game):
        self.rect.x += self.direction * 2
        for cell in game.tile_map.layers['Triggers'].collide(self.rect, 'reverse'):
            if self.direction == 1:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break


pygame.init()
pygame.mixer.music.load('data/soundtracks/m_bg1.mp3')  # фоновая музыка
pygame.mixer_music.set_volume(0.2)
pygame.mixer.music.play(-1)

jumpsound = pygame.mixer.Sound('data/soundtracks/gruntJumpFemale.wav')  # звук прыжка
runsound = pygame.mixer.Sound('data/soundtracks/footstepsTurn.wav')  # звук бега
enemypunch = pygame.mixer.Sound('data/soundtracks/wooosh.wav')  # звук удара врага
takedamage = pygame.mixer.Sound('data/soundtracks/splatFemale.wav')  # звук получения урона
jumpsound.set_volume(0.1)
runsound.set_volume(0.1)
takedamage.set_volume(0.3)


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
        # анимация
        self.SpriteSheet = load_image('sprites/Witch/Witch Sprite Sheet.png')
        self.frames_right = {'idle': get_list_sprites(self.SpriteSheet, 0, 4, 64, 64),
                             'move': get_list_sprites(self.SpriteSheet, 1, 8, 64, 64),
                             'spell': get_list_sprites(self.SpriteSheet, 2, 8, 64, 64),
                             'damage': get_list_sprites(self.SpriteSheet, 3, 4, 64, 64),
                             'death': get_list_sprites(self.SpriteSheet, 4, 10, 64, 64),
                             'flight': get_list_sprites(self.SpriteSheet, 5, 4, 64, 64)}
        self.frames_left = {'idle': list(map(lambda im: transform.flip(im, True, False), self.frames_right['idle'])),
                            'move': list(map(lambda im: transform.flip(im, True, False), self.frames_right['move'])),
                            'spell': list(map(lambda im: transform.flip(im, True, False), self.frames_right['spell'])),
                            'damage': list(
                                map(lambda im: transform.flip(im, True, False), self.frames_right['damage'])),
                            'death': list(map(lambda im: transform.flip(im, True, False), self.frames_right['death'])),
                            'flight': list(
                                map(lambda im: transform.flip(im, True, False), self.frames_right['flight']))}
        self.image = self.frames_right['idle'][0]
        self.update_rate = 0.1  # скорость обновления анимации в секунадх
        self.timer_of_update = 0  # таймер обновлений
        self.frame_number_IDLE = 0
        self.frame_number_MOVE = 0
        self.frame_number_SPELL = 0
        self.frame_number_DAMAGE = 0
        self.frame_number_DEATH = 0
        self.frame_number_FLIGHT = 0
        self.is_move = False
        self.is_jump = False
        self.is_stun = False
        self.is_SpellCast = False
        self.is_GameOver = False
        self.timer_of_immunity = 0
        self.damage_cooldown = 2
        self.timer_of_stun = 0
        self.spell_cooldown = 1
        self.timer_of_spell = 0
        self.left_MouseButton = False

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
        self.mana = 50
        self.max_mana = 100
        self.stamina = 30
        self.max_stamina = 100
        # физика
        self.jumpforce = 0  # сила прыжка
        self.gravityforce = 0  # сила гравитации
        self.maxgravityforce = 50  # сила максимальная сила гравитации

        self.mask = pygame.mask.from_surface(self.image)

    def set_frame(self, dt):
        self.timer_of_update += dt
        if self.is_dead:
            if self.timer_of_update >= self.update_rate:
                if self.direction == 1:
                    self.image = self.frames_right['death'][self.frame_number_DEATH]
                    self.frame_number_DEATH = (self.frame_number_DEATH + 1) % len(self.frames_right['death'])
                    if self.frame_number_DEATH == 9:
                        self.is_GameOver = True
                    self.timer_of_update = 0
                else:
                    self.image = self.frames_left['death'][self.frame_number_DEATH]
                    self.frame_number_DEATH = (self.frame_number_DEATH + 1) % len(self.frames_left['death'])
                    if self.frame_number_DEATH == 7:
                        self.is_GameOver = True
                    self.timer_of_update = 0
        else:
            if self.is_SpellCast:
                if self.timer_of_update >= self.update_rate:
                    if self.direction == 1:
                        self.image = self.frames_right['spell'][self.frame_number_SPELL]
                        self.frame_number_SPELL = (self.frame_number_SPELL + 1) % len(self.frames_right['spell'])
                        self.timer_of_update = 0
                    else:
                        self.image = self.frames_left['spell'][self.frame_number_SPELL]
                        self.frame_number_SPELL = (self.frame_number_SPELL + 1) % len(self.frames_left['spell'])
                        self.timer_of_update = 0
                    if self.frame_number_SPELL == 0:
                        self.is_SpellCast = False
            else:
                if self.is_stun:
                    if self.timer_of_update >= self.update_rate:
                        if self.direction == 1:
                            self.image = self.frames_right['damage'][2]
                            self.timer_of_update = 0
                        else:
                            self.image = self.frames_left['damage'][2]
                            self.timer_of_update = 0
                else:
                    if not self.is_jump:
                        if self.is_move:
                            if self.timer_of_update >= self.update_rate:
                                if self.direction == 1:
                                    self.image = self.frames_right['move'][self.frame_number_MOVE]
                                    self.frame_number_MOVE = (self.frame_number_MOVE + 1) % len(
                                        self.frames_right['move'])
                                    self.timer_of_update = 0
                                else:
                                    self.image = self.frames_left['move'][self.frame_number_MOVE]
                                    self.frame_number_MOVE = (self.frame_number_MOVE + 1) % len(
                                        self.frames_left['move'])
                                    self.timer_of_update = 0
                        else:
                            if self.timer_of_update >= self.update_rate:
                                if self.direction == 1:
                                    self.image = self.frames_right['idle'][self.frame_number_IDLE]
                                    self.frame_number_IDLE = (self.frame_number_IDLE + 1) % len(
                                        self.frames_right['idle'])
                                    self.timer_of_update = 0
                                else:
                                    self.image = self.frames_left['idle'][self.frame_number_IDLE]
                                    self.frame_number_IDLE = (self.frame_number_IDLE + 1) % len(
                                        self.frames_left['idle'])
                                    self.timer_of_update = 0
                    else:
                        if self.timer_of_update >= self.update_rate:
                            if self.direction == 1:
                                self.image = self.frames_right['move'][6]
                                self.timer_of_update = 0
                            else:
                                self.image = self.frames_left['move'][2]
                                self.timer_of_update = 0

    def death(self):
        pass

    def gravity(self):
        # Событие начала прыжка игрока
        self.jumpforce = 15
        self.gravityforce = 0

    def update(self, dt, game):
        last_masc = self.mask_for_platform.copy()

        keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT]:
        #     self.rect.x -= 7
        #     self.mask_for_platform.x -= 7
        #     self.image = self.left_image
        #     self.direction = -1
        # if keys[pygame.K_RIGHT]:
        #     self.rect.x += 7
        #     self.mask_for_platform.x += 7
        #     self.image = self.right_image
        #     self.direction = 1

        # if keys[pygame.K_LSHIFT] and not self.gun_cooldown:
        #     if self.direction > 0:
        #         Bullet(self.rect.midright, 1, game.sprites)
        #     else:
        #         Bullet(self.rect.midleft, -1, game.sprites)
        #     self.gun_cooldown = 1

        self.gun_cooldown = max(0, self.gun_cooldown - dt)

        # if self.on_the_ground:
        #     if keys[pygame.K_SPACE]:  # прыжок
        # if not self.is_dead or self.is_stun:
        #     last_masc = self.mask_for_platform.copy()

        keys = pygame.key.get_pressed()

        if keys[K_a] and not keys[K_d] and not self.is_stun and not self.is_SpellCast:
            self.rect.x -= 7
            self.mask_for_platform.x -= 7
            runsound.play()
            if not self.is_move:
                self.is_move = True
                self.timer_of_update = 0
                self.frame_number_MOVE = 2
                self.image = self.frames_left['move'][1]
            self.direction = -1
        if keys[K_d] and not keys[K_a] and not self.is_stun and not self.is_SpellCast:
            self.rect.x += 7
            self.mask_for_platform.x += 7
            runsound.play()
            if not self.is_move:
                self.is_move = True
                self.timer_of_update = 0
                self.frame_number_MOVE = 2
                self.image = self.frames_right['move'][1]
            self.direction = 1
        if (not keys[K_a] and not keys[K_d]) or (keys[K_a] and keys[K_d]):
            self.is_move = False

        # if keys[pygame.K_LSHIFT] and not self.gun_cooldown:
        #     if self.direction > 0:
        #         Bullet(self.rect.midright, 1, game.sprites)
        #     else:
        #         Bullet(self.rect.midleft, -1, game.sprites)
        #     self.gun_cooldown = 1

        # self.gun_cooldown = max(0, self.gun_cooldown - dt)

        # прыжок
        if self.on_the_ground and keys[pygame.K_SPACE] and not self.is_stun and not self.is_SpellCast:
            self.gravity()
            self.on_the_ground = False
            self.is_jump = True
            runsound.stop()
            jumpsound.play()
            if self.direction == 1:  # анимация начла прыжка
                self.image = self.frames_right['move'][5]
                self.timer_of_update = 0
            else:
                self.image = self.frames_right['move'][1]
                self.timer_of_update = 0
        # падение героя если находится в воздухе
        if not self.on_the_ground:
            if self.gravityforce >= self.maxgravityforce:
                self.gravityforce = self.maxgravityforce
            else:
                self.gravityforce += 1
            self.rect.y -= self.jumpforce
            self.rect.y += self.gravityforce
            self.mask_for_platform.y -= self.jumpforce
            self.mask_for_platform.y += self.gravityforce

        if self.timer_of_spell > 0:
            self.timer_of_spell -= dt
        else:
            if self.left_MouseButton and self.on_the_ground and not self.is_stun:
                self.is_SpellCast = True
                self.timer_of_spell = self.spell_cooldown
                self.frame_number_SPELL = 2
                self.timer_of_update = 0
                if self.direction == 1:
                    self.image = self.frames_right['spell'][1]
                else:
                    self.image = self.frames_right['spell'][1]

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
                if self.is_jump:  # анимация приземления
                    if self.direction == 1:
                        self.image = self.frames_right['move'][7]
                        self.timer_of_update = 0.03
                    else:
                        self.image = self.frames_left['move'][3]
                        self.timer_of_update = 0.03
                self.is_jump = False
                new.bottom = cell.top
                new_masc.bottom = cell.top
            if 'b' in blockers and last_masc.top >= cell.bottom > new_masc.top:
                self.gravityforce = self.jumpforce
                new.top = cell.bottom - 15
                new_masc.top = cell.bottom

        if self.is_stun and self.timer_of_stun > 0:
            self.timer_of_stun -= dt
            if self.is_dead and self.on_the_ground:
                self.timer_of_stun = 0
                if self.direction == 1:
                    self.image = self.frames_right['damage'][3]
                    self.timer_of_update = 0
                else:
                    self.image = self.frames_left['damage'][3]
                    self.timer_of_update = 0
                self.is_stun = False
        else:
            if self.is_stun:
                if self.direction == 1:
                    self.image = self.frames_right['damage'][3]
                    self.timer_of_update = 0
                else:
                    self.image = self.frames_left['damage'][3]
                    self.timer_of_update = 0
            self.is_stun = False

        if self.timer_of_immunity > 0:
            self.timer_of_immunity -= dt

        for enemy in sprite.spritecollide(self, game.enemies, False):
            if pygame.sprite.collide_mask(self, enemy) and self.timer_of_immunity <= 0 and not self.is_dead:
                takedamage.play()
                self.timer_of_stun = enemy.stun
                self.timer_of_immunity = self.damage_cooldown
                self.is_stun = True
                self.is_SpellCast = False
                self.HP -= enemy.damege
                enemypunch.play()
                if self.HP <= 0:
                    self.HP = 0
                    self.is_dead = True
                    if not self.on_the_ground:
                        self.timer_of_stun += 100
                if self.direction == 1:
                    self.image = self.frames_right['damage'][1]
                    self.timer_of_update = 0
                else:
                    self.image = self.frames_left['damage'][1]
                    self.timer_of_update = 0
        game.tile_map.set_focus(new.x, new.y)  # камера

        self.set_frame(dt)


class Game:
    def __init__(self):
        self.tile_map = None
        self.sprites = tmx.SpriteLayer()
        self.player = None
        self.enemies = tmx.SpriteLayer()
        self.fps = 60
        self.is_GameOver = False
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

        self.flag = True
        self.start_game = True

    def main(self, screen):
        clock = pygame.time.Clock()
        mouse.set_visible(False)
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
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.left_MouseButton = True
            if not self.player.is_GameOver:
                self.tile_map.update(dt / 1000, self)  # обновление всех груп спрайтов добавленных к self.tile_map
                screen.fill(Color("black"))
                self.tile_map.draw(screen)  # отрисовка всех груп спрайтов добавленных к self.tile_map
                # смещение полос
                self.offset_health = self.size_bar[0] - self.size_bar[0] * (self.player.HP / self.player.max_HP)
                self.offset_mana = self.size_bar[0] - self.size_bar[0] * (self.player.mana / self.player.max_mana)
                self.offset_stamina = self.size_bar[0] - self.size_bar[0] * (
                        self.player.stamina / self.player.max_stamina)
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
