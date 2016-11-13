from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import ClientFactory

from protocolo import PWProtocol


class CustomClientFactory(ClientFactory):

    def __init__(self, juego, hcriat, team):
        self.juego = juego
        self.hcriat = hcriat
        self.team = team

    def buildProtocol(self, _):
        self.protocol = PWProtocol(self.juego, self.hcriat, self.team)
        return self.protocol


class Conexion(object):

    PORT = 20000
    cf = None

    def __init__(self, host, juego, hcriat, team):
        endpoint = TCP4ClientEndpoint(reactor, host, self.PORT)
        self.cf = CustomClientFactory(juego, hcriat, team)
        self.cliente = endpoint.connect(self.cf)
