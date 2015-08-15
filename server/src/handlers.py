import time

from twisted.internet import reactor

from entidades import Jugador, Bala
from exceptions import PlayerDoesNotExist

DEBUG = False


class Singleton(type):
 
    def __init__(cls, name, bases, dct):
        cls.__instance = None
        type.__init__(cls, name, bases, dct)
 
    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = type.__call__(cls, *args, **kwargs)
        return cls.__instance


class HandlerId(object):

    def __init__(self):
        # el id 0 se reserva para los espacios vacios
        # el id 1 se reserva para los bloques
        self.uid = 2
        
    def getSiguienteId(self):
        self.uid += 1
        return self.uid


class HandlerCriaturas:

    __metaclass__ = Singleton

    VIDA_MAX = 100
    mapa = None
    ronda = None

    def __init__(self):
        self.jugadores = {}
        self.handler_id = HandlerId()

    def crearJugador(self, x, y, equipo):
        id = self.handler_id.getSiguienteId()
        # instanciamos
        j = Jugador(id, x, y, self.VIDA_MAX, self.VIDA_MAX, equipo, self)
        self.jugadores[id] = j
        # ubicamos el jugador en el mapa
        self.mapa.setObjeto(j, x, y)
        return j

    def del_player(self, uid):
        # se llama cuando se muere un jugador
        jug = self.get_creature_by_uid(uid)
        if jug:
            self.mapa.delObjeto(jug)

    def del_creature_by_uid(self, uid):
        player = self.jugadores.pop(uid, None)
        if player:
            self.mapa.delObjeto(player)
        return player

    def get_creature_by_uid(self, uid):
        if uid not in self.jugadores:
            raise PlayerDoesNotExist
        return self.jugadores[uid]

    def get_players(self):
        return self.jugadores
        
    def get_map(self):
        return self.mapa
        
    def start_round(self):
        if len(self.jugadores) > 1:
            if not self.ronda.comenzada:
                if not self.ronda.restarting:
                    self.ronda.comenzar()
                
    def restart_players(self):
        self.mapa.limpiarTodo()
        nuevas_pos = []
        for j in self.jugadores.values():
            j.revive()
            nuevas_pos.extend(self.mapa.posicionar(j))
        return nuevas_pos
        
    def restart_round(self):
        self.ronda.restart()


class HandlerBala(object):

    def __init__(self, jug, direction, hit_callback, die_callback):
        self.bala = Bala(jug.uid, jug.x, jug.y, direction, jug.get_team())
        self.hit_callback = hit_callback
        self.die_callback = die_callback
        self.hcriat = HandlerCriaturas()
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
        mid = self.mapa.getIdByPos(x, y)  # mid = map id

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
    return mapa.getAzul() if team == 1 else mapa.getRojo()
