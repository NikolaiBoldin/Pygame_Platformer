# from pygame import *
from methods import *


class Enemy(sprite.Sprite):
    # image = load_image('Skeleton.png')

    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.image = load_image('Skeleton.png')
        self.rect = Rect(location, self.image.get_size())
        self.direction = 1
        self.mask = mask.from_surface(self.image)
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
