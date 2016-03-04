from twisted.internet import reactor

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


class HandlerBalas(object):

    """ Clase que almacena las balas que dibuja el cliente """

    def __init__(self, juego):
        self.juego = juego
        self.balas = []
        self.clean_loop()

    def get_balas(self):
        return self.balas

    def add_bullet(self, bala):
        self.balas.append(bala)

    def clean_loop(self):
        [self.balas.remove(b) for b in self.balas if not b.alive]
        if self.juego.on:
            reactor.callLater(0.1, self.clean_loop)


class Bala(Positionable):

    def __init__(self, uid, x, y, direction, equipo, juego):
        Positionable.__init__(self, x, y)
        self.uid = uid
        self.dir = direction
        self.equipo = equipo
        self.juego = juego
        self.alive = True
        self.mapa = juego.conexion.cf.protocol.mapa  # horrible
        self.delay = 0.05
        # go for it!
        self.loop()

    def loop(self):
        mx, my = self.calc_desplazamiento()
        self.x += mx
        self.y += my
        self.collision()
        if self.juego.on and not self.collision():
            reactor.callLater(self.delay, self.loop)
        else:
            self.alive = False

    def calc_desplazamiento(self):
        return numeric_dir[self.dir]

    def next_pos(self):
        mx, my = self.calc_desplazamiento()
        return (self.x + mx, self.y + my), (mx, my)

    def collision(self):
        """Each bullet check its collisions with the creatures that are alive and belong to the
        enemy team
        """
        self.update(self.x, self.y)
        if not self.mapa.is_blocking_position(self.x, self.y):
            return False

        c = self.mapa.get_creature(self.x, self.y)
        if c and c.es_equipo(self.equipo):
            # hitting an ally
            return False

        # hitting a wall or enemy
        return True
