#!/usr/bin/env python
import pygame
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from client.bala import HandlerBalas
from client.conexion import Conexion
from client.criaturas import HandlerCreatures
from client.mapa import Mapa
from client.mouse import MouseHandler
from client.pantalla import Pantalla
from client.teclado import TecladoHandler

DESIRED_FPS = 30.0  # 30 frames per second


class Juego(object):

    def __init__(self, host, equipo):
        self.on = True
        self.principal = None
        # handlers
        self.balas = HandlerBalas(self)
        self.hcriat = HandlerCreatures()
        self.load_io_handlers()
        self.conexion = Conexion(host, self, self.hcriat, equipo)
        # loop principal
        tick = LoopingCall(self.update)
        tick.start(1.0 / DESIRED_FPS)
        reactor.run()

    def load_io_handlers(self):
        self.pantalla = Pantalla(self)
        self.teclado = TecladoHandler(self)
        self.mouse = MouseHandler(self)

    def update(self):
        self.pantalla.update()
        self.mouse.update()
        if not self.teclado.update():
            self.quit()

    def comenzar(self):
        self.pantalla.activar()
        self.teclado.activar()
        self.mouse.activar()

    def add_bullet(self, bala):
        self.balas.add_bullet(bala)

    def set_principal(self, jugador):
        self.principal = jugador
        self.hcriat.my_team = jugador.equipo
        self.pantalla.set_principal(jugador)

    def get_players(self):
        return self.hcriat.get_players()

    def get_bullets(self):
        return self.balas.get_balas()

    def get_score(self):
        return self.hcriat.azul, self.hcriat.rojo

    def create_map(self, sequence):
        mapa = Mapa(sequence)
        self.pantalla.dibujar.set_map(mapa)
        return mapa

    def quit(self):
        self.on = False
        pygame.quit()
        reactor.stop()


if __name__ == '__main__':
    team = input('1 - blue ; 2 - red\n')
    ip = raw_input('IP: (default is 127.0.0.1)\n') or '127.0.0.1'
    tutum = 'pixel-war-42e151b5.franr.svc.tutum.io'
    digitalocean = '107.170.76.156'
    Juego(ip, team)
