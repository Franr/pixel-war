from blocker import Blocker


class Objeto(object):
    """ Clase base para todos los objetos (visibles) del juego """

    def __init__(self, uid, x, y):
        self.x = x
        self.y = y
        self.uid = uid

    def get_coor(self):
        return self.x, self.y

    def set_coor(self, x, y):
        self.x = x
        self.y = y

    def get_uid(self):
        return self.uid


class Criatura(Objeto):

    """ Clase base para todas las criaturas (tanto para jugadores como monstruos """

    def __init__(self, uid, x, y, vida, vida_max, hcriat):
        Objeto.__init__(self, uid, x, y)
        self.vida = vida
        self.vida_max = vida_max
        self.vivo = True
        self.envenenado = False
        self.hcriat = hcriat
        self.team = 0

    def mover(self, x, y):
        self.set_coor(x, y)

    def is_live(self):
        return self.vivo

    def get_team(self):
        return self.team

    def hit(self, damage):
        self.vida -= damage
        if self.vida <= 0:
            self.vivo = False
            return True
        return False


class Jugador(Criatura):
    """ Clase para todos los jugadores del juego """
    MOVE_DELAY = 0.15
    SHOOT_DELAY = 0.10

    def __init__(self, uid, x, y, vida, vida_max, team, hcriat):
        Criatura.__init__(self, uid, x, y, vida, vida_max, hcriat)
        self.team = team
        self.bloqM = None
        self.bloqD = None

    def get_data(self):
        # devuelve los datos necesarios para el paquete de creacion de jugador
        return [self.get_uid(), self.team, self.x, self.y, self.vida, self.vida_max]

    def mover(self, x, y):
        Criatura.mover(self, x, y)
        self.block_movement()

    def block_movement(self):
        self.bloqM = Blocker(self.MOVE_DELAY)

    def block_shot(self):
        self.bloqD = Blocker(self.SHOOT_DELAY)

    def cant_move(self):
        return self.bloqM and self.bloqM.bloq

    def cant_shot(self):
        return self.bloqD and self.bloqD.bloq

    def revive(self):
        self.vivo = True
        self.vida = self.vida_max


class Bala(Objeto):

    DELAY = 0.05
    DMG = 5

    def __init__(self, uid, x, y, direction, equipo):
        Objeto.__init__(self, uid, x, y)
        self.direction = direction
        self.equipo = equipo
        self.dx = 0
        self.dy = 0
        for d in direction:
            self.calc_desplazamiento(d)

    def is_team(self, equipo):
        return self.equipo == equipo

    def calc_desplazamiento(self, direction):
        if direction == 'n':
            self.dy = -1
        elif direction == 's':
            self.dy = 1
        elif direction == 'e':
            self.dx = 1
        elif direction == 'o':
            self.dx = -1

    def mover(self):
        self.set_coor(self.x + self.dx, self.y + self.dy)
