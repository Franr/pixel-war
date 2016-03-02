from threading import Thread
import time

from criaturas import Positionable

numeric_dir = {
    'e': (1, 0),
    'se': (1, 1),
    's': (0, 1),
    'so': (-1, 1),
    'o': (-1, 0),
    'no': (-1, -1),
    'n': (0, -1),
    'ne': (1, -1),
}


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


class Bala(Thread, Positionable):

    def __init__(self, uid, x, y, direction, equipo, juego):
        Thread.__init__(self)
        Positionable.__init__(self, x, y)
        self.uid = uid
        self.dir = direction
        self.equipo = equipo
        self.juego = juego
        self.seguir = True
        self.mapa = juego.conexion.cf.protocol.mapa  # horrible
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
        return numeric_dir[self.dir]

    def next_pos(self):
        mx, my = self.calc_desplazamiento()
        return (self.x + mx, self.y + my), (mx, my)

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
