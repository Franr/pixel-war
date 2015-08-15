from twisted.internet import reactor
from twisted.internet.protocol import Factory

from protocol import PWProtocol


class MultiEchoFactory(Factory):
    def __init__(self):
        self.peers = {}

    def buildProtocol(self, addr):
        return PWProtocol(self)


class Conexion(object):

    PORT = 20000
    MAX_CONEXIONES = 20

    def __init__(self, hcriat):
        PWProtocol.hcriat = hcriat
        reactor.listenTCP(self.PORT, MultiEchoFactory())
        print 'server running...'
        reactor.run()
