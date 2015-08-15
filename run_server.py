#!/usr/bin/env python

from server.src.handlers import HandlerCriaturas
from server.src.mapa import Mapa
from server.src.conexion import Conexion
from server.src.score import Score


class Server(object):

    def __init__(self):
        self.pw_map = Mapa("mapa")
        self.score = Score()
        self.hcriat = HandlerCriaturas()
        self.hcriat.pw_map = self.pw_map
        self.hcriat.score = self.score
        self.conexion = Conexion(self.hcriat)


if __name__ == "__main__":
    server = Server()
