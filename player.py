from resources import images, table
import numpy as np
import pyglet


def unit_vec(angle):
    return np.array([np.cos(angle), np.sin(angle)])


class Player:
    init_cue_ball_dist = 0.05
    power = 0.6
    inc = 0.01

    def __init__(self, angle=0, pos=None, cue_ball=None):
        self.angle = angle
        self.cue_ball = cue_ball
        if cue_ball:
            self.pos = cue_ball.pos
        else:
            self.pos = pos
        tpos = table.from_space(self.pos)
        img = images["cue"]
        img.anchor_x = (
            img.anchor_x
            + table.from_space(self.init_cue_ball_dist)
            - table.from_space(0)
        )
        self.sprite = pyglet.sprite.Sprite(img, tpos[0], tpos[1], subpixel=True)

    def hit(self, ball):
        ball.vel = self.power * unit_vec(self.angle)

    def move(self, dir):
        print(self.angle)
        self.angle += dir * self.inc
        self.sprite.update(rotation=-(self.angle * (180 / np.pi)) % 360)

    def move_to_cue(self):
        self.pos = self.cue_ball.pos
        pos = table.from_space(self.pos)
        self.sprite.update(x=pos[0], y=pos[1])

