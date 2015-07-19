#!/usr/bin/env python

from server.src.handlers import HandlerCriaturas
from server.src.mapa import Mapa
from server.src.conexion import Conexion
from server.src.ronda import Ronda


class Server(object):

    def __init__(self):
        self.mapa = Mapa("mapa")
        self.ronda = Ronda()
        self.hcriat = HandlerCriaturas()
        self.hcriat.mapa = self.mapa
        self.hcriat.ronda = self.ronda
        self.conexion = Conexion(self.mapa, self.hcriat)


if __name__ == "__main__":
    Server()
