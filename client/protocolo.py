from twisted.protocols import amp

from commands import (
    Move, MoveObject, SendMap, CreateObject, CreateObjects, Login, PlayerReady, PlayerShoot, Shoot,
    PlayerHit)

from bala import Bala
from bloqueos import BloqueoDisp
from criaturas import Jugador
from mapa import Mapa


class PWProtocol(amp.AMP):

    def __init__(self, juego=None, hcriat=None, team=None):
        super(PWProtocol, self).__init__()
        self.juego = juego
        self.hcriat = hcriat
        self.team = team
        self.mapa = None
        self.my_uid = None

    def connectionMade(self):
        print 'team:', self.team
        self.callRemote(Login, team=self.team).addCallback(self.set_main_player)

    def set_main_player(self, result):
        self.my_uid = result['uid']
        print 'tu id:', self.my_uid
        principal = self.hcriat.get_creature_by_uid(self.my_uid)
        principal.es_principal = True
        self.juego.set_principal(principal)
        self.juego.comenzar()

    @CreateObject.responder
    def create_object(self, obj_data):
        uid, equipo, x, y, vida, vida_max = obj_data
        player = Jugador(uid, x, y, vida, vida_max, equipo)
        self.hcriat.add_player(player)
        self.mapa.set_creature(player, player.x, player.y)
        print 'jugador creado:', uid, "en:", x, y
        return {'ok': 1}

    @CreateObjects.responder
    def create_objects(self, obj_data):
        for player_data in obj_data:
            self.create_object(player_data)
        return {'ok': 1}

    @SendMap.responder
    def send_map(self, sec_map):
        # receiving map on client
        self.mapa = Mapa(sec_map)
        self.juego.pantalla.dibujar.set_map(self.mapa)
        return {'ok': 1}

    @MoveObject.responder
    def move_object(self, uid, x, y):
        # movemos el objeto
        criat = self.hcriat.get_creature_by_uid(uid)
        if criat:
            self.mapa.move_creature(criat, x, y)
            criat.mover(x, y)
        return {'ok': 1}

    @PlayerShoot.responder
    def player_shoot(self, uid, direction, x, y):
        # disparo
        jug = self.hcriat.get_creature_by_uid(uid)
        if jug:
            self.juego.add_bullet(Bala(uid, x, y, direction, jug.get_equipo(), self.juego))
        return {'ok': 1}

    @PlayerHit.responder
    def hit(self, uid, dmg):
        jugador = self.hcriat.get_creature_by_uid(uid)
        if jugador:
            jugador.hit(dmg)
        return {'ok': 1}

    def disparar(self, direction):
        if not BloqueoDisp.block:
            self.callRemote(Shoot, uid=self.my_uid, direction=direction)
            BloqueoDisp()

    def logout(self, uid):
        # desconectar
        jug = self.hcriat.get_creature_by_uid(uid)
        if jug:
            self.mapa.clean_position(jug.x, jug.y)
            self.hcriat.del_creature_by_id(uid)

    def ready(self):
        self.callRemote(PlayerReady, self.my_uid)
        self.juego.comenzar()

    def move(self, direction):
        self.callRemote(Move, uid=self.my_uid, dir=direction)

        # elif accion == 'nr':
        #     # nueva ronda
        #     score_azul = int(mensaje[0])
        #     score_rojo = int(mensaje[1])
        #     ronda = int(mensaje[2])
        #     self.hcriat.setScore(score_azul, score_rojo, ronda)
        #     self.hcriat.resetTodos()

        # elif accion == 'np':
        #     # nuevas posiciones de todos los jugadores
        #     for i in range(0, len(mensaje), 3):
        #         id = int(mensaje[i])
        #         px = int(mensaje[i+1])
        #         py = int(mensaje[i+2])
        #         jug = self.hcriat.getCriaturaById(id)
        #         if jug:
        #             jug.mover(px, py)
