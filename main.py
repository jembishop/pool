import itertools
import random

import numpy as np
import pyglet

from resources import (
    from_table_space,
    play_area_height,
    pockets,
    init,
    ball_radius,
    corner_pocket_size,
    draw_points)

window, images = init()
table = pyglet.sprite.Sprite(images["table"])
balls_batch = pyglet.graphics.Batch()
ball_radius*= 1.28

class Ball:
    def __init__(self, color, pos, vel):
        self.pos = pos.astype(float)
        self.vel = vel.astype(float)
        self.color = color
        tpos = from_table_space(pos)
        self.hit = None
        self.new_pos = pos
        self.sprite = pyglet.sprite.Sprite(
            images["balls"][color], tpos[0], tpos[1], subpixel=True, batch=balls_batch
        )


random.seed(42)
balls = set()
ball_cor = 0.95


def mag(x):
    return np.sqrt(np.dot(x, x))


cap = []


def resolve_ball_collision(b1, b2):
    b1.hit = "o"
    b2.hit = "o"
    touch_dist = 2 * ball_radius
    mean_vel = (b1.vel + b2.vel) / 2
    b1_cm_vel = b1.vel - mean_vel
    #move to to exactly radius
    centers_vec = b2.pos - b1.pos
    dist = mag(centers_vec)
    print("dist", dist)
    centers_vec /= dist

    dir = b1_cm_vel / mag(b1_cm_vel)
    c = np.dot(centers_vec, dir)
    offset = np.sqrt(dist ** 2 + touch_dist ** 2 - 2 * touch_dist * dist * c) / 2
    print("offset", offset)
    b1.new_pos = b1.pos + dir * offset
    b2.new_pos = b2.pos - dir * offset

    centers_vec = b2.new_pos - b1.new_pos
    dist = mag(centers_vec)
    print("dist", dist)
    print("2rad", touch_dist)
    centers_vec /= dist
    new_speed = ball_cor * mag(b1_cm_vel)
    b1.vel = -centers_vec * new_speed + mean_vel
    b2.vel = centers_vec * new_speed + mean_vel
    # print("angle", np.arccos(np.dot(b1.vel, b2.vel)/(mag(b1.vel)*mag(b2.vel))))
    # cap.append(np.arccos(np.dot(b1.vel, b2.vel) / (mag(b1.vel) * mag(b2.vel))))


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


inc = ball_radius*(2**0.5)
speed_inc = 0.3



def replay(to_add):
    global inc
    global speed_inc
    print(inc)
    to_add.add(Ball("yellow", np.array([0.4, play_area_height/2 + inc]), np.array([speed_inc, 0])))
    to_add.add(Ball("red", np.array([1 - play_area_height/2, play_area_height/2]), np.array([0, 0])))
    speed_inc += 0.05
    print(cap)
    # inc += 0.0005


static_drag = 0.001
linear_drag = 0.002
cushion_loss = 0.25
corner_radius_ff = -0.9
middle_radius_ff = 0.9


def update(dt):
    to_add = set()
    to_remove = set()
    if len(balls) == 0:
        replay(to_add)
    for ball in balls:
        s = mag(ball.vel)
        if not s:
            continue

        # drag
        if s < 0.02:
            ball.vel *= 0
            for ball in balls:
                to_remove.add(ball)

        else:
            ball.vel -= (static_drag / s) * ball.vel + linear_drag * ball.vel
        ball.new_pos = ball.pos + ball.vel * dt

    for ball in balls:
        s = mag(ball.vel)
        if not s:
            continue
        hit = None
        # cushions
        # right
        if ball.new_pos[0] + ball_radius > 1:
            hit = "r"
        # left
        elif ball.new_pos[0] - ball_radius < 0:
            hit = "l"

        # top
        if ball.new_pos[1] + ball_radius > play_area_height:
            hit = "t"

        # bottom
        elif ball.new_pos[1] - ball_radius < 0:
            hit = "b"

        if hit:
            ball.hit = hit
            pocket = [None, None]
            if hit in ["t", "b"]:
                pocket[0] = hit
                if (
                        pockets["bm"][0][0]
                        < ball.new_pos[0] + ball_radius * middle_radius_ff
                        < pockets["bm"][-1][0]
                ):
                    pocket[1] = "m"
                elif ball.new_pos[0] - ball_radius * corner_radius_ff < corner_pocket_size:
                    pocket[1] = "l"
                elif ball.new_pos[0] + ball_radius * corner_radius_ff > 1 - corner_pocket_size:
                    pocket[1] = "r"
            elif hit in ["l", "r"]:
                pocket[1] = hit
                if ball.new_pos[1] - ball_radius * corner_radius_ff < corner_pocket_size:
                    pocket[0] = "b"
                elif ball.new_pos[1] + ball_radius * corner_radius_ff > 1 - corner_pocket_size:
                    pocket[0] = "t"

            if not None in pocket:
                print(f"POT!! {pocket}")
                to_remove.add(ball)
            else:
                if hit in ["t", "b"]:
                    ball.vel[1] *= -(1 - cushion_loss)
                else:
                    ball.vel[0] *= -(1 - cushion_loss)

    for b1, b2 in itertools.combinations(balls, 2):
        centers_vec = b2.new_pos - b1.new_pos
        dist = mag(centers_vec)
        touch_dist = 2 * ball_radius
        if dist <= touch_dist:
            resolve_ball_collision(b1, b2)
    for ball in balls:
        if not ball.hit:
            ball.pos = ball.new_pos
            new_t_pos = from_table_space(ball.pos)
            ball.sprite.update(x=new_t_pos[0], y=new_t_pos[1])
        else:
            ball.hit = None

    for ball in to_remove:
        balls.remove(ball)
    for ball in to_add:
        balls.add(ball)


test = [None, None]
pyglet.clock.schedule_interval(update, 1 / 240.0)

fps_display = pyglet.clock.ClockDisplay()


@window.event
def on_draw():
    table.draw()
    fps_display.draw()
    # draw_points(np.array([[0, 0], [background_x, background_y]]))
    balls_batch.draw()
    # draw_points(play_area)
    for pocket in pockets.values():
        draw_points(from_table_space(pocket), color=(255, 0, 0))


for ball in balls:
    print(np.array([from_table_space(ball.pos + ball_radius)]))
pyglet.app.run()
