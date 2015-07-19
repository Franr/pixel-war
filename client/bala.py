from threading import Thread
import time

from criaturas import Objeto


class HandlerBalas(Thread):

    """ Clase que almacena las balas que dibuja el cliente """

    def __init__(self, juego):
        Thread.__init__(self)
        self.juego = juego
        self.balas = []
        self.start()

    def get_balas(self):
        return self.balas

    def add_bullet(self, bala):
        self.balas.append(bala)

    def run(self):
        while self.juego.on:
            for b in self.balas:
                if not b.seguir:
                    self.balas.remove(b)
            time.sleep(.1)


class Bala(Thread, Objeto):

    def __init__(self, uid, x, y, direction, equipo, juego):
        Thread.__init__(self)
        Objeto.__init__(self, x, y)
        self.uid = uid
        self.dir = direction
        self.equipo = equipo
        self.juego = juego
        self.seguir = True
        self.mapa = juego.pantalla.dibujar.mapa
        self.delay = 0.05
        # go for it!
        self.start()

    def run(self):
        mx, my = self.calc_desplazamiento()
        while self.seguir and self.juego.on:
            self.x += mx
            self.y += my
            time.sleep(self.delay)
            self.bala_update()
        del self

    def calc_desplazamiento(self):
        movx = 0
        movy = 0
        dist = 1
        if self.dir == 'e':
            movx = dist
        elif self.dir == 'se':
            movx = dist
            movy = dist
        elif self.dir == 's':
            movy = dist
        elif self.dir == 'so':
            movx = -dist
            movy = dist
        elif self.dir == 'o':
            movx = -dist
        elif self.dir == 'no':
            movx = -dist
            movy = -dist
        elif self.dir == 'n':
            movy = -dist
        elif self.dir == 'ne':
            movx = dist
            movy = -dist
        return movx, movy

    def bala_update(self):
        # cada bala revisa sus colisiones contra las criaturas que:
        #   estan vivas
        #   pertenecen al equipo contrario al de la bala
        self.update(self.x, self.y)
        # rects de los sprites
        # verificamos colisiones
        if self.mapa.is_blocking_position(self.x, self.y):
            c = self.mapa.get_creature(self.x, self.y)
            if c:
                # choca contra enemigo
                if not c.es_equipo(self.equipo):
                    self.seguir = False
            # choca contra bloque
            else:
                self.seguir = False
