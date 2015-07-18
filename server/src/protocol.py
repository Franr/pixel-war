from twisted.protocols import amp

from commands import ID, Move, MoveObject, SendMap, CreateObject, Login, PlayerReady, PlayerShoot, Shoot
from server.src.handlers import HandlerBala


class PWProtocol(amp.AMP):
    hcriat = None
    mapa = None

    # def connectionMade(self):
    #     pass

    @Move.responder
    def move(self, id, dir):
        jug = self.hcriat.getCriaturaById(id)
        if not jug:
            print 'jugador no existe'
        if not validar_dir4(dir):
            print 'direccion invalida'

        if not jug.estaBloqueadoMov() and jug.estaVivo():
            if mover_criatura(jug, self.hcriat, dir):
                self.callRemote(MoveObject, id=id, x=jug.x, y=jug.y)
            else:
                print 'posicion bloqueada o jugador muerto'
        return {'ok': 1}

    @Login.responder
    def login(self, team):
        print 'login on', team
        # creamos el jugador
        mapa = self.hcriat.getMapa()
        pos = mapa.getAzul() if team == "a" else mapa.getRojo()
        # no hay lugar
        # if not pos:
        #     print "Error: Todos los lugares ocupados."
        #     self.enviarError(socket, 2)

        x, y = pos
        jugador = self.hcriat.crearJugador(x, y, team)
        # enviamos id
        self.callRemote(ID, id=jugador.id)
        # enviamos mapa
        self.callRemote(SendMap, sec_map=mapa.getMapaChar())
        # creamos el jugador en todos los clientes
        self.callRemote(CreateObject, obj_data=jugador.getDatos())
        # despues le enviamos al nuevo cliente todos los jugadores excepto el suyo
        # players_data = [j.getDatos() for j in self.hcriat.getJugadores().values() if j != jugador]
        # self.callRemote(CreateObjects, players_data)
        # y por ultimo el score de las rondas
        # azul, rojo, ronda = self.hcriat.ronda.get()
        # EnviarTodos('nr', [azul, rojo, ronda])
        return {'ok': 1}

    @PlayerReady.responder
    def ready(self, id):
        jug = self.hcriat.getCriaturaById(id)
        if jug:
            jug.setListo()
            return {'ok': 1}
        self.hcriat.comenzarRonda()

    @Shoot.responder
    def player_shoot(self, id, dir):
        if not validar_dir8(dir):
            return

        jug = self.hcriat.getCriaturaById(id)
        if not jug:
            return

        if jug.estaVivo() and not jug.estaBloqueadoDisp():
            # manejo interno
            HandlerBala(jug, dir, self)
            # envio del paquete
            self.callRemote(PlayerShoot, id=id, dir=dir, x=jug.x, y=jug.y)
        return {'ok': 1}


class Protocolo: pass
#
#     SEPARADOR = '|'
#
#     ## servidor <-- cliente
#
#     def __init__(self, mensaje, socket, id):
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
#             self.handlerCrearJugadorInicial(socket, id, equipo)
#
#         elif accion == 'ok':
#             self.handlerJugadorListo(id, socket)
#
#         ## paquetes in-game
#         elif accion == 'mv':
#             # movimiento
#             dir = mensaje[1]
#             self.handlerMovimiento(id, dir)
#
#         elif accion == 'dp':
#             # disparo
#             dir = mensaje[1]
#             self.handlerDisparo(id, dir)
#
#         elif accion == 'rr':
#             # ressetear ronda
#             HandlerCriaturas().restartRonda()
#
#          ## DEBERIA IR UN PAQUETE DE DESCONEXION ACA TAMBIEN
#
#         else:
#             print "Paquete desconocido:", accion
#
#     ## servidor --> cliente
#
#     @classmethod
#     def enviarId(self, socket, id):
#         Enviar(socket, 'id', [id])
#
#     @classmethod
#     def enviarCrearJugador(self, jugador):
#         # para crear un jugador en todos los clientes
#         datos = jugador.getDatos()
#         EnviarTodos('cr', datos)
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
#     def enviarError(self, socket, id):
#         # 1 -> movimiento imposible
#         # 2 -> no hay posiciones libres para generar jugador
#         Enviar(socket, 'er', [id])
#
#     @classmethod
#     def enviarDisparo(self, id, dir, x, y):
#         EnviarTodos('dp', [id, dir, x, y])
#
#     @classmethod
#     def enviarMapa(self, socket, mapa):
#         sec = mapa.getMapaChar()
#         Enviar(socket, 'mp', [sec])
#
#     @classmethod
#     def enviarEliminarCriatura(self, id):
#         # este es para cuando se muere
#         EnviarTodos('dl', [id])
#
#     @classmethod
#     def enviarDesconectarCriatura(self, id):
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
#     def handlerDisparo(self, id, dir):
#         jug = self.hcriat.getCriaturaById(id)
#         if jug:
#             if jug.estaVivo() and not jug.estaBloqueadoDisp():
#                 if validarDir8(dir):
#                     # manejo interno
#                     HandlerBala(jug, dir, self)
#                     # envio del paquete
#                     self.enviarDisparo(id, dir, jug.x, jug.y)
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
    x, y = criatura.getCoor()
    # next position
    if dir == 'n':
        y -= 1
    elif dir == 'e':
        x += 1
    elif dir == 's':
        y += 1
    elif dir == 'o':
        x -= 1

    mapa = hcriat.getMapa()
    if mapa.posBloqueada(x, y):
        return False

    if not criatura.estaVivo():
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
