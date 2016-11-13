#!/usr/bin/env python

import pygame
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from client.map_render import MapRender
from client.mouse import MouseHandler
from client.pantalla import Pantalla
from client.teclado import KeyboardHandler
from generic_client import GenericClient


class WindowClient(GenericClient):

    DESIRED_FPS = 30.0  # 30 frames per second

    def run_loop(self):
        self.loop = LoopingCall(self.update)
        self.loop.start(1.0 / self.DESIRED_FPS)
        if self.STANDALONE:
            reactor.run()

    def load_io_handlers(self):
        self.pantalla = Pantalla(self)
        self.teclado = KeyboardHandler(self)
        self.mouse = MouseHandler(self)

    def update(self):
        self.pantalla.update()
        self.mouse.update()
        if not self.teclado.update():
            self.close_window()

    def activate_io_handlers(self):
        self.pantalla.activar()
        self.teclado.activar()
        self.mouse.activar()

    def create_map(self, sequence):
        mapa = MapRender(sequence)
        self.pantalla.dibujar.set_map(mapa)
        return mapa

    def set_principal(self, player):
        self.principal = player
        self.hcriat.my_team = player.equipo
        self.pantalla.set_principal(player)

    def close_window(self):
        self.on = False
        pygame.quit()
        reactor.stop()


if __name__ == '__main__':
    team = raw_input('1 - blue ; 2 - red\n') or 1
    ip = raw_input('IP: (default is 127.0.0.1)\n') or '127.0.0.1'
    WindowClient(ip, int(team))
