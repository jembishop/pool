import itertools
import random

import numpy as np
import pyglet

from resources import (
    play_area_height,
    pockets,
    init,
    ball_radius,
    draw_points,
    table,
    window,
)

from collisions import ball_collision, cushion_collision, mag
from balls import make_rack, Ball, balls_batch
from potting import potted
from player import Player
from pyglet.window import key

random.seed(42)
balls = set()


def generate_random_ball():
    return Ball(
        random.choice(["yellow", "red"]),
        play_area_height
        * np.array(
            [
                random.uniform(ball_radius, 1 - ball_radius),
                random.uniform(ball_radius, play_area_height - ball_radius),
            ]
        ),
        0.6 * np.random.random(2),
    )


incs = itertools.cycle([2 ** (0.5), 2])
speed_inc = 0.2


def replay(to_add):
    global inc
    global speed_inc
    to_add.add(
        Ball(
            "yellow",
            np.array([0.4, play_area_height / 2 + next(incs)]),
            np.array([speed_inc, 0]),
        )
    )
    to_add.add(
        Ball(
            "red",
            np.array([1 - play_area_height / 2, play_area_height / 2]),
            np.array([0, 0]),
        )
    )
    print("ball pso", [ball.pos for ball in balls])
    # speed_inc += 0.05
    # inc += 0.0005


balls = make_rack()
cue_ball = Ball("cue", np.array([0.2, 0.01 + play_area_height / 2]), np.array([2.5, 0]))
balls.add(cue_ball)

player = Player(cue_ball=cue_ball)
keyboard = key.KeyStateHandler()
window.push_handlers(keyboard)


def update(dt):
    to_add = set()
    to_remove = set()
    if max(mag(x.vel) for x in balls) < 0.01:
        allowed_to_hit = True
        if (player.pos != cue_ball.pos).all():
            player.move_to_cue()
    else:
        allowed_to_hit = False
    for ball in balls:
        ball.move(dt)
    for ball in balls:
        hit = cushion_collision(ball)
        if hit:
            pot = potted(ball, hit)
        else:
            pot = None
        if pot:
            ball, pocket = pot
            to_remove.add(ball)

    for b1, b2 in itertools.combinations(balls, 2):
        ball_collision(b1, b2)

    for ball in balls:
        ball.pos = ball.new_pos
        new_t_pos = table.from_space(ball.pos)
        ball.sprite.update(x=new_t_pos[0], y=new_t_pos[1])
    for ball in to_remove:
        balls.remove(ball)
    for ball in to_add:
        balls.add(ball)
    if keyboard[key.Z]:
        mod = 0.1
    elif keyboard[key.X]:
        mod = 3
    else:
        mod = 1
    if keyboard[key.LEFT]:
        player.move(-mod)
    elif keyboard[key.RIGHT]:
        player.move(mod)
    elif keyboard[key.SPACE] and allowed_to_hit:
        player.hit()


pyglet.clock.schedule_interval(update, 1 / 120.0)

fps_display = pyglet.clock.ClockDisplay()

from player import unit_vec


@window.event
def on_draw():
    table.sprite.draw()
    fps_display.draw()
    balls_batch.draw()
    player.sprite.draw()
    # draw_points(play_area)
    # for pocket in pockets.values():
    #     draw_points(from_table_space(pocket), color=(255, 0, 0))
    cue_dir = unit_vec(player.angle)
    draw_points(table.from_space(np.array([player.pos, player.pos + cue_dir * 1])))
    # for ball in balls:
    #     draw_points(np.array([np.array([0,0]), from_table_space(ball.pos)]))


pyglet.app.run()
