import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_F1, K_ESCAPE

from bloqueos import BloqueoMov


class TecladoHandler(object):

    def __init__(self, juego):
        self.juego = juego
        self.enabled = False

    def activar(self):
        self.enabled = True

    def update(self):
        if self.enabled:
            try:
                tecla = pygame.key.get_pressed()
                if tecla[K_UP]:
                    if not BloqueoMov.block:
                        BloqueoMov()
                        self.juego.conexion.cf.protocol.move('n')
                elif tecla[K_DOWN]:
                    if not BloqueoMov.block:
                        BloqueoMov()
                        self.juego.conexion.cf.protocol.move('s')
                elif tecla[K_LEFT]:
                    if not BloqueoMov.block:
                        BloqueoMov()
                        self.juego.conexion.cf.protocol.move('o')
                elif tecla[K_RIGHT]:
                    if not BloqueoMov.block:
                        BloqueoMov()
                        self.juego.conexion.cf.protocol.move('e')
                elif tecla[K_F1]:
                    self.juego.conexion.protcol.restartRound()
                elif tecla[K_ESCAPE]:
                    return False
            except Exception as exc:
                print 'exception', exc
        return True
