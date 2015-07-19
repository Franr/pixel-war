#!/usr/bin/env python
import pygame
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from client.criaturas import HandlerCriaturas
from client.pantalla import Pantalla
from client.mouse import MouseHandler
from client.teclado import TecladoHandler
from client.conexion import Conexion
from client.bala import HandlerBalas


DESIRED_FPS = 30.0  # 30 frames per second


class Juego(object):

    def __init__(self, host, equipo, srf=None):
        self.on = True
        self.principal = None
        # handlers
        self.balas = HandlerBalas(self)
        self.hcriat = HandlerCriaturas()
        self.pantalla = Pantalla(self, srf)
        self.conexion = Conexion(host, self, self.hcriat, equipo)
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

    def add_bullet(self, bala):
        self.balas.add_bullet(bala)

    def set_principal(self, jugador):
        self.principal = jugador
        self.pantalla.set_principal(jugador)

    def get_players(self):
        return self.hcriat.get_players()

    def get_bullets(self):
        return self.balas.get_balas()

    def get_score(self):
        return self.hcriat.azul, self.hcriat.rojo, self.hcriat.ronda

    def salir(self):
        self.on = False
        pygame.quit()
        reactor.stop()


if __name__ == '__main__':
    Juego('127.0.0.1', 1)
