import time

from twisted.internet import reactor

from entidades import Jugador, Bala
from exceptions import PlayerDoesNotExist


class HandlerId(object):  # TODO: use a generator

    def __init__(self):
        # el id 0 se reserva para los espacios vacios
        # el id 1 se reserva para los bloques
        self.uid = 2
        
    def next_id(self):
        self.uid += 1
        return self.uid


class HandlerCriaturas:

    VIDA_MAX = 100
    pw_map = None
    score = None
    BLUE = 1
    RED = 2

    def __init__(self):
        self.jugadores = {}
        self.handler_id = HandlerId()

    def crear_jugador(self, x, y, equipo):
        uid = self.handler_id.next_id()
        # instanciamos
        j = Jugador(uid, x, y, self.VIDA_MAX, self.VIDA_MAX, equipo, self)
        self.jugadores[uid] = j
        # ubicamos el jugador en el mapa
        self.pw_map.set_object(j, x, y)

    def del_creature_by_uid(self, uid):
        player = self.jugadores.pop(uid, None)
        if player:
            self.pw_map.del_object(player)
        return player

    def get_creature_by_uid(self, uid):
        if uid not in self.jugadores:
            raise PlayerDoesNotExist
        return self.jugadores[uid]

    def get_players(self):
        return self.jugadores

    def get_map(self):
        return self.pw_map

    def get_score(self):
        return self.score.get_data()

    def restart_players(self):
        self.pw_map.clean_map()
        players = self.jugadores.values()
        for j in players:
            j.revive()
            self.pw_map.base_position(j)
        return players


class HandlerBala(object):

    def __init__(self, jug, direction, hcriat, hit_callback, die_callback):
        self.bala = Bala(jug.uid, jug.x, jug.y, direction, jug.get_team())
        self.hit_callback = hit_callback
        self.die_callback = die_callback
        self.hcriat = hcriat
        self.mapa = self.hcriat.get_map()
        self.jug = jug
        self.jug.block_shot()
        reactor.callInThread(self.handle)

    def handle(self):
        while self.update():
            time.sleep(self.bala.DELAY)

    def update(self):
        # proximo movimiento
        x = self.bala.x + self.bala.dx
        y = self.bala.y + self.bala.dy
        # recuperamos el id de lo que haya en la proxima posicion
        mid = self.mapa.get_id_by_pos(x, y)  # mid = map id

        # hit nothing or its owner
        if mid in (0, self.bala.get_uid()):
            self.bala.mover()
            return True

        # hit a block
        if mid == 1:
            return False
        else:
            # hit a creature
            c = self.hcriat.get_creature_by_uid(mid)
            if not c:
                return False

            # same team
            if self.bala.is_team(c.get_team()):
                self.bala.mover()
                return True
            # enemy
            else:
                if c.is_live():
                    if c.hit(self.bala.DMG):
                        self.die_callback(mid)
                    else:
                        self.hit_callback(mid, self.bala.DMG)
                return False


def get_team_start_position(hcriat, team):
    mapa = hcriat.get_map()
    return mapa.get_blue() if team == HandlerCriaturas.BLUE else mapa.get_red()
