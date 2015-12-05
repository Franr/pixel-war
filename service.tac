from twisted.application import service, internet

from server.main import Server
from server.src.protocol import PWProtocolFactory, PWProtocol


def get_service():
    server = Server()
    PWProtocol.hcriat = server.hcriat
    # TODO: take port from command line
    port = 20000
    return internet.TCPServer(port, PWProtocolFactory())

application = service.Application("Pixel War Server")
service = get_service()
service.setServiceParent(application)
