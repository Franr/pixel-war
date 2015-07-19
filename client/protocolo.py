from twisted.protocols import amp

from commands import (
    ID, Move, MoveObject, SendMap, CreateObject, Login, PlayerReady, PlayerShoot, Shoot)

from bala import Bala
from bloqueos import BloqueoDisp
from criaturas import Jugador, Principal
from mapa import Mapa


class PWProtocol(amp.AMP):

    def __init__(self, juego=None, hcriat=None, team=None):
        super(PWProtocol, self).__init__()
        self.juego = juego
        self.hcriat = hcriat
        self.team = team
        self.mapa = None
        self.my_id = None

    def connectionMade(self):
        print 'team:', self.team
        self.callRemote(Login, team=self.team)

    @ID.responder
    def got_id(self, uid):
        self.my_id = uid
        print 'nuevo id:', uid
        self.juego.comenzar()
        return {'ok': 1}

    @CreateObject.responder
    def create_object(self, obj_data):
        uid, equipo, x, y, vida, vida_max = obj_data
        if self.my_id and uid == self.my_id:
            j = Principal(uid, x, y, vida, vida_max, equipo)
            self.juego.set_principal(j)
        else:
            j = Jugador(uid, x, y, vida, vida_max, equipo)
        self.hcriat.add_player(j)
        self.mapa.set_creature(j, j.x, j.y)
        print 'jugador creado:', uid, "en:", x, y
        return {'ok': 1}

    def create_objects(self, args_list):
        for args in args_list:
            self.create_object(*args)

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
            self.juego.agregar_bala(Bala(uid, x, y, direction, jug.get_equipo(), self.juego))
        return {'ok': 1}

    def disparar(self, direction):
        if not BloqueoDisp.block:
            self.callRemote(Shoot, id=self.my_id, dir=direction)
            BloqueoDisp()

    def hit(self, uid, damage):
        # hit
        jugador = self.hcriat.get_creature_by_uid(uid)
        if jugador:
            jugador.hit(damage)

    def logout(self, uid):
        # desconectar
        jug = self.hcriat.get_creature_by_uid(uid)
        if jug:
            self.mapa.clean_position(jug.x, jug.y)
            self.hcriat.del_creature_by_id(uid)

    def ready(self):
        self.callRemote(PlayerReady, self.my_id)
        self.juego.comenzar()

    def move(self, direction):
        self.callRemote(Move, id=self.my_id, dir=direction)

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
