import math

import pygame

from constantes import P_X, P_Y

C_X = P_X/2
C_Y = P_Y/2


def esta_entre(n, menor, mayor):
    return (n >= menor) and (n < mayor)


def angulo_to_dir(ang):
    if esta_entre(ang, 22.5*0, 22.5*1):
        return 's'
    elif esta_entre(ang, 22.5*1, 22.5*3):
        return 'se'
    elif esta_entre(ang, 22.5*3, 22.5*5):
        return 'e'
    elif esta_entre(ang, 22.5*5, 22.5*7):
        return 'ne'
    elif esta_entre(ang, 22.5*7, 22.5*9):
        return 'n'
    elif esta_entre(ang, 22.5*9, 22.5*11):
        return 'no'
    elif esta_entre(ang, 22.5*11, 22.5*13):
        return 'o'
    elif esta_entre(ang, 22.5*13, 22.5*15):
        return 'so'
    elif esta_entre(ang, 22.5*15, 22.5*16):
        return 's'
    else:
        print "error"


class Mouse(object):

    def __init__(self):
        self.mouse = pygame.mouse

    def get_angle(self):
        """Return the angle between the mouse position and the center of the screen."""
        mx, my = self.mouse.get_pos()
        angle = math.degrees(math.atan2((mx - C_X), (my - C_Y)))
        if angle < 0:
            angle += 360
        return int(angle)


class MouseHandler(object):

    def __init__(self, juego):
        self.juego = juego
        self.enabled = False
        self.mouse = Mouse()

    def activar(self):
        self.enabled = True

    def update(self):
        clicks = pygame.mouse.get_pressed()
        if not clicks[0]:
            return

        direction = angulo_to_dir(self.mouse.get_angle())
        if self.enabled:
            self.juego.conexion.cf.protocol.fire(direction)
