from twisted.protocols import amp

from commands import UID, Move, MoveObject, SendMap, CreateObject, Login, PlayerReady, PlayerShoot, Shoot
from server.src.handlers import HandlerBala


class PWProtocol(amp.AMP):
    hcriat = None
    mapa = None

    # def connectionMade(self):
    #     pass

    @Move.responder
    def move(self, uid, dir):
        jug = self.hcriat.get_creature_by_uid(uid)
        if not jug:
            print 'jugador no existe'
        if not validar_dir4(dir):
            print 'direccion invalida'

        if not jug.cant_move() and jug.is_live():
            if mover_criatura(jug, self.hcriat, dir):
                self.callRemote(MoveObject, uid=uid, x=jug.x, y=jug.y)
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
        # enviamos uid
        self.callRemote(UID, uid=jugador.uid)
        # enviamos mapa
        self.callRemote(SendMap, sec_map=mapa.getMapaChar())
        # creamos el jugador en todos los clientes
        self.callRemote(CreateObject, obj_data=jugador.get_data())
        # despues le enviamos al nuevo cliente todos los jugadores excepto el suyo
        # players_data = [j.getDatos() for j in self.hcriat.getJugadores().values() if j != jugador]
        # self.callRemote(CreateObjects, players_data)
        # y por ultimo el score de las rondas
        # azul, rojo, ronda = self.hcriat.ronda.get()
        # EnviarTodos('nr', [azul, rojo, ronda])
        return {'ok': 1}

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
            # manejo interno
            HandlerBala(jug, direction, self)
            # envio del paquete
            self.callRemote(PlayerShoot, uid=uid, direction=direction, x=jug.x, y=jug.y)
        return {'ok': 1}


class Protocolo(object):
    pass

#
#     SEPARADOR = '|'
#
#     ## servidor <-- cliente
#
#     def __init__(self, mensaje, socket, uid):
#         self.hcriat = HandlerCriaturas()
#         # separamos el mensaje en un array
#         mensaje = mensaje.split(self.SEPARADOR)
#         # la accion siempre se encuentra en la primer posicion del array
#         accion = mensaje[0]
#
#         ## paquetes log-in
#         if accion == 'dt':
#             # este paquete se recibe cuando un cliente responde al pedido de datos en el momento de efectuar la conexion
#             equipo = mensaje[1]
#             # creamos el jugador
#             self.handlerCrearJugadorInicial(socket, uid, equipo)
#
#         elif accion == 'ok':
#             self.handlerJugadorListo(uid, socket)
#         elif accion == 'rr':
#             # ressetear ronda
#             HandlerCriaturas().restartRonda()
#
#     @classmethod
#     def enviarCrearTodosJugadores(self, socket, excepcion):
#         hcriat = HandlerCriaturas()
#         jugadores = [j for j in hcriat.getJugadores().values() if j != excepcion]
#         datos = []
#         for j in jugadores:
#             datos.extend(j.getDatos())
#         # Le agregamos la senia de que a "datos" hay que iterarlo (no uso la enie por el encoding, giles)
#         ## esto del 'i-' es re sucio
#         datos.insert(0, Enviar.IT1NIVEL)
#         Enviar(socket, 'cv', [len(jugadores), datos])
#
#     @classmethod
#     def enviarHit(self, jugador, danio):
#         EnviarTodos('ht', [jugador.getId(), danio])
#
    # @classmethod
    # def enviarMovimiento(self, jugador):
    #     EnviarTodos('mv', [jugador.getId(), jugador.x, jugador.y])
#
#     @classmethod
#     def enviarError(self, socket, uid):
#         # 1 -> movimiento imposible
#         # 2 -> no hay posiciones libres para generar jugador
#         Enviar(socket, 'er', [id])
#
#     @classmethod
#     def enviarDisparo(self, uid, dir, x, y):
#         EnviarTodos('dp', [id, dir, x, y])
#
#     @classmethod
#     def enviarMapa(self, socket, mapa):
#         sec = mapa.getMapaChar()
#         Enviar(socket, 'mp', [sec])
#
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
#
#     ## handlers paquetes recibidos
#
#
#     def handlerDisparo(self, uid, dir):
#         jug = self.hcriat.getCriaturaById(uid)
#         if jug:
#             if jug.estaVivo() and not jug.estaBloqueadoDisp():
#                 if validarDir8(dir):
#                     # manejo interno
#                     HandlerBala(jug, dir, self)
#                     # envio del paquete
#                     self.enviarDisparo(uid, dir, jug.x, jug.y)
#
#
# ## Acciones que usan el protocolo
#
# class AtacarCriatura:
#
#     def __init__(self, criat_atacante, criat_atacada, danio, hcriat):
#         if criat_atacante.esEquipo(criat_atacada.getEquipo()):
#             return
#         else:
#             if criat_atacada.estaVivo():
#                 criat_atacada.hit(danio)
#                 Protocolo.enviarHit(criat_atacada, danio)
#
#


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
    # Protocolo.enviarMovimiento(criatura)
    return True
#
#
# ### FUNCIONES PARA VALIDAR


def validar_dir4(dir):
    return dir in ('n', 's', 'o', 'e')


def validar_dir8(dir):
    return validar_dir4(dir) or dir in ('no', 'ne', 'so', 'se')
