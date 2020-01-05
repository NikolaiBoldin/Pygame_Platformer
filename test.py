import pygame
import sys
import os
import data.maps.tmx as tmx


# class Enemy(pygame.sprite.Sprite):
#     image = pygame.image.load('enemy.png')
#
#     def __init__(self, location, *groups):
#         super(Enemy, self).__init__(*groups)
#         self.rect = pygame.rect.Rect(location, self.image.get_size())
#         self.direction = 1
#
#     def update(self, dt, game):
#         self.rect.x += self.direction * 100 * dt
#         for cell in game.tile_map.layers['triggers'].collide(self.rect, 'reverse'):
#             if self.direction > 0:
#                 self.rect.right = cell.left
#             else:
#                 self.rect.left = cell.right
#             self.direction *= -1
#             break
#         if self.rect.colliderect(game.player.rect):
#             game.player.is_dead = True


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
        super(Player, self).__init__(*groups)
        # self.image = pygame.image.load(os.path.join('data/sprites/Witch', 'Witch2.png'))
        self.image = pygame.transform.scale(pygame.image.load(os.path.join('data/sprites/Witch', 'Witch.png')),
                                            (64, 64))
        self.right_image = self.image
        self.left_image = pygame.transform.flip(self.image, True, False)
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.resting = False
        self.dy = 0
        self.is_dead = False
        self.direction = 1
        self.gun_cooldown = 0
        print(1)

    def update(self, dt, game):
        last = self.rect.copy()

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.rect.x -= 300 * dt
            self.image = self.left_image
            self.direction = -1
        if key[pygame.K_RIGHT]:
            self.rect.x += 300 * dt
            self.image = self.right_image
            self.direction = 1

        # if key[pygame.K_LSHIFT] and not self.gun_cooldown:
        #     if self.direction > 0:
        #         Bullet(self.rect.midright, 1, game.sprites)
        #     else:
        #         Bullet(self.rect.midleft, -1, game.sprites)
        #     self.gun_cooldown = 1

        self.gun_cooldown = max(0, self.gun_cooldown - dt)

        if self.resting and key[pygame.K_SPACE]:
            self.dy = -500
        self.dy = min(400, self.dy + 40)

        self.rect.y += self.dy * dt

        new = self.rect
        self.resting = False
        for cell in game.tile_map.layers['Blocking'].collide(new, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last.right <= cell.left < new.right:
                new.right = cell.left
            if 'r' in blockers and last.left >= cell.right > new.left:
                new.left = cell.right
            if 't' in blockers and last.bottom <= cell.top < new.bottom:
                self.resting = True
                new.bottom = cell.top
                self.dy = 0
            if 'b' in blockers and last.top >= cell.bottom > new.top:
                new.top = cell.bottom
                self.dy = 0

        game.tile_map.set_focus(new.x, new.y)


class Game:
    def __init__(self):
        self.tile_map = None
        self.sprites = tmx.SpriteLayer()
        self.player = None
        self.enemies = tmx.SpriteLayer()

    def main(self, screen):
        clock = pygame.time.Clock()

        # background = pygame.image.load('background.png')

        self.tile_map = load_map('testing.tmx')

        start_cell = self.tile_map.layers['Spawn'].find('player')[0]
        # print((start_cell.px, start_cell.py))
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tile_map.layers.append(self.sprites)

        # for enemy in self.tile_map.layers['triggers'].find('enemy'):
        #     Enemy((enemy.px, enemy.py), self.enemies)
        # self.tile_map.layers.append(self.enemies)

        while 1:
            dt = clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            self.tile_map.update(dt / 1000., self)
            # screen.blit(background, (0, 0))
            screen.fill(pygame.Color("black"))
            self.tile_map.draw(screen)

            pygame.display.flip()

            # if self.player.is_dead:
            #     print('YOU DIED')
            #     return


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
    return tmx.load(fullname, display.get_size())


if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((800, 600))
    Game().main(display)
