from twisted.protocols import amp

from commands import ID, Move, MoveObject, SendMap, CreateObject, Login, PlayerReady, PlayerShoot, Shoot

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
        self.my_id = None

    def connectionMade(self):
        print 'team:', self.team
        self.callRemote(Login, team=self.team)

    @ID.responder
    def got_id(self, id):
        self.my_id = id
        print 'nuevo id:', id
        self.juego.comenzar()
        return {'ok': 1}

    @CreateObject.responder
    def create_object(self, obj_data):
        id, equipo, x, y, vida, vida_max = obj_data
        if self.my_id and id == self.my_id:
            j = Principal(id, x, y, vida, vida_max, equipo)
            self.juego.setPrincipal(j)
        else:
            j = Jugador(id, x, y, vida, vida_max, equipo)
        self.hcriat.addJugador(j)
        self.mapa.setCriatura(j, j.x, j.y)
        print 'jugador creado:', id, "en:", x, y
        return {'ok': 1}

    def create_objects(self, list):
        for args in list:
            self.create_object(*args)

    @SendMap.responder
    def send_map(self, sec_map):
        # receiving map on client
        self.mapa = Mapa(sec_map)
        self.juego.pantalla.dibujar.setMapa(self.mapa)
        return {'ok': 1}

    @MoveObject.responder
    def move_object(self, id, x, y):
        # movemos el objeto
        criat = self.hcriat.getCriaturaById(id)
        if criat:
            self.mapa.moverCriatura(criat, x, y)
            criat.mover(x, y)
        return {'ok': 1}

    @PlayerShoot.responder
    def player_shoot(self, id, dir, x, y):
        # disparo
        jug = self.hcriat.getCriaturaById(id)
        if jug:
            self.juego.agregarBala(Bala(id, x, y, dir, jug.getEquipo(), self.juego))
        return {'ok': 1}

    def disparar(self, dir):
        if not BloqueoDisp.block:
            self.callRemote(Shoot, id=self.my_id, dir=dir)
            BloqueoDisp()

    def hit(self, id, damage):
        # hit
        jugador = self.hcriat.getCriaturaById(id)
        if jugador:
            jugador.hit(damage)

    def logout(self, id):
        # desconectar
        jug = self.hcriat.getCriaturaById(id)
        if jug:
            self.mapa.limpiarPos(jug.x, jug.y)
            self.hcriat.delCriaturaById(id)

    def ready(self):
        self.callRemote(PlayerReady, self.my_id)
        self.juego.comenzar()

    def move(self, dir):
        self.callRemote(Move, id=self.my_id, dir=dir)

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
