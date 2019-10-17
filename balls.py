import pyglet
import numpy as np
from resources import ball_radius, play_area_height, images, table
from collisions import mag


balls_batch = pyglet.graphics.Batch()
class Ball:

    static_drag = 0.0015
    linear_drag = 0.0025

    def __init__(self, color, pos, vel=np.array([0, 0])):
        self.pos = pos.astype(float)
        self.vel = vel.astype(float)
        self.color = color
        tpos = table.from_space(pos)
        self.new_pos = pos
        self.sprite = pyglet.sprite.Sprite(
            images["balls"][color], tpos[0], tpos[1], subpixel=True, batch=balls_batch
        )

    def move(self, dt):
        s = mag(self.vel)
        # drag
        if s < 0.02:
            self.vel *= 0

        else:
            self.vel -= (self.static_drag / s) * self.vel + self.linear_drag * self.vel
        self.new_pos = self.pos + self.vel * dt


def make_rack():
    s = np.sin(np.pi / 6)
    c = np.cos(np.pi / 6)
    d = 2 * ball_radius + 0.0005
    rack = {
        Ball("red", np.array([0, 0])),
        Ball("red", np.array([d * c, d * s])),
        Ball("yellow", np.array([d * c, d * s - d])),
        Ball("yellow", np.array([2 * d * c, 2 * d * s])),
        Ball("black", np.array([2 * d * c, 2 * d * s - d])),
        Ball("red", np.array([2 * d * c, 2 * d * s - 2 * d])),
        Ball("red", np.array([3 * d * c, 3 * d * s])),
        Ball("yellow", np.array([3 * d * c, 3 * d * s - d])),
        Ball("red", np.array([3 * d * c, 3 * d * s - 2 * d])),
        Ball("yellow", np.array([3 * d * c, 3 * d * s - 3 * d])),
        Ball("yellow", np.array([4 * d * c, 4 * d * s])),
        Ball("yellow", np.array([4 * d * c, 4 * d * s - d])),
        Ball("red", np.array([4 * d * c, 4 * d * s - 2 * d])),
        Ball("yellow", np.array([4 * d * c, 4 * d * s - 3 * d])),
        Ball("red", np.array([4 * d * c, 4 * d * s - 4 * d])),
    }
    for ball in rack:
        ball.pos += np.array(
            [1 - play_area_height / 2 - 2 * d * c, play_area_height / 2]
        )
    return rack