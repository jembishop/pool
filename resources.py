import itertools
import pathlib

import numpy as np
import pyglet


def center_image(image):
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


pyglet.resource.path = ["resources"]
pyglet.resource.reindex()

background_x = 2368
background_y = 1327
play_area_offset_abs = 143
play_area_width_abs = background_x - 2 * play_area_offset_abs
play_area_height_abs = background_y - 2 * play_area_offset_abs
play_area_height = play_area_height_abs / play_area_width_abs
play_area_sf = play_area_width_abs / background_x
ball_radius = 0.0185

play_area = np.array(
    [
        np.array(i)
        for i in [
            [play_area_offset_abs, play_area_offset_abs],
            [play_area_offset_abs + play_area_width_abs, play_area_offset_abs],
            [
                play_area_offset_abs + play_area_width_abs,
                play_area_offset_abs + play_area_height_abs,
            ],
            [play_area_offset_abs, play_area_offset_abs + play_area_height_abs],
        ]
    ]
) + np.array([-1, -1])


def scale_images():
    resolution = background_x, background_y
    images = {
        "table": pyglet.resource.image("table.png"),
        "balls": {
            name.name.split("_")[0]: pyglet.resource.image(f"sprites/{name.name}")
            for name in pathlib.Path(f"{pyglet.resource.path[0]}/sprites").glob(
                "*ball.png"
            )
        },
    }
    for image in images:
        if image != "balls":
            images[image].width, images[image].height = (
                images[image].width,
                images[image].height,
            )

    for ball in images["balls"]:
        img = images["balls"][ball]
        size = 2*(from_table_space(ball_radius) - from_table_space(0))
        images["balls"][ball].width, images["balls"][ball].height = size, size 
        center_image(img)

    return images, resolution


corner_pocket_size = 0.038
middle_pocket_size = 0.036
pockets = {
    "bl": np.array([[0, corner_pocket_size], [0, 0], [corner_pocket_size, 0]]),
    "bm": np.array(
        [[0.5 - middle_pocket_size, 0], [0.5, 0], [0.5 + middle_pocket_size, 0]]
    ),
    "br": np.array([[1 - corner_pocket_size, 0], [1, 0], [1, corner_pocket_size]]),
    "tr": np.array(
        [
            [1, play_area_height - corner_pocket_size],
            [1, play_area_height],
            [1 - corner_pocket_size, play_area_height],
        ]
    ),
    "tm": np.array(
        [
            [0.5 - middle_pocket_size, play_area_height],
            [0.5, play_area_height],
            [0.5 + middle_pocket_size, play_area_height],
        ]
    ),
    "tl": np.array(
        [
            [0, play_area_height - corner_pocket_size],
            [0, play_area_height],
            [corner_pocket_size, play_area_height],
        ]
    ),
}

def from_table_space(point):
    x = play_area[0][0] + point * play_area_width_abs
    return x.astype(int)


def to_table_space(point):
    x = (point - play_area[0][0]) / play_area_width_abs
    return x.astype(float)


def draw_points(points, color=(255, 255, 255)):
    lpoints = tuple(itertools.chain.from_iterable(points))
    pyglet.graphics.draw(
        len(points),
        pyglet.gl.GL_LINE_LOOP,
        ("v2f", lpoints),
        ("c3B", color * len(points)),
    )


def init():
    screens = pyglet.window.get_platform().get_default_display().get_screens()
    screen = max(screens, key=lambda x: x.width)
    images, resolution = scale_images()
    window = pyglet.window.Window(*resolution, screen=screen)
    return window, images
