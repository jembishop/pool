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
    draw_points,
)

window, images = init()
table = pyglet.sprite.Sprite(images["table"])
balls_batch = pyglet.graphics.Batch()


random.seed(42)
balls = set()
ball_cor = 0.95


def mag(x):
    return np.sqrt(np.dot(x, x))


class Ball:
    def __init__(self, color, pos, vel=np.array([0, 0])):
        self.pos = pos.astype(float)
        self.vel = vel.astype(float)
        self.color = color
        tpos = from_table_space(pos)
        self.new_pos = pos
        self.sprite = pyglet.sprite.Sprite(
            images["balls"][color], tpos[0], tpos[1], subpixel=True, batch=balls_batch
        )


def make_rack():
    s = np.sin(np.pi / 6)
    c = np.cos(np.pi / 6)
    d = 2 * ball_radius + 0.0005
    rack = {
        Ball("red", np.array([0, 0])),
        Ball("red", np.array([d * c, d * s])),
        Ball("yellow", np.array([d * c, d * s -d])),
        Ball("yellow", np.array([2 * d * c, 2 * d * s])),
        Ball("black", np.array([2 * d * c, 2 * d * s - d])),
        Ball("red", np.array([2 * d * c, 2 * d * s - 2*d])),
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


def resolve_ball_collision(b1, b2):
    y = b2.pos - b1.pos
    mean_vel = (b1.vel + b2.vel) / 2
    v = b1.vel - mean_vel
    mag_v = mag(v)
    if mag_v < 0.01:
        return
    v_bar = v / mag_v
    term =(2 * ball_radius) ** 2 - mag(y) ** 2 + np.dot(y, v_bar) ** 2 
    # print("magy", mag(y))
    # print("dist", 2*ball_radius)
    # print("TERM", term)
    # print("sqrt", np.sqrt(term))
    scoot = np.dot(y, v_bar) - np.sqrt((2 * ball_radius) ** 2 - mag(y) ** 2 + np.dot(y, v_bar) ** 2)
        
    
    # print("scoot", scoot)
    t_scoot = scoot / (2 * mag_v)
    assert isinstance(t_scoot, float)
    # print("b1_pos", b1.pos)
    # print("b2_pos", b2.pos)
    b1.pos = b1.pos + t_scoot * b1.vel
    b2.pos = b2.pos + t_scoot * b2.vel
    # print("b1_pos", b1.new_pos)
    # print("b2_pos", b2.new_pos)

    centers_vec = b2.new_pos - b1.new_pos
    # print("centers_vec", centers_vec)
    dist = mag(centers_vec)
    centers_vec /= dist
    # print("dist", dist)
    # print("2rad", 2 * ball_radius)
    new_speed = ball_cor * mag_v
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


def resolve_cushion(ball):
    to_remove = set()
    # cushions
    hit = None
    x_dist = 0
    y_dist = 0
    # right
    if ball.new_pos[0] + ball_radius > 1:
        x_dist = 1 - (ball.pos[0] + ball_radius)
        y_dist = ball.vel[1] * x_dist / ball.vel[0]
        hit = "r"
    # left
    elif ball.new_pos[0] - ball_radius < 0:
        x_dist = ball.pos[0] - ball_radius
        y_dist = ball.vel[1] * x_dist / ball.vel[0]
        hit = "l"

    # top
    if ball.new_pos[1] + ball_radius > play_area_height:
        y_dist = play_area_height - (ball.pos[1] + ball_radius)
        x_dist = ball.vel[0] * y_dist / ball.vel[1]
        hit = "t"

    # bottom
    elif ball.new_pos[1] - ball_radius < 0:
        y_dist = ball.pos[1] - ball_radius
        x_dist = ball.vel[0] * y_dist / ball.vel[1]
        hit = "b"

    if hit:
        ball.new_pos = ball.pos + np.array([x_dist, y_dist])

    if hit:
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
            elif (
                ball.new_pos[0] + ball_radius * corner_radius_ff
                > 1 - corner_pocket_size
            ):
                pocket[1] = "r"
        elif hit in ["l", "r"]:
            pocket[1] = hit
            if ball.new_pos[1] - ball_radius * corner_radius_ff < corner_pocket_size:
                pocket[0] = "b"
            elif (
                ball.new_pos[1] + ball_radius * corner_radius_ff
                > 1 - corner_pocket_size
            ):
                pocket[0] = "t"

        if hit in ["t", "b"]:
            ball.vel[1] *= -(1 - cushion_loss)
        else:
            ball.vel[0] *= -(1 - cushion_loss)
        if not None in pocket:
            print(f"POT!! {pocket}")
            if ball.color != "cue":
                to_remove.add(ball)
    if to_remove:
        print(to_remove)
    return to_remove




static_drag = 0.0015
linear_drag = 0.0025
cushion_loss = 0.25
corner_radius_ff = 0
middle_radius_ff = 0.7

balls = make_rack()
cue_ball = Ball("cue", np.array([0.2, 0.01+play_area_height / 2]), np.array([3.5, 0]))
balls.add(cue_ball)
import time
begin =True
def update(dt):
    global begin
    if begin:
        time.sleep(2)
        begin = False
    to_add = set()
    to_remove = set()
    if max(mag(x.vel) for x in balls) < 0.01:
        cue_ball.vel = np.random.random(2)
    for ball in balls:
        s = mag(ball.vel)

        # drag
        if s < 0.02:
            ball.vel *= 0
            

        else:
            ball.vel -= (static_drag / s) * ball.vel + linear_drag * ball.vel
        ball.new_pos = ball.pos + ball.vel * dt

    for ball in balls:
        to_remove = resolve_cushion(ball)|to_remove

    for b1, b2 in itertools.combinations(balls, 2):
        centers_vec = b2.new_pos - b1.new_pos
        dist = mag(centers_vec)
        touch_dist = 2 * ball_radius
        if dist < touch_dist:
            resolve_ball_collision(b1, b2)
    for ball in balls:
        ball.pos = ball.new_pos
        new_t_pos = from_table_space(ball.pos)
        ball.sprite.update(x=new_t_pos[0], y=new_t_pos[1])
    for ball in to_remove:
        balls.remove(ball)
    for ball in to_add:
        balls.add(ball)


pyglet.clock.schedule_interval(update, 1 / 120.0)

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


    # for ball in balls:
    #     draw_points(np.array([np.array([0,0]), from_table_space(ball.pos)]))
pyglet.app.run()

