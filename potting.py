from resources import ball_radius, corner_pocket_size, middle_pocket_size, pockets

corner_radius_ff = 0
middle_radius_ff = 0.7


def potted(ball, hit):
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
        if ball.color != "cue":
            return ball, pocket
