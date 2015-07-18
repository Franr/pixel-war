#!/usr/bin/env python
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import pygame

from client.criaturas import HandlerCriaturas
from client.pantalla import Pantalla
from client.mouse import MouseHandler
from client.teclado import TecladoHandler
from client.conexion import Conexion
from client.bala import HandlerBalas


DESIRED_FPS = 30.0  # 30 frames per second


class Juego(object):

    def __init__(self, host, equipo, srf=None):
        # banderas
        self.on = True
        # instanciamos las clases necesarias
        self.balas = HandlerBalas(self)
        self.hcriat = HandlerCriaturas()
        self.pantalla = Pantalla(self.hcriat, self.balas, srf)
        self.conectar(host, equipo)
        self.teclado = TecladoHandler(self)
        self.mouse = MouseHandler(self)
        # loop principal
        tick = LoopingCall(self.update)
        tick.start(1.0 / DESIRED_FPS)
        reactor.run()

    def update(self):
        self.pantalla.update()
        self.mouse.update()
        if not self.teclado.update():
            self.salir()

    def comenzar(self):
        self.pantalla.activar()
        self.teclado.activar()
        self.mouse.activar()

    def agregarBala(self, bala):
        self.balas.agregarBala(bala)

    def setPrincipal(self, jugador):
        self.principal = jugador
        self.pantalla.setPrincipal(jugador)

    def conectar(self, host, equipo):
        self.conexion = Conexion(host, self, self.hcriat, equipo)
        # no nos pudimos conectar
        # else:
        #     self.login.error_conexion()
        #     self.salir()

    def salir(self):
        self.on = False
        self.pantalla.salir()
        reactor.stop()


if __name__ == '__main__':
    Juego('127.0.0.1', 1)
