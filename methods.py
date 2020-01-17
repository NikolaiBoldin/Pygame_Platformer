from pygame import *
import os


def load_image(name, color_key=None):
    fullname = os.path.join('data/sprites/', name)
    try:
        im = image.load(fullname)
    except error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    im = im.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = im.get_at((0, 0))
        im.set_colorkey(color_key)
    return im


def get_list_sprites(sheet, line, count_frames, x, y):
    list_frames = []
    for i in range(count_frames):
        list_frames.append(sheet.subsurface(Rect(
            (x * i, y * line), (x, y))))
    return list_frames
