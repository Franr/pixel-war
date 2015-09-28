import os

from twisted.application import service, internet

from server.main import Server
from server.src.protocol import MultiEchoFactory, PWProtocol


def get_service():
    openshit_ip = os.getenv("OPENSHIFT_INTERNAL_IP")
    extra_args = {}
    if openshit_ip:
        extra_args = {'interface': openshit_ip}

    server = Server()
    PWProtocol.hcriat = server.hcriat
    return internet.TCPServer(20000, MultiEchoFactory(), **extra_args)

application = service.Application("Pixel War Server")
service = get_service()
service.setServiceParent(application)
