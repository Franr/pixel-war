import time
from contextlib import contextmanager
from typing import final

from shared.constants import Direction


@final
class TemporalContextLock:

    def __init__(self, cooldown: float):
        self.cooldown = cooldown
        self.last_executed = 0.0

    @contextmanager
    def guard(self):
        """Yields True if execution is allowed, False if it should be ignored."""

        if self.is_locked():
            # Cooldown active: skip execution
            yield False
        else:
            # Cooldown expired: allow execution and update timestamp
            self.last_executed = time.monotonic()
            yield True

    def is_locked(self):
        return time.monotonic() - self.last_executed < self.cooldown

class BaseObjet:
    """ Clase base para todos los objetos (visibles) del juego """

    def __init__(self, uid: int, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.uid: int = uid

    def get_coor(self) -> tuple[int, int]:
        return self.x, self.y

    def set_coor(self, x: int, y: int):
        self.x = x
        self.y = y

    def get_uid(self):
        return self.uid


class Criatura(BaseObjet):

    """ Clase base para todas las criaturas (tanto para jugadores como monstruos """

    def __init__(self, uid: int, x: int, y: int, vida: int, vida_max: int, ch):
        super().__init__(uid, x, y)
        self.vida: int = vida
        self.vida_max: int = vida_max
        self.vivo: bool = True
        self.ch = ch
        self.team: int = 0

    def mover(self, x: int, y: int):
        self.set_coor(x, y)

    def is_live(self):
        return self.vivo

    def get_team(self):
        return self.team

    def hit(self, damage: int):
        self.vida -= damage
        if self.vida <= 0:
            self.vivo = False
            return True
        return False


@final
class Jugador(Criatura):
    """ Clase para todos los jugadores del juego """
    MOVE_COOLDOWN: float = 0.15
    SHOOT_COOLDOWN: float = 0.10

    def __init__(self, uid: int, x: int, y: int, vida: int, vida_max: int, team: int, ch):
        super().__init__(uid, x, y, vida, vida_max, ch)
        self.team = team
        self._movement_lock = TemporalContextLock(cooldown=self.MOVE_COOLDOWN)
        self._shoot_lock = TemporalContextLock(cooldown=self.SHOOT_COOLDOWN)

    def get_data(self) -> list[int]:
        return [self.get_uid(), self.team, self.x, self.y, self.vida, self.vida_max]

    def mover(self, x: int, y: int):
        # lock and then move
        with self._movement_lock.guard():
            Criatura.mover(self, x, y)

    def block_shot(self):
        with self._shoot_lock.guard():
            # just lock, bullet movement is handled by its own handler
            pass

    def cant_move(self):
        return self._movement_lock.is_locked()

    def cant_shot(self):
        return self._shoot_lock.is_locked()

    def revive(self):
        self.vivo = True
        self.vida = self.vida_max


class Bala(BaseObjet):


    def __init__(self, uid: int, x: int, y: int, direction: str, equipo: int):
        super().__init__(uid, x, y)
        self.direction: str = direction
        self.equipo: int = equipo
        self.dx: int = 0
        self.dy: int = 0
        for d in direction:
            self.calc_desplazamiento(d)

    def is_team(self, equipo: int) -> bool:
        return self.equipo == equipo

    def calc_desplazamiento(self, direction: str):
        if direction == Direction.NORTH:
            self.dy = -1
        elif direction == Direction.SOUTH:
            self.dy = 1
        elif direction == Direction.EAST:
            self.dx = 1
        elif direction == Direction.WEST:
            self.dx = -1

    def mover(self):
        self.set_coor(self.x + self.dx, self.y + self.dy)
