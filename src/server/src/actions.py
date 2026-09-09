from collections.abc import Callable

from shared.constants import Direction, Team

from .entidades import Jugador
from .exceptions import (
    BlockedPosition,
    CantMove,
    CantShoot,
    InvalidMovementDirection,
    InvalidShootDirection,
    PlayerDoesNotExist,
)
from .handlers import BulletHandler, CreaturesHandler
from .logger import logger
from .mapa import Mapa


def create_player(team, ch: CreaturesHandler) -> tuple[Jugador, list[Jugador], tuple[int, int], Mapa]:
    # you
    x, y = ch.get_team_start_position(team)
    player: Jugador = ch.create_player(x, y, team)
    # the others
    other_players: list[Jugador] = [j for j in ch.get_players().values() if j != player]
    # the score
    score: tuple[int, int] = ch.get_score()
    return player, other_players, score, ch.get_map()


def move_player(uid: int, direction: str, ch: CreaturesHandler):
    jug = ch.get_creature_by_uid(uid)

    if not Direction.validate_2(direction):
        logger.debug(f"[move_player] uid: {uid} - invalid direction: {direction}")
        raise InvalidMovementDirection
    if not jug.is_live() or jug.cant_move():
        logger.debug(f"[move_player] uid: {uid} - NotLive/CantMove")
        raise CantMove

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

    return teleport_player(uid, x, y, ch)


def teleport_player(uid: int, x: int, y:int , ch: CreaturesHandler):
    jug = ch.get_creature_by_uid(uid)
    pw_map = ch.get_map()
    print(x, y, pw_map.pos_is_blocked(x, y))
    if pw_map.pos_is_blocked(x, y):
        raise BlockedPosition
    pw_map.move_player(jug, x, y)

    return jug


def shoot_action(uid: int, direction: str, ch: CreaturesHandler, hit_callback: Callable, die_callback: Callable):
    if not Direction.validate_4(direction):
        raise InvalidShootDirection

    jug = ch.get_creature_by_uid(uid)

    if jug.is_live() and not jug.cant_shot():
        return BulletHandler(jug, direction, ch, hit_callback, die_callback)
    else:
        raise CantShoot


def revive_player(uid, ch: CreaturesHandler):
    jug = ch.get_creature_by_uid(uid)
    jug.revive()


def increase_score(uid, ch: CreaturesHandler):
    jug = ch.get_creature_by_uid(uid)
    if jug.team == Team.BLUE:
        ch.score.murio_azul()
    else:
        ch.score.murio_rojo()
    return ch.score.get_data()


def restart_round(uid, ch: CreaturesHandler):
    try:
        ch.get_creature_by_uid(uid)
    except PlayerDoesNotExist:
        return
    ch.score.restart()
    new_players = ch.restart_players()
    new_score = ch.get_score()
    return new_players, new_score


# def add_bot(team):
    # return Bot('127.0.0.1', team)
