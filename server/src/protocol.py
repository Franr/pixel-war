from twisted.protocols import amp

from game_commands import (
    Move, MoveObject, SendMap, CreateObject, CreateObjects, Login, PlayerReady, PlayerShoot,
    Shoot, PlayerHit, LogoutPlayer)
import exceptions
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

    def connectionLost(self, reason):
        player = self.factory.peers.pop(self)
        self.hcriat.del_creature_by_uid(player.uid)
        self.send_client(LogoutPlayer, broadcast=True, uid=player.uid)

    def send_client(self, commandType, *a, **kw):
        echoers = [self]
        if 'broadcast' in kw:
            echoers = self.factory.peers.keys()
            del kw['broadcast']
        for echoer in echoers:
            echoer.callRemote(commandType, *a, **kw)

    @Move.responder
    def move(self, uid, direction):
        try:
            jug = move_player(uid, direction, self.hcriat)
        except exceptions.BlockedPosition:
            pass
        else:
            self.send_client(MoveObject, broadcast=True, uid=uid, x=jug.x, y=jug.y)
        return {'ok': 1}

    @Login.responder
    def login(self, team):
        player, other_players, map = create_player(team, self.hcriat)
        self.factory.peers[self] = player
        # map
        self.send_client(SendMap, sec_map=map.getMapaChar())
        # create new player on all the clients
        self.send_client(CreateObject, broadcast=True, obj_data=player.get_data())
        # create all the players on the new client
        self.send_client(CreateObjects, obj_data=[p.get_data() for p in other_players])
        return {'uid': player.uid}

    @PlayerReady.responder
    def ready(self, uid):  # TODO: deprecated?
        jug = self.hcriat.get_creature_by_uid(uid)
        if jug:
            jug.set_ready()
            return {'ok': 1}
        self.hcriat.start_round()

    @Shoot.responder
    def player_shoot(self, uid, direction):
        jug, shoot_handler = shoot_action(uid, direction, self.hcriat, self.hit)
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
#     def enviarNuevaRonda(self):
#         azul, rojo, ronda = HandlerCriaturas().ronda.get()
#         EnviarTodos('nr', [azul, rojo, ronda])
#
#     @classmethod
#     def enviarNuevasPos(self, nuevas_pos):
#         # nuevas_pos ya es un array
#         EnviarTodos('np', nuevas_pos)


def create_player(team, hcriat):
    # creamos el jugador
    map = hcriat.get_map()
    pos = map.getAzul() if team == 1 else map.getRojo()

    x, y = pos
    player = hcriat.crearJugador(x, y, team)

    other_players = [j for j in hcriat.get_players().values() if j != player]

    # y por ultimo el score de las rondas
    # azul, rojo, ronda = self.hcriat.ronda.get()
    # EnviarTodos('nr', [azul, rojo, ronda])
    return player, other_players, map


def move_player(uid, direction, hcriat):
    jug = hcriat.get_creature_by_uid(uid)
    if not jug:
        raise exceptions.PlayerDoesNotExist
    if not validar_dir4(direction):
        raise exceptions.InvalidMovementDirection

    if jug.is_live() and not jug.cant_move():
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

        mapa = hcriat.get_map()
        if mapa.posBloqueada(x, y):
            raise exceptions.BlockedPosition
        mapa.moverJugador(jug, x, y)

        return jug


def shoot_action(uid, direction, hcriat, callback):
    if not validar_dir8(direction):
        raise exceptions.InvalidShootDirection

    jug = hcriat.get_creature_by_uid(uid)
    if not jug:
        raise exceptions.PlayerDoesNotExist

    if jug.is_live() and not jug.cant_shot():
        shoot_handler = HandlerBala(jug, direction, callback)
        return jug, shoot_handler
