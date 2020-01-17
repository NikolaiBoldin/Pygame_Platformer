# from pygame import *
from methods import *


class Enemy(sprite.Sprite):

    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.frames_left = [load_image('Things/thing1.png'),
                            load_image('Things/thing2.png'),
                            load_image('Things/thing3.png'),
                            load_image('Things/thing4.png')]
        self.frames_right = list(map(lambda im: transform.flip(im, True, False), self.frames_left))
        self.image = self.frames_right[1]
        self.rect = Rect(location, self.image.get_size())
        self.direction = 1
        self.mask = mask.from_surface(self.image)
        self.damege = 30
        self.stun = 1
        self.HP = 50
        self.update_rate = 0.2  # скорость обновления анимации в секунадх
        self.timer_of_update = 0  # таймер обновлений
        self.frame_number_IDLE = 0  # номера кадров

    def set_frame(self, dt):
        self.timer_of_update += dt
        if self.timer_of_update >= self.update_rate:
            self.timer_of_update = 0
            if self.direction == 1:
                self.image = self.frames_right[self.frame_number_IDLE]
            else:
                self.image = self.frames_left[self.frame_number_IDLE]
            self.frame_number_IDLE = (self.frame_number_IDLE + 1) % len(self.frames_left)

    def update(self, dt, game):
        if self.HP <= 0:
            self.kill()
        self.rect.x += self.direction * 1
        for cell in game.tile_map.layers['Triggers'].collide(self.rect, 'reverse'):
            if self.direction == 1:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break
        self.set_frame(dt)
