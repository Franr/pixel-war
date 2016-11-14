from math import atan2, degrees
import random


SHOOT_VISION = 10


def avoid_shoot(bot, shoots, connection):
    for s in shoots:
        next_pos, direction = s.next_pos()
        if (bot.x, bot.y) != next_pos:
            continue

        mapa = connection.cf.protocol.mapa
        empties = get_all_empty_place(mapa, bot.x, bot.y)
        # remove the same direction than the shoot
        # (ugly, refactor this later)
        if direction in empties:
            empties.remove(direction)
        # opposite side of the same direction
        direction = direction[0] * -1, direction[1] * -1,
        if direction in empties:
            empties.remove(direction)
        # move away!
        if empties:
            connection.cf.protocol.move(pos_letter[random.choice(empties)])


def shoot_enemy(bot, enemies, connection):
    for enemy in enemies:
        direction = get_relative_pos(bot, enemy)
        if direction:
            connection.cf.protocol.fire(direction)


def move(_, connection):
    if connection.cf.protocol:
        connection.cf.protocol.move(random.choice(pos_letter.values()))


def get_all_empty_place(map_obj, x, y):
    positions = (0, -1), (-1,  0), (1,  0), (0,  1)
    empties = []
    for pos in positions:
        nx = x + pos[0]
        ny = y + pos[1]
        if not map_obj.is_blocking_position(nx, ny):
            empties.append(pos)
    return empties


def get_relative_pos(obj1, obj2):
    _x = obj2.x - obj1.x
    _y = obj2.y - obj1.y
    if max(map(abs, (_x, _y))) > SHOOT_VISION:
        return
    angle = int(degrees(atan2(_y, _x)))
    return angle_letter.get(angle, None)

pos_letter = {
    (0, -1): 'n',
    (-1,  0): 'o',
    (1,  0): 'e',
    (0,  1): 's'
}

angle_letter = {
    -90: 'n',
    180: 'o',
    0: 'e',
    90: 's',
    45: 'se',
    135: 'so',
    -135: 'no',
    -45: 'ne',
}
