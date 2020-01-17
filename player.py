# from pygame import *
from methods import *


class Player(sprite.Sprite):
    def __init__(self, location, *groups):
        super().__init__(*groups)  # добавление к группе спрайтов
        # анимация
        self.SpriteSheet = load_image('Witch/Witch Sprite Sheet.png')
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
        self.image = self.frames_right['idle'][0]  # текущее изображение персонажа
        self.rect = Rect(location, self.image.get_size())  # размер изображения
        self.update_rate = 0.1  # скорость обновления анимации в секунадх
        self.timer_of_update = 0  # таймер обновлений
        self.frame_number_IDLE = 0  # номера кадров
        self.frame_number_MOVE = 0
        self.frame_number_SPELL = 0
        self.frame_number_DAMAGE = 0
        self.frame_number_DEATH = 0
        self.frame_number_FLIGHT = 0
        self.is_move = False  # движется?
        self.is_jump = False  # в прыжке?
        self.is_stun = False  # оглущён?
        self.is_SpellCast = False  # кастует способность?
        self.is_GameOver = False  # игра закончена?
        self.is_dead = False  # персонаж умер?
        self.is_fly = False  # активен полёт?
        self.on_the_ground = False  # персонаж стоит на платформе?
        self.direction = 1  # направление персонажа: 1 -> право, -1 -> лево
        # длительность эффектов
        self.duration_of_immunity = 2  # иммунитет
        # перезарядка способностей
        self.spell_cooldown = 1  # заклинание (ЛКМ)
        # таймеры способностей
        self.timer_of_immunity = 0  # иммунитет
        self.timer_of_stun = 0  # оглушение
        self.timer_of_spell = 0  # заклинание (ЛКМ)
        # маски персонажа для работы с пересечениями (враги и платформы)
        self.mask = mask.from_surface(self.image)  # маска для корректного пересечения с врагами
        lx, ly = location  # координаты персонажа
        ix, iy = self.image.get_size()  # размеры персонажа
        self.mask_for_platform = Rect((lx + 23, ly + 15),
                                      (ix - 46, iy - 15))  # маска для корректного пересечения с платформами
        # характеристики
        self.HP = 100  # здоровье
        self.max_HP = 100  # максимальное здоровье
        self.MANA = 50  # мана
        self.max_mana = 100  # максимальная мана
        self.STAMINA = 30  # выносливость
        self.max_stamina = 100  # максимальная выносливость
        # физика
        self.jump_force = 0  # сила прыжка
        self.gravity_force = 0  # сила гравитации
        self.max_gravity_force = 50  # сила максимальная сила гравитации
        # звуки
        self.jump_sound = mixer.Sound('data/sounds/gruntJumpFemale.wav')  # звук прыжка
        self.run_sound = mixer.Sound('data/sounds/footstepsTurn.wav')  # звук бега
        self.enemy_punch = mixer.Sound('data/sounds/wooosh.wav')  # звук удара врага
        self.take_damage = mixer.Sound('data/sounds/splatFemale.wav')  # звук получения урона
        self.jump_sound.set_volume(0.1)
        self.run_sound.set_volume(0.1)
        self.take_damage.set_volume(0.3)

        self.left_MouseButton = False  # нажата ли ЛКМ?

    # обновление анимации
    def set_frame(self, dt):
        self.timer_of_update += dt  # обновление таймера
        if self.is_dead:
            # анимация смерти
            if self.timer_of_update >= self.update_rate:
                if self.direction == 1:
                    self.image = self.frames_right['death'][self.frame_number_DEATH]
                else:
                    self.image = self.frames_left['death'][self.frame_number_DEATH]
                self.frame_number_DEATH = (self.frame_number_DEATH + 1) % len(self.frames_right['death'])
                self.timer_of_update = 0
                if self.frame_number_DEATH == 0:
                    self.is_GameOver = True
        else:
            if self.is_fly:
                # анимация полёта
                if self.timer_of_update >= self.update_rate:
                    self.timer_of_update = 0
                    if self.direction == 1:
                        self.image = self.frames_right['flight'][self.frame_number_FLIGHT]
                    else:
                        self.image = self.frames_left['flight'][self.frame_number_FLIGHT]
                    self.frame_number_FLIGHT = (self.frame_number_FLIGHT + 1) % len(self.frames_left['flight'])
            else:
                if self.is_SpellCast:
                    # анимация каста способности
                    if self.timer_of_update >= self.update_rate:
                        self.timer_of_update = 0
                        if self.direction == 1:
                            self.image = self.frames_right['spell'][self.frame_number_SPELL]
                        else:
                            self.image = self.frames_left['spell'][self.frame_number_SPELL]
                        self.frame_number_SPELL = (self.frame_number_SPELL + 1) % len(self.frames_left['spell'])
                        if self.frame_number_SPELL == 0:
                            self.is_SpellCast = False
                else:
                    if self.is_stun:
                        # анимация оглушения
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
                                # анимация ходьбы
                                if self.timer_of_update >= self.update_rate:
                                    if self.direction == 1:
                                        self.image = self.frames_right['move'][self.frame_number_MOVE]
                                    else:
                                        self.image = self.frames_left['move'][self.frame_number_MOVE]
                                    self.frame_number_MOVE = (self.frame_number_MOVE + 1) % len(self.frames_left['move'])
                                    self.timer_of_update = 0
                            else:
                                # анимация покоя
                                if self.timer_of_update >= self.update_rate:
                                    if self.direction == 1:
                                        self.image = self.frames_right['idle'][self.frame_number_IDLE]
                                    else:
                                        self.image = self.frames_left['idle'][self.frame_number_IDLE]
                                    self.frame_number_IDLE = (self.frame_number_IDLE + 1) % len(self.frames_left['idle'])
                                    self.timer_of_update = 0
                        else:
                            # анимация полета после прыжка
                            if self.timer_of_update >= self.update_rate:
                                if self.direction == 1:
                                    self.image = self.frames_right['move'][6]
                                else:
                                    self.image = self.frames_left['move'][2]
                                self.timer_of_update = 0

    # изменение гравитации для прыжка
    def gravity(self):
        self.jump_force = 15
        self.gravity_force = 0

    def update(self, dt, game):
        if not self.is_dead or self.is_stun:
            last_masc = self.mask_for_platform.copy()
            # движение влево
            keys = key.get_pressed()
            if keys[K_a] and not keys[K_d] and not self.is_stun and not self.is_SpellCast:
                self.rect.x -= 7
                self.mask_for_platform.x -= 7
                self.run_sound.play()
                if not self.is_move:  # начало анимации движения
                    self.is_move = True
                    self.timer_of_update = 0
                    self.frame_number_MOVE = 2
                    self.image = self.frames_left['move'][1]
                self.direction = -1

            # движение вправо
            if keys[K_d] and not keys[K_a] and not self.is_stun and not self.is_SpellCast:
                self.rect.x += 7
                self.mask_for_platform.x += 7
                self.run_sound.play()
                if not self.is_move:  # начало анимации движения
                    self.is_move = True
                    self.timer_of_update = 0
                    self.frame_number_MOVE = 2
                    self.image = self.frames_right['move'][1]
                self.direction = 1

            # покой
            if (not keys[K_a] and not keys[K_d]) or (keys[K_a] and keys[K_d]):
                self.is_move = False

            # начало прыжка
            if self.on_the_ground and keys[K_SPACE] and not self.is_stun and not self.is_SpellCast:
                self.gravity()
                self.on_the_ground = False
                self.is_jump = True
                self.run_sound.stop()
                self.jump_sound.play()
                if self.direction == 1:  # анимация начала прыжка
                    self.image = self.frames_right['move'][5]
                    self.timer_of_update = 0
                else:
                    self.image = self.frames_right['move'][1]
                    self.timer_of_update = 0
            print(keys[K_SPACE])
            # падение героя если находится в воздухе
            if not self.on_the_ground:
                if self.is_jump and keys[K_SPACE] and (self.STAMINA > 25 or self.is_fly):  # полёт
                    self.is_fly = True
                else:
                    if self.gravity_force >= self.max_gravity_force:
                        self.gravity_force = self.max_gravity_force
                    else:
                        self.gravity_force += 1  # усиление силы гравитации для ускорения при падении
                    self.rect.y -= self.jump_force
                    self.rect.y += self.gravity_force
                    self.mask_for_platform.y -= self.jump_force
                    self.mask_for_platform.y += self.gravity_force

            # способность (ЛКМ)
            if self.timer_of_spell > 0:  # перезарядка способности
                self.timer_of_spell -= dt
            else:
                if self.left_MouseButton and self.on_the_ground and not self.is_stun:  # начало каста способности
                    self.is_SpellCast = True
                    self.timer_of_spell = self.spell_cooldown
                    self.frame_number_SPELL = 2
                    self.timer_of_update = 0
                    if self.direction == 1:  # начало анимации способности
                        self.image = self.frames_right['spell'][1]
                    else:
                        self.image = self.frames_right['spell'][1]

            # определение столкновений героя с платформами
            new = self.rect
            new_masc = self.mask_for_platform
            self.on_the_ground = False
            for cell in game.tile_map.layers['Blocking'].collide(new_masc, 'blockers'):
                blockers = cell['blockers']
                # print(blockers)
                if 'l' in blockers and last_masc.right <= cell.left < new_masc.right:  # left
                    new.right = cell.left + 23
                    new_masc.right = cell.left
                if 'r' in blockers and last_masc.left >= cell.right > new_masc.left:  # right
                    new.left = cell.right - 23
                    new_masc.left = cell.right
                if 't' in blockers and last_masc.bottom <= cell.top < new_masc.bottom:  # top
                    self.jump_force = 0
                    self.gravity_force = 0
                    self.on_the_ground = True
                    self.is_fly = False
                    if self.is_jump:  # анимация приземления после прыжка
                        if self.direction == 1:
                            self.image = self.frames_right['move'][7]
                            self.timer_of_update = 0.03
                        else:
                            self.image = self.frames_left['move'][3]
                            self.timer_of_update = 0.03
                    self.is_jump = False
                    new.bottom = cell.top
                    new_masc.bottom = cell.top
                if 'b' in blockers and last_masc.top >= cell.bottom > new_masc.top:  # bottom
                    self.gravity_force = self.jump_force
                    new.top = cell.bottom - 15
                    new_masc.top = cell.bottom  # что бы не прилипал

            # оглушение
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

            # обновление времени иммунитета
            if self.timer_of_immunity > 0:
                self.timer_of_immunity -= dt

            # пересечение с врагами по макам
            for enemy in sprite.spritecollide(self, game.enemies, False):
                if sprite.collide_mask(self, enemy) and self.timer_of_immunity <= 0 and not self.is_dead:
                    self.take_damage.play()
                    self.timer_of_stun = enemy.stun
                    self.timer_of_immunity = self.duration_of_immunity
                    self.is_stun = True
                    self.is_SpellCast = False
                    self.HP -= enemy.damege
                    self.enemy_punch.play()
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


class FireBall(sprite.Sprite):
    def __init__(self, location, direction, *groups):
        super().__init__(*groups)  # добавление к группе спрайтов

        self.SpriteSheet = load_image('Witch/Witch Sprite Sheet.png')
        self.frames_right = get_list_sprites(self.SpriteSheet, 0, 45, 64, 64)
        self.frames_left = list(map(lambda im: transform.flip(im, True, False), self.frames_right))

