from twisted.internet import reactor
from twisted.internet.protocol import Factory

from protocol import PWProtocol
from handlers import HandlerCriaturas


class MultiEchoFactory(Factory):
    def __init__(self):
        self.echoers = []

    def buildProtocol(self, addr):
        return PWProtocol(self)


class Conexion(object):

    PORT = 20000
    MAX_CONEXIONES = 20

    def __init__(self, mapa, hcriat):
        PWProtocol.mapa = mapa
        PWProtocol.hcriat = hcriat
        reactor.listenTCP(self.PORT, MultiEchoFactory())
        reactor.run()


class Cliente(object):

    """ Clase para manejar los sockets hijos conectados con los clientes."""
    
    def __init__(self, socket, direccion, id):
        self.socket = socket
        self.direccion = direccion[0] + ':' + str(direccion[1])
        self.id = id
        self.hcriat = HandlerCriaturas()
        self.size = 1024
        # una vez creado le enviamos su id
        Protocolo.enviarId(socket, self.id)
        # funcionando!

    def run(self):
        Protocolo(paquete, self.socket, self.id)
