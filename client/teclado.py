import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_F1, K_ESCAPE


class TecladoHandler(object):

    def __init__(self, juego):
        self.juego = juego
        self.enabled = False

    def activar(self):
        self.enabled = True

    def update(self):
        tecla = pygame.key.get_pressed()
        if tecla[K_ESCAPE]:
            return False
        if self.enabled:
            if tecla[K_UP]:
                self.juego.conexion.cf.protocol.move('n')
            elif tecla[K_DOWN]:
                self.juego.conexion.cf.protocol.move('s')
            elif tecla[K_LEFT]:
                self.juego.conexion.cf.protocol.move('o')
            elif tecla[K_RIGHT]:
                self.juego.conexion.cf.protocol.move('e')
            elif tecla[K_F1]:
                self.juego.conexion.cf.protocol.restart_round()
        return True
