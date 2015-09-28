import os

from twisted.application import service, internet

from server.main import Server
from server.src.protocol import MultiEchoFactory, PWProtocol


def get_service():
    port = int(os.environ['OPENSHIFT_DIY_PORT'] or 20000)
    interface = os.environ['OPENSHIFT_DIY_IP']
    extra_args = {}
    if interface:
        extra_args = {'interface': interface}

    server = Server()
    PWProtocol.hcriat = server.hcriat
    return internet.TCPServer(port, MultiEchoFactory(), **extra_args)

application = service.Application("Pixel War Server")
service = get_service()
service.setServiceParent(application)
