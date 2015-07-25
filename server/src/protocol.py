from twisted.protocols import amp

from commands import (
    Move, MoveObject, SendMap, CreateObject, CreateObjects, Login, PlayerReady, PlayerShoot,
    Shoot, PlayerHit)
from server.src.handlers import HandlerBala


def validar_dir4(dir):
    return dir in ('n', 's', 'o', 'e')


def validar_dir8(dir):
    return validar_dir4(dir) or dir in ('no', 'ne', 'so', 'se')


class PWProtocol(amp.AMP):
    hcriat = None
    mapa = None

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.echoers.append(self)

    def connectionLost(self, reason):
        self.factory.echoers.remove(self)

    def send_client(self, commandType, *a, **kw):
        echoers = [self]
        if 'broadcast' in kw:
            echoers = self.factory.echoers
            del kw['broadcast']
        for echoer in echoers:
            echoer.callRemote(commandType, *a, **kw)

    @Move.responder
    def move(self, uid, dir):
        jug = self.hcriat.get_creature_by_uid(uid)
        if not jug:
            print 'jugador no existe'
        if not validar_dir4(dir):
            print 'direccion invalida'

        if not jug.cant_move() and jug.is_live():
            if mover_criatura(jug, self.hcriat, dir):
                self.send_client(MoveObject, broadcast=True, uid=uid, x=jug.x, y=jug.y)
            else:
                print 'posicion bloqueada o jugador muerto'
        return {'ok': 1}

    @Login.responder
    def login(self, team):
        print 'login on', team
        # creamos el jugador
        mapa = self.hcriat.get_map()
        pos = mapa.getAzul() if team == "a" else mapa.getRojo()

        x, y = pos
        jugador = self.hcriat.crearJugador(x, y, team)
        # enviamos mapa
        self.send_client(SendMap, sec_map=mapa.getMapaChar())
        # creamos el jugador en todos los clientes
        self.send_client(CreateObject, broadcast=True, obj_data=jugador.get_data())
        # despues le enviamos al nuevo cliente todos los jugadores excepto el suyo
        players_data = [j.get_data() for j in self.hcriat.get_players().values() if j != jugador]
        self.send_client(CreateObjects, obj_data=players_data)
        # y por ultimo el score de las rondas
        # azul, rojo, ronda = self.hcriat.ronda.get()
        # EnviarTodos('nr', [azul, rojo, ronda])
        return {'uid': jugador.uid}

    @PlayerReady.responder
    def ready(self, uid):
        jug = self.hcriat.get_creature_by_uid(uid)
        if jug:
            jug.set_ready()
            return {'ok': 1}
        self.hcriat.start_round()

    @Shoot.responder
    def player_shoot(self, uid, direction):
        if not validar_dir8(direction):
            return

        jug = self.hcriat.get_creature_by_uid(uid)
        if not jug:
            return

        if jug.is_live() and not jug.cant_shot():
            HandlerBala(jug, direction, self)
            self.send_client(
                PlayerShoot, broadcast=True, uid=uid, direction=direction, x=jug.x, y=jug.y)
        return {'ok': 1}

    def hit(self, player_uid, damage):
        self.send_client(PlayerHit, broadcast=True, uid=player_uid, dmg=damage)


class Protocolo(object):
    pass


#     @classmethod
#     def enviarEliminarCriatura(self, uid):
#         # este es para cuando se muere
#         EnviarTodos('dl', [id])
#
#     @classmethod
#     def enviarDesconectarCriatura(self, uid):
#         # este es para cuando hace log-out
#         EnviarTodos('dc', [id])
#
#     @classmethod
#     def enviarNuevaRonda(self):
#         azul, rojo, ronda = HandlerCriaturas().ronda.get()
#         EnviarTodos('nr', [azul, rojo, ronda])
#
#     @classmethod
#     def enviarNuevasPos(self, nuevas_pos):
#         # nuevas_pos ya es un array
#         EnviarTodos('np', nuevas_pos)


def mover_criatura(criatura, hcriat, dir):
    x, y = criatura.get_coor()
    # next position
    if dir == 'n':
        y -= 1
    elif dir == 'e':
        x += 1
    elif dir == 's':
        y += 1
    elif dir == 'o':
        x -= 1

    mapa = hcriat.get_map()
    if mapa.posBloqueada(x, y):
        return False

    if not criatura.is_live():
        return False

    mapa.moverJugador(criatura, x, y)
    return True
