import exceptions
from handlers import BulletHandler, CreaturesHandler


def validate_dir4(direction):
    return direction in ('n', 's', 'o', 'e')


def validate_dir8(direction):
    return validate_dir4(direction) or direction in ('no', 'ne', 'so', 'se')


def create_player(team, hcriat):
    # you
    x, y = hcriat.get_team_start_position(team)
    player = hcriat.create_player(x, y, team)
    # the others
    other_players = [j for j in hcriat.get_players().values() if j != player]
    # the score
    score = hcriat.get_score()
    return player, other_players, score, hcriat.get_map()


def move_player(uid, direction, hcriat):
    jug = hcriat.get_creature_by_uid(uid)
    if not validate_dir4(direction):
        raise exceptions.InvalidMovementDirection

    if not jug.is_live() or jug.cant_move():
        raise exceptions.CantMove

    x, y = jug.get_coor()
    # next position
    if direction == 'n':
        y -= 1
    elif direction == 'e':
        x += 1
    elif direction == 's':
        y += 1
    elif direction == 'o':
        x -= 1

    return teleport_player(uid, x, y, hcriat)


def teleport_player(uid, x, y, hcriat):
    jug = hcriat.get_creature_by_uid(uid)
    pw_map = hcriat.get_map()
    if pw_map.pos_is_blocked(x, y):
        raise exceptions.BlockedPosition
    pw_map.move_player(jug, x, y)

    return jug


def shoot_action(uid, direction, hcriat, hit_callback, die_callback):
    if not validate_dir8(direction):
        raise exceptions.InvalidShootDirection

    jug = hcriat.get_creature_by_uid(uid)

    if jug.is_live() and not jug.cant_shot():
        shoot_handler = BulletHandler(jug, direction, hcriat, hit_callback, die_callback)
        return jug, shoot_handler
    raise exceptions.CantShoot


def revive_player(uid, hcriat):
    jug = hcriat.get_creature_by_uid(uid)
    jug.revive()


def increase_score(uid, hcriat):
    jug = hcriat.get_creature_by_uid(uid)
    if jug.team == CreaturesHandler.BLUE:
        hcriat.score.murio_azul()
    else:
        hcriat.score.murio_rojo()
    return hcriat.score.get_data()


def restart_round(uid, hcriat):
    jug = hcriat.get_creature_by_uid(uid)
    if not jug:  # TODO: validate that the player is the round leader
        return
    hcriat.score.restart()
    new_players = hcriat.restart_players()
    new_score = hcriat.get_score()
    return new_players, new_score
