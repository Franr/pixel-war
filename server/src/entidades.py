from bloqueos import BloqueoMov, BloqueoDisp


class Objeto(object):
    """ Clase base para todos los objetos (visibles) del juego """

    def __init__(self, uid, x, y):
        self.x = x
        self.y = y
        self.uid = uid

    def get_coor(self):
        return self.x, self.y

    def setCoor(self, x, y):
        self.x = x
        self.y = y

    def is_uid(self, uid):
        return self.uid == uid

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
        
    def mover(self, x, y):
        self.setCoor(x, y)
        
    def is_live(self):
        return self.vivo

    def get_team(self):
        return self.equipo

    def esEquipo(self, equipo):
        return self.equipo == equipo

    def hit(self, danio):
        self.vida -= danio
        if self.vida <= 0:
            self.morir()
            return True
        return False
            
    def morir(self):
        if self.vivo:
            self.vivo = False
            self.die()
            
    def die(self):
        self.hcriat.eliminarCriatura(self.get_uid())


class Jugador(Criatura):
    """ Clase para todos los jugadores del juego """
    
    def __init__(self, uid, x, y, vida, vida_max, equipo, hcriat):
        Criatura.__init__(self, uid, x, y, vida, vida_max, hcriat)
        self.equipo = equipo
        self.bloqM = BloqueoMov()
        self.bloqD = BloqueoDisp()
        # un jugador esta listo una vez asignados todos sus datos
        self.listo = False

    def set_ready(self):
        self.listo = True

    def get_data(self):
        # devuelve los datos necesarios para el paquete de creacion de jugador
        return [self.get_uid(), self.equipo, self.x, self.y, self.vida, self.vida_max]
    
    def mover(self, x, y):
        Criatura.mover(self, x, y)
        self.block_movement()
    
    def block_movement(self):
        self.bloqM = BloqueoMov()
    
    def block_shot(self):
        self.bloqD = BloqueoDisp()

    def cant_move(self):
        return self.bloqM.bloq

    def cant_shot(self):
        return self.bloqD.bloq

    def die(self):
        self.hcriat.del_player(self.get_uid())

    def revivir(self):
        self.vivo = True
        self.vida = self.vida_max


class Bala(Objeto):

    DELAY = 0.05
    DMG = 5

    def __init__(self, uid, x, y, dir, equipo):
        Objeto.__init__(self, uid, x, y)
        self.dir = dir
        self.equipo = equipo
        self.dx = 0
        self.dy = 0
        for d in dir:
            self.calc_desplazamiento(d)
        
    def is_team(self, equipo):
        return self.equipo == equipo
        
    def calc_desplazamiento(self, dir):
        if dir == 'n':
            self.dy = -1
        elif dir == 's':
            self.dy = 1
        elif dir == 'e':
            self.dx = 1
        elif dir == 'o':
            self.dx = -1
        
    def mover(self):    
        self.setCoor(self.x + self.dx, self.y + self.dy)
