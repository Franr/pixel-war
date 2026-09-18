import asyncio
import random
from math import atan2, degrees
from typing import TYPE_CHECKING

from shared.constants import Direction

from .entidades import Jugador
from .mapa import Mapa

if TYPE_CHECKING:
    from .game import GameHandler

SHOOT_VISION = 10

directions_4 = [Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST]


def get_all_empty_place(map_obj: Mapa, x: int, y: int):
    positions = (0, -1), (-1, 0), (1, 0), (0, 1)
    empties = []
    for pos in positions:
        nx = x + pos[0]
        ny = y + pos[1]
        if not map_obj.pos_is_blocked(nx, ny):
            empties.append(pos)
    return empties


def get_relative_pos(obj1: Jugador, obj2: Jugador):
    _x = obj2.x - obj1.x
    _y = obj2.y - obj1.y
    if max(map(abs, (_x, _y))) > SHOOT_VISION:
        return
    angle = int(degrees(atan2(_y, _x)))
    return angle_letter.get(angle, None)


pos_letter = {
    (0, -1): Direction.NORTH,
    (-1, 0): Direction.WEST,
    (1, 0): Direction.EAST,
    (0, 1): Direction.SOUTH,
}

angle_letter = {
    -90: Direction.NORTH,
    180: Direction.WEST,
    0: Direction.EAST,
    90: Direction.SOUTH,
    45: Direction.SOUTH_EAST,
    135: Direction.SOUTH_WEST,
    -135: Direction.NORTH_WEST,
    -45: Direction.NORTH_EAST,
}


class Bot:
    LOOPS_PER_SECOND = 2  # actions per second

    def __init__(self, player: Jugador, gh: "GameHandler"):
        self.player = player
        self.loop = asyncio.get_running_loop()
        self.gh = gh
        self.online = True
        self.update()

    def update(self):
        if not self.avoid_shoot():
            # if no shot is incoming, move randomly
            self.move()
        # and then shoot!
        self.shoot_enemy()

        # call itself while alive
        if self.online:
            self.loop.call_later(1 / self.LOOPS_PER_SECOND, self.update)

    def avoid_shoot(self) -> bool:
        """
        Avoid the first shot from the list that is about to hit the bot.
        TODO: take in account all of them.
        """
        for s in self.gh.sh.shoots.values():
            next_pos, direction = s.next_pos()
            if (self.player.x, self.player.y) != next_pos:
                # if bullet is not about to hit you, ignore it
                continue

            empties = get_all_empty_place(self.gh.pw_map, self.player.x, self.player.y)
            # get away from the trajectory of the shot
            if direction in empties:
                empties.remove(direction)
            # opposite side of the same direction
            direction = (
                direction[0] * -1,
                direction[1] * -1,
            )
            if direction in empties:
                empties.remove(direction)
            # move away!
            if empties:
                # TODO: create a dummy Client for bots
                return self.gh.move(
                    None, self.player.uid, pos_letter[random.choice(empties)]
                )

        return False

    def shoot_enemy(self) -> bool:
        """
        Shoot the first near enemy from the list.
        """
        enemies = self.gh.ch.get_enemies(self.player.team)
        for enemy in enemies:
            if direction := get_relative_pos(self.player, enemy):
                # TODO: create a dummy Client for bots
                return self.gh.shoot(None, self.player.uid, direction)

        return False

    def move(self):
        self.gh.move(None, self.player.uid, random.choice(directions_4))

        return True
