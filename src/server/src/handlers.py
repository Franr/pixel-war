import asyncio
from collections.abc import Callable, Generator

from shared.constants import Team

from .entidades import Bala, Jugador
from .exceptions import InvalidTeam, PlayerDoesNotExist
from .logger import logger
from .mapa import Mapa
from .score import Score


def id_generator() -> Generator[int]:
    """
    the id 0 and 1 are reserved for empty (0) and blocking (1) SQM's
    """
    num = 2
    while True:
        yield num
        num += 1


class CreaturesHandler:

    VIDA_MAX = 100
    pw_map: Mapa
    score: Score

    def __init__(self):
        self.jugadores: dict[int, Jugador] = {}
        self.handler_id: Generator[int] = id_generator()

    def get_team_start_position(self, team: int) -> tuple[int, int]:
        pw_map = self.get_map()
        if team == Team.BLUE:
           return pw_map.get_blue()
        elif team == Team.RED:
            return pw_map.get_red()

        raise InvalidTeam

    def create_player(self, x, y, equipo):
        uid = next(self.handler_id)
        # instanciamos
        j = Jugador(uid, x, y, self.VIDA_MAX, self.VIDA_MAX, equipo, self)
        self.jugadores[uid] = j
        # ubicamos el jugador en el mapa
        self.pw_map.set_object(j, x, y)
        return j

    def del_creature_by_uid(self, uid):
        player = self.jugadores.pop(uid, None)
        if player:
            self.pw_map.del_object(player)
        return player

    def get_creature_by_uid(self, uid: int) -> Jugador:
        if uid not in self.jugadores:
            raise PlayerDoesNotExist
        return self.jugadores[uid]

    def get_players(self):
        return self.jugadores

    def get_map(self) -> Mapa:
        return self.pw_map

    def get_score(self) -> tuple[int, int]:
        return self.score.get_data()

    def restart_players(self):
        self.pw_map.clean_map()
        players = self.jugadores.values()
        for j in players:
            j.revive()
            self.pw_map.base_position(j)
        return players


class BulletHandler:
    DELAY = 0.05
    DMG = 5

    def __init__(self, jug: Jugador, direction: str, ch: CreaturesHandler, hit_callback: Callable, die_callback: Callable):
        self.bala = Bala(jug.uid, jug.x, jug.y, direction, jug.get_team())
        self.hit_callback = hit_callback
        self.die_callback = die_callback
        self.ch = ch
        self.mapa = self.ch.get_map()
        self.jug = jug
        self.jug.block_shot()

        asyncio.get_event_loop().call_later(self.DELAY, self.loop)

    def loop(self):
        if self.update():
            asyncio.get_event_loop().call_later(self.DELAY, self.loop)

    def update(self):
        # proximo movimiento
        x = self.bala.x + self.bala.dx
        y = self.bala.y + self.bala.dy
        # recuperamos el id de lo que haya en la proxima posicion
        mid = self.mapa.get_id_by_pos(x, y)  # mid = map id

        # hit nothing or its owner
        if mid in (0, self.bala.get_uid()):
            self.bala.mover()
            logger.debug(f"[Bullet] Player: {self.jug.uid} - Moved to: {self.bala.direction} - Spot: [{x} {y} / {mid}]")
            return True

        # hit a block
        if mid == 1:
            logger.debug(f"[Bullet] Player: {self.jug.uid} - Hit block.")
            return False
        else:
            # hit a creature
            c = self.ch.get_creature_by_uid(mid)

            # same team
            if self.bala.is_team(c.get_team()):
                self.bala.mover()
                logger.debug(f"[Bullet] Player: {self.jug.uid} - Hit same team player: {mid}. Keep moving.")
                return True
            # enemy
            else:
                logger.debug(f"[Bullet] Player: {self.jug.uid} - Hit enemy: {mid}.")
                if c.is_live():
                    if c.hit(self.DMG):
                        self.die_callback(mid)
                    else:
                        self.hit_callback(mid, self.DMG)
                return False
