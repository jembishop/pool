from resources import ball_radius, play_area_height
import numpy as np

ball_cor = 0.9
cushion_loss = 0.25


def mag(x):
    return np.sqrt(np.dot(x, x))


def ball_collision(b1, b2):
    new_dist = b2.new_pos - b1.new_pos
    mag_new_dist = mag(new_dist)
    touch_dist = 2 * ball_radius

    if mag_new_dist > touch_dist:
        return
    print("ball collision")
    # cm frame
    dist = b2.pos - b1.pos
    mean_vel = (b1.vel + b2.vel) / 2
    vel_cm = b1.vel - mean_vel

    # compute scoot factor
    mag_v = mag(vel_cm)
    v_bar = vel_cm / mag_v
    scoot = np.dot(dist, v_bar) - np.sqrt(
        (touch_dist) ** 2 - mag(dist) ** 2 + np.dot(dist, v_bar) ** 2
    )
    # update new position of balls after the scoot
    t_scoot = scoot / (2 * mag_v)
    b1.pos = b1.pos + t_scoot * b1.vel
    b2.pos = b2.pos + t_scoot * b2.vel

    # now compute new velocities and move out of cm frame
    dist = b2.new_pos - b1.new_pos
    dist /= mag(dist)
    new_speed = ball_cor * mag_v
    b1.vel = -dist * new_speed + mean_vel
    b2.vel = dist * new_speed + mean_vel


def cushion_collision(ball):
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
        ball.pos = ball.pos + np.array([x_dist, y_dist])
        ball.new_pos = ball.pos
        print("cushion collision")
        if hit in ["t", "b"]:
            ball.vel[1] *= -(1 - cushion_loss)
        else:
            ball.vel[0] *= -(1 - cushion_loss)
    return hit
