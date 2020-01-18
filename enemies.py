# from pygame import *
from methods import *


class Skeleton(sprite.Sprite):
    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.x, self.y = location
        self.frames_right = {'hit': get_list_sprites(load_image('Skelet/Skeleton Hit.png'), 0, 8, 60, 64),
                             'dead': get_list_sprites(load_image('Skelet/Skeleton Dead.png'), 0, 15, 66, 64),
                             'walk': get_list_sprites(load_image('Skelet/Skeleton Walk.png'), 0, 13, 44, 66)}
        self.frames_left = {'hit': list(map(lambda im: transform.flip(im, True, False), self.frames_right['hit'])),
                            'dead': list(map(lambda im: transform.flip(im, True, False), self.frames_right['dead'])),
                            'walk': list(map(lambda im: transform.flip(im, True, False), self.frames_right['walk']))}
        self.image = self.frames_right['walk'][0]  # текущее изображение персонажа
        self.rect = Rect(location, self.image.get_size())  # размер изображения
        self.is_hit = False
        self.is_dead = False
        self.direction = 1
        self.mask = mask.from_surface(self.image)
        self.damege = 20
        self.stun = 0.7
        self.HP = 30
        self.update_rate = 0.1  # скорость обновления анимации в секунадх
        self.timer_of_update = 0  # таймер обновлений
        self.frame_number_HIT = 0  # номера кадров
        self.frame_number_DEAD = 0
        self.frame_number_WALK = 0
        self.sound_of_death = mixer.Sound('data/sounds/dead.wav')  # звук получения урона
        self.sound_of_death.set_volume(0.1)
        self.sound_of_hit = mixer.Sound('data/sounds/рык.wav')
        self.sound_of_hit.set_volume(0.2)

    def set_frame(self, dt):
        self.timer_of_update += dt
        if self.timer_of_update >= self.update_rate:
            self.timer_of_update = 0
            if self.is_dead:
                self.rect.width = 66
                if self.direction == 1:
                    self.image = self.frames_right['dead'][self.frame_number_DEAD]
                else:
                    self.image = self.frames_left['dead'][self.frame_number_DEAD]
                if self.frame_number_DEAD == 3:
                    self.sound_of_death.play()
                self.frame_number_DEAD = (self.frame_number_DEAD + 1) % len(self.frames_right['dead'])
                if self.frame_number_DEAD == 0:
                    self.kill()
            else:
                if self.is_hit:
                    self.rect.width = 60
                    if self.direction == 1:
                        self.image = self.frames_right['hit'][self.frame_number_HIT]
                    else:
                        self.image = self.frames_left['hit'][self.frame_number_HIT]
                    if self.frame_number_HIT == 1:
                        self.sound_of_hit.play()
                    self.frame_number_HIT = (self.frame_number_HIT + 1) % len(self.frames_right['hit'])
                    if self.frame_number_HIT == 0:
                        self.is_hit = False
                else:
                    self.rect.width = 44
                    if self.direction == 1:
                        self.image = self.frames_right['walk'][self.frame_number_WALK]
                    else:
                        self.image = self.frames_left['walk'][self.frame_number_WALK]
                    self.frame_number_WALK = (self.frame_number_WALK + 1) % len(self.frames_right['walk'])

    def update(self, dt, game):
        if self.HP <= 0:
            self.is_dead = True
        if not self.is_dead and not self.is_hit:
            self.rect.x += self.direction * 1
        for cell in game.tile_map.layers['Triggers'].collide(self.rect, 'reverse'):
            if self.direction == 1:
                self.rect.right = cell.left - 1
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break
        self.set_frame(dt)


class Enemy(sprite.Sprite):

    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.frames_left = [load_image('Things/thing1.png'),
                            load_image('Things/thing2.png'),
                            load_image('Things/thing3.png'),
                            load_image('Things/thing4.png')]
        self.frames_right = list(map(lambda im: transform.flip(im, True, False), self.frames_left))
        self.frames_death = [transform.scale(load_image('Things/1.png'), (66, 90)),
                             transform.scale(load_image('Things/2.png'), (66, 90)),
                             transform.scale(load_image('Things/3.png'), (66, 90)),
                             transform.scale(load_image('Things/4.png'), (66, 90)),
                             transform.scale(load_image('Things/5.png'), (66, 90)),
                             transform.scale(load_image('Things/6.png'), (66, 90))]
        self.image = self.frames_right[1]
        self.rect = Rect(location, self.image.get_size())
        self.direction = 1
        self.mask = mask.from_surface(self.image)
        self.damege = 30
        self.stun = 1
        self.HP = 60
        self.update_rate = 0.15  # скорость обновления анимации в секунадх
        self.timer_of_update = 0  # таймер обновлений
        self.frame_number_IDLE = 0  # номера кадров
        self.frame_number_DEATH = 0  # номера кадров
        self.is_hit = False
        self.is_dead = False

    def set_frame(self, dt):
        self.timer_of_update += dt
        if self.timer_of_update >= self.update_rate:
            self.timer_of_update = 0
            if self.is_dead:

                self.image = self.frames_death[self.frame_number_DEATH]
                self.frame_number_DEATH = (self.frame_number_DEATH + 1) % len(self.frames_death)
                if self.frame_number_DEATH == 0:
                    self.kill()
            else:
                if self.direction == 1:
                    self.image = self.frames_right[self.frame_number_IDLE]
                else:
                    self.image = self.frames_left[self.frame_number_IDLE]
                self.frame_number_IDLE = (self.frame_number_IDLE + 1) % len(self.frames_left)

    def update(self, dt, game):
        if self.HP <= 0:
            self.is_dead = True
        if not self.is_dead:
            self.rect.x += self.direction * 1
            for cell in game.tile_map.layers['Triggers'].collide(self.rect, 'reverse'):
                if self.direction == 1:
                    self.rect.right = cell.left
                else:
                    self.rect.left = cell.right
                self.direction *= -1
                break
        self.set_frame(dt)


class Boss(sprite.Sprite):
    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.location = location
        self.SpriteSheet_attack = load_image('Boss/attack.png')
        self.SpriteSheet_idle = load_image('Boss/idle.png')

        self.frames = {'idle': get_list_sprites(self.SpriteSheet_idle, 0, 6, 640, 576),
                       'attack': get_list_sprites(self.SpriteSheet_attack, 0, 8, 960, 768)}
        self.image = self.frames['idle'][0]
        self.rect = Rect(location, self.image.get_size())
        self.HP = 500
        self.is_attack = True

        self.update_rate = 0.1  # скорость обновления анимации в секунадх
        self.timer_of_update = 0  # таймер обновлений
        self.frame_number_IDLE = 0  # номера кадров
        self.frame_number_Attack = 0  # номера кадров

    def set_frame(self, dt):
        self.timer_of_update += dt
        if self.timer_of_update >= self.update_rate:
            self.timer_of_update = 0
            if self.is_attack:
                self.image = self.frames['attack'][self.frame_number_Attack]
                self.frame_number_Attack = (self.frame_number_Attack + 1) % len(self.frames['attack'])
                self.rect = Rect(self.location, self.image.get_size())
                if self.frame_number_Attack == 0:
                    self.is_attack = False
            else:
                self.image = self.frames['idle'][self.frame_number_IDLE]
                self.frame_number_IDLE = (self.frame_number_IDLE + 1) % len(self.frames['idle'])
                self.rect = Rect(self.location, self.image.get_size())
                if self.frame_number_IDLE == 0:
                    self.is_attack = True

    def update(self, dt, game):
        if self.HP <= 0:
            self.kill()

        self.set_frame(dt)
